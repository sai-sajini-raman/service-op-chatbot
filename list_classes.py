# list_classes.py
"""
List all classes in Weaviate to confirm existence and schema.
"""
import weaviate

client = weaviate.Client("http://localhost:8080")

schema = client.schema.get()
classes = schema.get("classes", [])

print("Classes in Weaviate:")
for cls in classes:
    print(f"Class: {cls.get('class')}")
    print(f"Properties: {[p['name'] for p in cls.get('properties', [])]}")
    print("---")

if not classes:
    print("No classes found in Weaviate.")
