# list_chunks.py
"""
List the first 10 chunk texts from the Weaviate class to verify ingestion and chunk formatting.
"""
import weaviate
from config import WEAVIATE_CLASS_NAME

client = weaviate.Client("http://localhost:8080")

print(f"Listing first 10 objects from class: {WEAVIATE_CLASS_NAME}\n")

results = (
    client.query
    .get(WEAVIATE_CLASS_NAME, ["text", "sheet", "row", "source_file"])
    .with_limit(10)
    .do()
)
chunks = results.get("data", {}).get("Get", {}).get(WEAVIATE_CLASS_NAME, [])

for i, chunk in enumerate(chunks):
    print(f"Chunk {i+1}:")
    print(f"Text: {chunk.get('text')}")
    print(f"Sheet: {chunk.get('sheet')}")
    print(f"Row: {chunk.get('row')}")
    print(f"Source File: {chunk.get('source_file', 'N/A')}")
    print("---")

if not chunks:
    print("No objects found in the class. Check ingestion.")
