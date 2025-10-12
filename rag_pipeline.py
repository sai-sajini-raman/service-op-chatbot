import os
import time
from llama_index.llms.gemini import Gemini
from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.memory import ChatMemoryBuffer
import weaviate
from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    WEAVIATE_HOST,
    WEAVIATE_PORT,
    CHAT_WINDOW_SIZE,
    HYBRID_SEARCH_K,
    get_current_class_name,
)

# Global variables for initialized components
_client = None
_current_class = None
_llm = None
_index = None
_conversation_histories = {}  # Store conversation history per conversation_id

def hybrid_search(client, class_name, query, rewritten_query, top_k=5):
    """Perform true hybrid search combining keyword (BM25) and semantic similarity"""
    try:
        # Generate embedding for semantic search
        query_embedding = Settings.embed_model.get_query_embedding(rewritten_query)
        
        # Hybrid search using both nearText (keyword) and nearVector (semantic)
        result = (
            client.query
            .get(class_name, ["text", "source", "filename_incident", "document_type", "incident_reference"])
            .with_hybrid(
                query=rewritten_query,  # Keyword search
                vector=query_embedding,  # Semantic search  
                alpha=0.5  # Balance between keyword (0) and semantic (1)
            )
            .with_limit(top_k)
            .do()
        )
        
        if 'data' in result and 'Get' in result['data'] and class_name in result['data']['Get']:
            return result['data']['Get'][class_name]
        else:
            return []
            
    except Exception as e:
        # Fallback to semantic-only search if hybrid fails
        try:
            result = (
                client.query
                .get(class_name, ["text", "source", "filename_incident", "document_type", "incident_reference"])
                .with_near_vector({
                    "vector": query_embedding,
                    "certainty": 0.7
                })
                .with_limit(top_k)
                .do()
            )
            
            if 'data' in result and 'Get' in result['data'] and class_name in result['data']['Get']:
                return result['data']['Get'][class_name]
            else:
                return []
        except:
            return []

def get_llm():
    try:
        # Initialize Gemini with explicit model configuration
        llm = Gemini(
            api_key=GEMINI_API_KEY, 
            model=GEMINI_MODEL,
            max_tokens=1024,
            temperature=0.1
        )
        
        # Patch the metadata issue by adding missing _model_meta attribute
        if not hasattr(llm, '_model_meta'):
            # Create a mock model meta with required attributes
            class MockModelMeta:
                def __init__(self):
                    self.input_token_limit = 30720  # Gemini default
                    self.output_token_limit = 2048
            
            llm._model_meta = MockModelMeta()
        
        # Patch the _model attribute issue
        if not hasattr(llm, '_model'):
            llm._model = GEMINI_MODEL
        
        return llm
    except Exception as e:
        print(f"Error initializing Gemini LLM: {e}")
        raise e

def rewrite_query_with_context(llm, user_query, conversation_history):
    """Rewrite user query considering conversation context for better retrieval"""
    if conversation_history:
        recent_context = "\n".join(conversation_history[-4:])  # Last 2 exchanges
        prompt = f"""Given the conversation history below, rewrite the user's current query to be more specific and better suited for document retrieval. Include relevant context from previous questions if needed.

Conversation history:
{recent_context}

Current user query: {user_query}

Rewritten query (make it more specific and searchable):"""
    else:
        prompt = f"""Rewrite this user query to be more specific and better suited for document retrieval in an IT incident knowledge base: {user_query}

Rewritten query:"""
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return user_query  # Fallback to original query

