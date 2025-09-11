# view_embeddings.py
import chromadb
from config import CHROMA_DB_PATH, CHROMA_COLLECTION_NAME

client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = client.get_collection(CHROMA_COLLECTION_NAME)

# Query a sample of documents and their embeddings
results = collection.get(include=[ "documents", "metadatas"], limit=5)

for i, doc in enumerate(results["documents"]):
    print(f"Document {i}: {doc}")
    # print(f"Embedding: {results['embeddings'][i]}")
    print(f"Metadata: {results['metadatas'][i]}")
    print("-" * 40)
