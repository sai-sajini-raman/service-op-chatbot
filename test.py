import weaviate
from config import WEAVIATE_EXCEL_CLASS_NAME, WEAVIATE_DOCUMENT_CLASS_NAME
import uuid
from rag_pipeline import answer_query

client = weaviate.Client("http://localhost:8080")

print("--- SCHEMA --- (class names and vectorizer only) ---")
schema = client.schema.get()
for class_def in schema.get('classes', []):
    print(f"Class: {class_def.get('class')}, Vectorizer: {class_def.get('vectorizer')}")

def main():
    conversation_id = str(uuid.uuid4())
    user_id = f"user_{str(uuid.uuid4())[:8]}"

    print("\n=== Interactive Test for RAG Chatbot ===")
    print("Type 'q' to quit.\n")

    while True:
        user_query = input("You: ")
        if user_query.strip().lower() == 'q':
            print("Exiting chat.")
            break
        result = answer_query(user_query, conversation_id, user_id)
        chunks = result.get('chunks', [])
        print(f"\n[INFO] Number of chunks sent to LLM: {len(chunks)}")
        print("[INFO] Top K chunks sent to LLM:")
        for i, chunk in enumerate(chunks):
            print(f"  {i+1}. Sheet: {chunk.get('sheet')}, Row: {chunk.get('row')}, Distance: {chunk.get('distance'):.4f}\n     Text: {str(chunk.get('text'))[:200]}{'...' if len(str(chunk.get('text'))) > 200 else ''}")
        print("\n--- BOT OUTPUT ---")
        print(result["answer"])
        print("\n--- SOURCES ---")
        for chunk in chunks:
            print(f"Sheet: {chunk.get('sheet')}, Row: {chunk.get('row')}, Distance: {chunk.get('distance'):.4f}")
        print("\n--- LATENCY ---")
        print(f"{result['latency']:.2f} seconds\n")

if __name__ == "__main__":
    main()