# rag_pipeline.py
import os
import time
from sentence_transformers import SentenceTransformer
import weaviate
from config import WEAVIATE_URL, WEAVIATE_CLASS_NAME, EMBEDDING_MODEL, TOP_K, SYSTEM_PROMPT, DEFAULT_MODEL, FALLBACK_MODEL

def retrieve_chunks(query, top_k=TOP_K):
    # Connect to Weaviate HTTP-only (v4)
    client = weaviate.Client("http://localhost:8080")
    model = SentenceTransformer(EMBEDDING_MODEL)
    query_emb = model.encode([query])[0].tolist()
    # Use legacy HTTP query API to avoid gRPC errors
    results = (
        client.query
        .get(WEAVIATE_CLASS_NAME, ["text", "sheet", "row"])
        .with_near_vector({"vector": query_emb})
        .with_limit(top_k)
        .do()
    )
    # print Debug: Show raw Weaviate results
    print("[DEBUG] Raw Weaviate results:", results)
    hits = results.get("data", {}).get("Get", {}).get(WEAVIATE_CLASS_NAME, [])
    # print Debug: Show hits before chunk processing
    print(f"[DEBUG] Hits before chunk processing: {hits}")
    chunks = []
    for hit in hits:
        chunks.append({
            "text": hit.get("text"),
            "sheet": hit.get("sheet"),
            "row": hit.get("row"),
            "distance": hit.get("_additional", {}).get("distance")
        })
    # print Debug: Show processed chunks
    print(f"[DEBUG] Processed chunks: {chunks}")
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

def answer_query(user_query):
    start = time.time()
    retrieved_chunks = retrieve_chunks(user_query)
    # Sort chunks by similarity score (distance ascending)
    sorted_chunks = sorted(
        retrieved_chunks,
        key=lambda c: c.get('distance') if c.get('distance') is not None else float('inf')
    )
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
