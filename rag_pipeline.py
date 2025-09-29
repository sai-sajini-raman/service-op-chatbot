# rag_pipeline.py
import os
import time
from sentence_transformers import SentenceTransformer
import weaviate
from config import WEAVIATE_URL, WEAVIATE_EXCEL_CLASS_NAME,WEAVIATE_DOCUMENT_CLASS_NAME, EMBEDDING_MODEL, TOP_K, SYSTEM_PROMPT, DEFAULT_MODEL, FALLBACK_MODEL, MEMORY_CLASS

context_class = MEMORY_CLASS
def store_context(content, role, conversation_id, user_id):
    """
    Store a conversation entry in Context_v1 with timestamp.
    Assumes Context_v1 schema already exists.
    """
    client = weaviate.Client("http://localhost:8080")
    context_data = {
        "content": content,
        "role": role,
        "conversationId": conversation_id,
        "userId": user_id,
        "timestamp": int(time.time()),
    }
    try:
        client.data_object.create(data_object=context_data, class_name=context_class)
        print(f"Stored {role} message in {context_class} successfully")
    except Exception as e:
        print(f"Error storing message in {context_class}: {str(e)}")

def get_context_history(conversation_id):
    """
    Retrieve all context history for a given conversation_id from Context_v1.
    Returns messages sorted by timestamp ascending.
    """
    client = weaviate.Client("http://localhost:8080")
    try:
        result = (
            client.query
            .get(context_class, ["content", "role", "conversationId", "userId", "timestamp"])
            .with_where({
                "path": ["conversationId"],
                "operator": "Equal",
                "valueString": conversation_id
            })
            .with_limit(100)
            .do()
        )
        messages = result.get("data", {}).get("Get", {}).get(context_class, [])
        return sorted(messages, key=lambda x: x["timestamp"])
    except Exception as e:
        print(f"Error retrieving context history: {str(e)}")
        return []


def retrieve_chunks(query, top_k=TOP_K):
    # Connect to Weaviate HTTP-only (v4)
    client = weaviate.Client("http://localhost:8080")
    model = SentenceTransformer(EMBEDDING_MODEL)
    query_emb = model.encode([query])[0].tolist()
    # Query both classes separately and combine results
    excel_results = (
        client.query
        .get(WEAVIATE_EXCEL_CLASS_NAME, ["text", "sheet", "row"])
        .with_near_vector({"vector": query_emb})
        .with_limit(top_k)
        .with_additional(["distance"])
        .do()
    )
    
    doc_results = (
        client.query
        .get(WEAVIATE_DOCUMENT_CLASS_NAME, ["text", "sheet", "row"])
        .with_near_vector({"vector": query_emb})
        .with_limit(top_k)
        .with_additional(["distance"])
        .do()
    )
    # Collect hits from both classes
    chunks = []
    excel_hits = excel_results.get("data", {}).get("Get", {}).get(WEAVIATE_EXCEL_CLASS_NAME, [])
    doc_hits = doc_results.get("data", {}).get("Get", {}).get(WEAVIATE_DOCUMENT_CLASS_NAME, [])
    all_hits = excel_hits + doc_hits
    
    for hit in all_hits:
        chunks.append({
            "text": hit.get("text"),
            "sheet": hit.get("sheet"),
            "row": hit.get("row"),
            "distance": hit.get("_additional", {}).get("distance")
        })
    return chunks


def build_prompt(context_chunks, user_query,conversation_history):
    # Format conversation history
    history_txt = ""
    for msg in conversation_history:
        history_txt += f"{msg['role'].capitalize()}: {msg['content']}\n"
    context = "\n".join([f"[{c['sheet']}:{c['row']}] {c['text']}" for c in context_chunks])
    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Conversation History:\n{history_txt}\n"
        f"Context:\n{context}\n\n"
        f"User Query: {user_query}"
    )
    return prompt

def call_llm(prompt, model=DEFAULT_MODEL):
    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import SystemMessage, UserMessage
    from azure.core.credentials import AzureKeyCredential

    endpoint = "https://models.github.ai/inference"
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("Missing GITHUB_TOKEN environment variable.")

    model_name = "openai/gpt-4o" if model == DEFAULT_MODEL else "openai/gpt-4.1"

    client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(token))
    response = client.complete(
        messages=[SystemMessage(SYSTEM_PROMPT), UserMessage(prompt)],
        temperature=1.0,
        top_p=1.0,
        max_tokens=1000,
        model=model_name
    )
    return response.choices[0].message.content

def answer_query(user_query,conversation_id,user_id):
    start = time.time()
    history = get_context_history(conversation_id)
    store_context(user_query, "user", conversation_id, user_id)

    retrieved_chunks = retrieve_chunks(user_query)
    # Filter out poor matches (distance >= 0.60)
    filtered_chunks = [c for c in retrieved_chunks if c.get('distance') is not None and c.get('distance') < 0.60]
    # Sort chunks by similarity score (distance ascending)
    sorted_chunks = sorted(
        filtered_chunks,
        key=lambda c: c.get('distance') if c.get('distance') is not None else float('inf')
    )

    prompt = build_prompt(sorted_chunks, user_query,history)
    answer = call_llm(prompt)
    store_context(answer, "assistant", conversation_id, user_id)
    latency = time.time() - start
    sources = [(c['sheet'], c['row']) for c in sorted_chunks]


    return {
        "answer": answer,
        "sources": sources,
        "chunks": sorted_chunks,
        "latency": latency
    }

