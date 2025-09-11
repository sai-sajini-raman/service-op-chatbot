# query_chromadb.py
import chromadb
from sentence_transformers import SentenceTransformer
from config import CHROMA_DB_PATH, CHROMA_COLLECTION_NAME, EMBEDDING_MODEL

QUERY = "dispatcher"
TOP_K = 3

client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = client.get_collection(CHROMA_COLLECTION_NAME)

model = SentenceTransformer(EMBEDDING_MODEL)
query_emb = model.encode([QUERY])[0]
results = collection.query(query_embeddings=[query_emb], n_results=TOP_K)

print("#--------- ChromaDB Query Results ---------")
for i, (doc, meta, id_, dist) in enumerate(zip(results['documents'], results['metadatas'], results['ids'], results['distances'])):
    print(f"Result {i}:")
    print(f"Text: {doc}")
    print(f"Metadata: {meta}")
    print(f"ID: {id_}")
    print(f"Distance: {dist}")
    print("-" * 40)
print("#--------- END DEBUG ---------")
