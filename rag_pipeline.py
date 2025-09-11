# rag_pipeline.py

import chromadb
from sentence_transformers import SentenceTransformer
from config import CHROMA_DB_PATH, CHROMA_COLLECTION_NAME, EMBEDDING_MODEL, TOP_K, SYSTEM_PROMPT, DEFAULT_MODEL, FALLBACK_MODEL
import os

def get_chromadb_collection():
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    return client.get_collection(CHROMA_COLLECTION_NAME)

def retrieve_chunks(query, top_k=TOP_K):
    model = SentenceTransformer(EMBEDDING_MODEL)
    query_emb = model.encode([query])[0]
    collection = get_chromadb_collection()
    results = collection.query(query_embeddings=[query_emb], n_results=top_k)
    # Flatten nested lists (one inner list per query)
    docs = results['documents'][0] if results['documents'] and isinstance(results['documents'][0], list) else results['documents']
    metas = results['metadatas'][0] if results['metadatas'] and isinstance(results['metadatas'][0], list) else results['metadatas']
    ids = results['ids'][0] if results['ids'] and isinstance(results['ids'][0], list) else results['ids']
    dists = results['distances'][0] if results['distances'] and isinstance(results['distances'][0], list) else results['distances']
    chunks = []
    for doc, meta, id_, dist in zip(docs, metas, ids, dists):
        chunks.append({
            "text": doc,
            "sheet": meta.get("sheet"),
            "row": meta.get("row"),
            "id": id_,
            "distance": dist
        })
    return chunks

def build_prompt(context_chunks, user_query):
    context = "\n".join([f"[{c['sheet']}:{c['row']}] {c['text']}" for c in context_chunks])
    prompt = f"{SYSTEM_PROMPT}\n\nContext:\n{context}\n\nUser Query: {user_query}"
    return prompt

def call_llm(prompt, model=DEFAULT_MODEL):
    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import SystemMessage, UserMessage
    from azure.core.credentials import AzureKeyCredential
    endpoint = "https://models.github.ai/inference"
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("Missing GITHUB_TOKEN environment variable.")
    if model == DEFAULT_MODEL:
        model_name = "openai/gpt-4o"
    else:
        model_name = "openai/gpt-4.1"
    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(token),
    )
    response = client.complete(
        messages=[
            SystemMessage(SYSTEM_PROMPT),
            UserMessage(prompt),
        ],
        temperature=1.0,
        top_p=1.0,
        max_tokens=1000,
        model=model_name
    )
    return response.choices[0].message.content

def answer_query(user_query):
    import time
    start = time.time()
    retrieved_chunks = retrieve_chunks(user_query)
    # Sort chunks by similarity score (distance, ascending)
    sorted_chunks = sorted(retrieved_chunks, key=lambda c: c.get('distance', float('inf')))
    prompt = build_prompt(sorted_chunks, user_query)
    answer = call_llm(prompt)
    latency = time.time() - start
    sources = [(c['sheet'], c['row']) for c in sorted_chunks]
    return {
        "answer": answer,
        "sources": sources,
        "chunks": sorted_chunks,
        "latency": latency
    }


