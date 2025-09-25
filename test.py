# test.py
"""
Test what context chunks would be sent to the LLM for a sample query.
This script uses the same retrieval logic as rag_pipeline.py and prints the retrieved context chunks.
"""

from rag_pipeline import answer_query

def main():
    test_query = "17 Foods suppliers served by True Commerce were getting duplicated advance shipping notice"  
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