def initialize_rag_components():
    """Initialize all RAG components once - called at module import"""
    global _client, _current_class, _llm, _index
    
    if _client is not None:  # Already initialized
        return True
    
    try:
        # Set global embedding model (same as ingestion)
        from llama_index.core.embeddings import BaseEmbedding
        from sentence_transformers import SentenceTransformer
        from typing import List, Any
        
        class LocalSentenceTransformerEmbedding(BaseEmbedding):
            """Local embedding using SentenceTransformer - same as ingestion"""
            _model: Any = None
            
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                object.__setattr__(self, '_model', SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2"))
                
            def _get_query_embedding(self, query: str) -> List[float]:
                return self._model.encode(query).tolist()
                
            def _get_text_embedding(self, text: str) -> List[float]:
                return self._model.encode(text).tolist()
                
            def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
                return [self._model.encode(text).tolist() for text in texts]
                
            async def _aget_query_embedding(self, query: str) -> List[float]:
                return self._get_query_embedding(query)
                
            async def _aget_text_embedding(self, text: str) -> List[float]:
                return self._get_text_embedding(text)
                
            async def _aget_text_embeddings(self, texts: List[str]) -> List[List[float]]:
                return self._get_text_embeddings(texts)
        
        Settings.embed_model = LocalSentenceTransformerEmbedding()
        
        # Initialize LLM with error handling and metadata fix
        _llm = get_llm()
        Settings.llm = _llm
        
        # Get current class name automatically
        _current_class = get_current_class_name()
        if not _current_class:
            print("Error: No valid class found. Please run ingestion first.")
            return False
        
        # Load Weaviate vector store and index (v3 client)
        _client = weaviate.Client(
            url=f"http://{WEAVIATE_HOST}:{WEAVIATE_PORT}"
        )
        vector_store = WeaviateVectorStore(
            weaviate_client=_client, 
            index_name=_current_class,
            text_key="text",
            retrieval_mode="text"  # Ensure text field is retrieved
        )
        # Patch for compatibility: add _client attribute if missing
        if not hasattr(vector_store, '_client'):
            vector_store._client = _client
        
        # Create index from existing vector store instead of loading from storage
        from llama_index.core import VectorStoreIndex
        try:
            _index = VectorStoreIndex.from_vector_store(
                vector_store, 
                embed_model=Settings.embed_model,
                show_progress=False  # Disable progress for UI
            )
        except Exception as e:
            # Alternative: create index directly with vector store
            _index = VectorStoreIndex([], vector_store=vector_store, embed_model=Settings.embed_model)
        
        return True
        
    except Exception as e:
        print(f"Error initializing RAG components: {e}")
        return False

def answer_query(query, conversation_id, user_id):
    """
    Main function to process a query and return the response
    
    Args:
        query (str): User's question
        conversation_id (str): Unique conversation identifier
        user_id (str): User identifier
        
    Returns:
        dict: Contains 'answer', 'chunks', 'latency', 'sources'
    """
    start_time = time.time()
    
    # Initialize components if not already done
    if not initialize_rag_components():
        return {
            "answer": "Sorry, I'm having trouble initializing. Please try again later.",
            "chunks": [],
            "latency": 0.0,
            "sources": []
        }
    
    # Get or create conversation history for this conversation_id
    if conversation_id not in _conversation_histories:
        _conversation_histories[conversation_id] = []
    
    conversation_history = _conversation_histories[conversation_id]
    
    try:
        # Step 1: Rewrite query with conversation context
        rewritten_query = rewrite_query_with_context(_llm, query, conversation_history)
        
        # Step 2: Perform hybrid search (keyword + semantic)
        chunks = hybrid_search(_client, _current_class, query, rewritten_query, HYBRID_SEARCH_K)
        
        # Step 3: Process retrieved chunks
        if chunks:
            # Combine all chunk texts for the LLM
            combined_text = ""
            sources = []
            
            for chunk in chunks:
                text = chunk.get('text', '')
                source = chunk.get('source', 'Unknown source')
                
                if text:
                    combined_text += f"\n--- From {source} ---\n{text}\n"
                    if source not in sources:
                        sources.append(source)
            
            if combined_text.strip():
                # Step 4: Generate response with context + memory
                recent_context = "\n".join(conversation_history[-4:]) if conversation_history else "No previous conversation."
                
                prompt = f"""You are an IT incident support assistant. Answer the user's question using the retrieved documents and conversation context.

Previous conversation context:
{recent_context}

Current user question: {query}

Retrieved relevant documents:
{combined_text}

Please provide a clear, helpful response that:
1. Directly answers the user's question
2. References specific incident numbers if relevant
3. Considers the conversation context
4. Provides actionable information when possible"""

                try:
                    import google.generativeai as genai
                    genai.configure(api_key=GEMINI_API_KEY)
                    model = genai.GenerativeModel('gemini-2.0-flash-exp')
                    
                    response = model.generate_content(prompt)
                    bot_response = response.text
                    
                    # Extract just the filenames from full paths for sources
                    source_filenames = []
                    for source in sources:
                        if '\\' in source or '/' in source:
                            filename = source.split('\\')[-1].split('/')[-1]
                        else:
                            filename = source
                        source_filenames.append(filename)
                    
                    # Step 5: Update conversation history (LlamaIndex memory style)
                    conversation_history.append(f"User: {query}")
                    conversation_history.append(f"Bot: {bot_response}")
                    
                    # Keep only recent conversation (memory window)
                    if len(conversation_history) > CHAT_WINDOW_SIZE * 2:
                        conversation_history = conversation_history[-(CHAT_WINDOW_SIZE * 2):]
                    
                    # Update global conversation history
                    _conversation_histories[conversation_id] = conversation_history
                    
                    latency = time.time() - start_time
                    
                    return {
                        "answer": bot_response,
                        "chunks": chunks,
                        "latency": latency,
                        "sources": source_filenames
                    }
                    
                except Exception as direct_llm_error:
                    latency = time.time() - start_time
                    return {
                        "answer": f"Found {len(chunks)} relevant documents but cannot process them due to an error.",
                        "chunks": chunks,
                        "latency": latency,
                        "sources": sources
                    }
            else:
                latency = time.time() - start_time
                return {
                    "answer": "Found relevant documents but no readable text content.",
                    "chunks": chunks,
                    "latency": latency,
                    "sources": []
                }
        else:
            latency = time.time() - start_time
            return {
                "answer": "I couldn't find relevant information in the knowledge base for your query. Please try rephrasing your question or provide more specific details.",
                "chunks": [],
                "latency": latency,
                "sources": []
            }
            
    except Exception as e:
        latency = time.time() - start_time
        return {
            "answer": "Sorry, I encountered an error processing your question.",
            "chunks": [],
            "latency": latency,
            "sources": []
        }

def main():
    """CLI version for direct testing"""
    print("RAG Chatbot with Memory & Hybrid Search (type 'exit' to quit)\n")
    
    # Initialize components
    if not initialize_rag_components():
        print("Failed to initialize RAG components. Exiting.")
        return
    
    print("RAG components initialized successfully!")
    
    conversation_id = "cli_session"
    user_id = "cli_user"
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        
        print(f"Querying with: {user_input}")
        
        # Use the answer_query function
        result = answer_query(user_input, conversation_id, user_id)
        
        print(f"Bot: {result['answer']}")
        
        if result['sources']:
            print(f"Sources: {', '.join(result['sources'])}")
        
        print(f"⏱️ Response time: {result['latency']:.2f} seconds\n")

if __name__ == "__main__":
    main()