import time
import uuid
import weaviate
from config import MEMORY_CLASS

# ---------------- Schema for Context_v1 ----------------
context_class = MEMORY_CLASS
def setup_context_schema(client):
    """Create Context_v1 collection schema if it doesn't exist"""
    try:
        existing_classes = [cls["class"] for cls in client.schema.get()["classes"]]
        
        if context_class not in existing_classes:
            class_obj = {
                "class": context_class,
                "properties": [
                    {"name": "content", "dataType": ["text"]},
                    {"name": "role", "dataType": ["text"]},
                    {"name": "conversationId", "dataType": ["text"]},
                    {"name": "userId", "dataType": ["text"]},
                    {"name": "timestamp", "dataType": ["int"]},
                ]
            }
            client.schema.create_class(class_obj)
            print(f"{context_class} schema created successfully")
        else:
            print(f"{context_class} schema already exists")
    except Exception as e:
        print(f"{context_class} schema creation error: {str(e)}")

def main():
    """Test the schema creation"""
    client = weaviate.Client("http://localhost:8080")
    setup_context_schema(client)

if __name__ == "__main__":
    main()
