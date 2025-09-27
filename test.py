# Debug Weaviate schema and object vectors.
# Run: python test.py
import weaviate
from config import WEAVIATE_CLASS_NAME

client = weaviate.Client("http://localhost:8080")

print("--- SCHEMA --- (class names and vectorizer only) ---")
schema = client.schema.get()
for class_def in schema.get('classes', []):
    print(f"Class: {class_def.get('class')}, Vectorizer: {class_def.get('vectorizer')}")

print("\n--- SAMPLE OBJECTS WITH VECTORS ---")
results = client.query.get(WEAVIATE_CLASS_NAME, ["sheet", "row"]).with_additional(["vector"]).with_limit(3).do()
objects = results.get("data", {}).get("Get", {}).get(WEAVIATE_CLASS_NAME, [])
for idx, obj in enumerate(objects):
    print(f"Object {idx+1}:")
    print(f"  sheet: {obj.get('sheet')}")
    print(f"  row: {obj.get('row')}")
    vector = obj.get('_additional', {}).get('vector')
    print(f"  vector: {'present' if vector else 'MISSING'}\n")

if not objects:
    print("No objects found in class.")
# test.py
"""
Test what context chunks would be sent to the LLM for a sample query.
This script uses the same retrieval logic as rag_pipeline.py and prints the retrieved context chunks.
"""

from rag_pipeline import answer_query

def main():
    test_query = "There is some delay in FFO order."  
    print(f"Testing query: {test_query}\n")
    result = answer_query(test_query)
    answer = result.get("answer")
    context_chunks = result.get("chunks", [])
    sources = context_chunks
    print("--- Retrieved Context Chunks ---")
    for i, chunk in enumerate(context_chunks):
        print(f"Chunk {i+1}:")
        print(chunk)
        print()
    print("--- LLM Input Preview ---")
    print("\n".join([c.get('text', '') for c in context_chunks]))
    print("\n--- Answer ---\n")
    print(answer)
    print("\n--- Sources ---\n")
    print(sources)

if __name__ == "__main__":
    main()
