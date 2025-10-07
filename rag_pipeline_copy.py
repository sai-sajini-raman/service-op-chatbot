import os
import time
from sentence_transformers import SentenceTransformer
import weaviate
from config import WEAVIATE_URL, WEAVIATE_EXCEL_CLASS_NAME, WEAVIATE_DOCUMENT_CLASS_NAME, EMBEDDING_MODEL, TOP_K, SYSTEM_PROMPT, DEFAULT_MODEL, FALLBACK_MODEL, MEMORY_CLASS

context_class = MEMORY_CLASS

PAIR_LIMIT = 2  # Only keep the most recent 2 user-bot pairs

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
    Returns messages sorted by timestamp ascending, but only the last PAIR_LIMIT pairs.
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
            .with_limit(PAIR_LIMIT * 2)
            .do()
        )
        messages = result.get("data", {}).get("Get", {}).get(context_class, [])
        messages = sorted(messages, key=lambda x: x["timestamp"])
        # Only keep the last PAIR_LIMIT pairs (user/assistant alternation)
        # Each pair is [user, assistant], so take the last PAIR_LIMIT*2 messages
        return messages[-(PAIR_LIMIT * 2):]
    except Exception as e:
        print(f"Error retrieving context history: {str(e)}")
        return []

def trim_context_history_if_needed(conversation_id):
    """
    Truncate old context entries if more than PAIR_LIMIT pairs (4 messages) exist.
    """
    client = weaviate.Client("http://localhost:8080")
    try:
        result = (
            client.query
            .get(context_class, ["content", "role", "conversationId", "userId", "timestamp", "id"])
            .with_where({
                "path": ["conversationId"],
                "operator": "Equal",
                "valueString": conversation_id
            })
            .with_limit(100)
            .do()
        )
        messages = result.get("data", {}).get("Get", {}).get(context_class, [])
        messages = sorted(messages, key=lambda x: x["timestamp"])
        # If more than PAIR_LIMIT*2 messages, delete the oldest ones
        if len(messages) > PAIR_LIMIT * 2:
            to_delete = messages[:len(messages) - PAIR_LIMIT * 2]
            for msg in to_delete:
                try:
                    client.data_object.delete(
                        id=msg["id"], class_name=context_class
                    )
                except Exception as e:
                    print(f"Error deleting old context msg: {str(e)}")
    except Exception as e:
        print(f"Error trimming context history: {str(e)}")


def retrieve_chunks(query, top_k=TOP_K):
    client = weaviate.Client("http://localhost:8080")
    model = SentenceTransformer(EMBEDDING_MODEL)
    query_emb = model.encode([query])[0].tolist()
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

def build_prompt(context_chunks, user_query, conversation_history):
    history_txt = ""
    from datetime import date
    today = date.today()
    previous_query = ""
    for msg in conversation_history:
        history_txt += f"{msg['role'].capitalize()}: {msg['content']}\n"
        if msg['role'] == 'user':
            previous_query += f"{msg['content']} + "
         
    context = "\n".join([f"[{c['sheet']}:{c['row']}] {c['text']}" for c in context_chunks])
    prompt = (
        f"{today}\n"
        f"{SYSTEM_PROMPT}\n\n"
        f"Conversation History:\n{history_txt}\n"
        f"Context:\n{context}\n\n"
        f"User Query: {user_query}"
        # f"User Query: {previous_query} + {user_query}"

    )
    return prompt

def call_llm(prompt):
    import os
    from dotenv import load_dotenv
    from google import genai
    from google.genai import types

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")

    client = genai.Client(api_key=api_key)
    model_name = "gemini-2.5-pro"  # You can make this configurable if needed

    # Gemini expects contents as a list of strings (the prompt)
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt],
            config=types.GenerateContentConfig(
                temperature=0.7,
                top_p=0.9,
                top_k=40,
            ),
        )
        return response.text.strip() if response.text else "No response text returned."
    except Exception as e:
        return f"Error generating response: {str(e)}"

def answer_query(user_query, conversation_id, user_id):
    start = time.time()
   
    store_context(user_query, "user", conversation_id, user_id)
    history = get_context_history(conversation_id)
    # Remove older pairs if needed
    trim_context_history_if_needed(conversation_id)

    retrieved_chunks = retrieve_chunks(user_query)
    filtered_chunks = [c for c in retrieved_chunks if c.get('distance') is not None and c.get('distance') < 0.6]
    sorted_chunks = sorted(
        filtered_chunks,
        key=lambda c: c.get('distance') if c.get('distance') is not None else float('inf')
    )

    prompt = build_prompt(sorted_chunks, user_query, history)
    answer = call_llm(prompt)
    store_context(answer, "assistant", conversation_id, user_id)
    trim_context_history_if_needed(conversation_id)
    latency = time.time() - start
    sources = [(c['sheet'], c['row']) for c in sorted_chunks]

    return {
        "answer": answer,
        "sources": sources,
        "chunks": sorted_chunks,
        "latency": latency
    }