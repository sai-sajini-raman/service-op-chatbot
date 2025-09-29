# Debug Weaviate schema and object vectors.
# Run: python test.py
import weaviate
from config import WEAVIATE_EXCEL_CLASS_NAME, WEAVIATE_DOCUMENT_CLASS_NAME

# client = weaviate.Client("http://localhost:8080")

# print("--- SCHEMA --- (class names and vectorizer only) ---")
# schema = client.schema.get()
# for class_def in schema.get('classes', []):
#     print(f"Class: {class_def.get('class')}, Vectorizer: {class_def.get('vectorizer')}")

# print("\n--- SAMPLE OBJECTS WITH VECTORS ---")
# results = client.query.get(WEAVIATE_CLASS_NAME, ["sheet", "row"]).with_additional(["vector"]).with_limit(3).do()
# objects = results.get("data", {}).get("Get", {}).get(WEAVIATE_CLASS_NAME, [])
# for idx, obj in enumerate(objects):
#     print(f"Object {idx+1}:")
#     print(f"  sheet: {obj.get('sheet')}")
#     print(f"  row: {obj.get('row')}")
#     vector = obj.get('_additional', {}).get('vector')
#     print(f"  vector: {'present' if vector else 'MISSING'}\n")

# if not objects:
#     print("No objects found in class.")
# test.py



from rag_pipeline import answer_query


def main():
    test_query = "There is some delay in FFO order."
    from config import TOP_K
    result = answer_query(test_query)
    chunks = result.get("chunks", [])
    for chunk in chunks[:]:
        print(chunk.get("distance"))



if __name__ == "__main__":
    main()
