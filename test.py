import weaviate
import uuid
import json
from rag_pipeline import answer_query, build_filter_prompt, call_llm, get_metadata_uniques

def main():
    conversation_id = str(uuid.uuid4())
    user_id = f"user_{str(uuid.uuid4())[:8]}"

    print("\n=== Interactive Test for RAG Chatbot (with filter debug) ===")
    print("Type 'q' to quit.\n")

    while True:
        user_query = input("You: ")
        if user_query.strip().lower() == 'q':
            print("Exiting chat.")
            break

        # 1. Build filter prompt and get JSON filter from LLM
        metadata_fields = [
            "incident_date", "incident_number", "incident_category", "problem_record",
            "portfolio", "application", "sheet", "source_file"
        ]
        metadata_dict = get_metadata_uniques("ExcelChunks", metadata_fields)  # Use your class name
        prompt_f = build_filter_prompt(user_query, metadata_dict)
        llm_filter_output = call_llm(prompt_f)
        print("\n[INFO] Raw LLM filter output:")
        print(llm_filter_output)

        try:
            filter_json = json.loads(llm_filter_output)
        except Exception as e:
            print(f"[ERROR] Could not parse LLM output as JSON: {e}")
            filter_json = {}

        print("\n[INFO] Parsed JSON filter object:")
        print(json.dumps(filter_json, indent=2))

        # 2. Run answer_query (which uses the filter for retrieval)
        result = answer_query(user_query, conversation_id, user_id)
        chunks = result.get('chunks', [])

        print(f"\n[INFO] Retrieved chunks (metadata only):")
        for i, chunk in enumerate(chunks):
            print(f"  {i+1}. Sheet: {chunk.get('sheet')}, Row: {chunk.get('row')}, Distance: {chunk.get('distance'):.4f}, Portfolio: {chunk.get('portfolio')}, Incident Date: {chunk.get('incident_date')}")

        # 3. Filtered chunks (distance < threshold)
        filtered_chunks = [c for c in chunks if c.get('distance') is not None and c.get('distance') < 0.8]
        print(f"\n[INFO] Filtered chunks (distance < 0.8):")
        for i, chunk in enumerate(filtered_chunks):
            print(f"  {i+1}. Sheet: {chunk.get('sheet')}, Row: {chunk.get('row')}, Distance: {chunk.get('distance'):.4f}, Portfolio: {chunk.get('portfolio')}, Incident Date: {chunk.get('incident_date')}")

        print("\n--- BOT OUTPUT ---")
        print(result["answer"])
        print("\n--- LATENCY ---")
        print(f"{result['latency']:.2f} seconds\n")

if __name__ == "__main__":
    main()