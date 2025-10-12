import weaviate

client = weaviate.Client("http://localhost:8080")
schema = client.schema.get()
for cls in schema["classes"]:
    name = cls["class"]
    print(f"Deleting class: {name}")
    client.schema.delete_class(name)
print("✅ All classes deleted.")

# /var/lib/weaviate-data/coconut