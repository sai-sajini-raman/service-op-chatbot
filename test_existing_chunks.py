import weaviate
from config import (
    WEAVIATE_HOST,
    WEAVIATE_PORT,
    CHUNK_CLASS_PREFIX,
    get_current_class_name
)

def test_existing_chunks():
    print(f"Connecting to Weaviate at {WEAVIATE_HOST}:{WEAVIATE_PORT}")
    print("=" * 80)
    
    # Connect to Weaviate
    client = weaviate.Client(url=f"http://{WEAVIATE_HOST}:{WEAVIATE_PORT}")
    
    class_name = get_current_class_name()
    # Check if class exists
    existing_classes = [schema['class'] for schema in client.schema.get()['classes']]
    
    if class_name not in existing_classes:
        print(f"Class '{class_name}' does not exist in Weaviate.")
        print("Available classes:", existing_classes)
        return
    
    print(f"Found class: {class_name}")
    print("=" * 80)
    
    # Get class schema
    schema = client.schema.get(class_name)
    print(f"Class schema:")
    print(f"- Class name: {schema['class']}")
    properties_to_get = [
        "text",  # MOST IMPORTANT - this was missing!
        "ref_doc_id",
        "node_info",
        "relationships",
        "incident_reference",
        "filename_incident",
        "has_filename_incident",
        "page_count",
        "source",
        "document_type",
        "file_path",
        "extraction_method",
        "sheet_name"
    ]
    valid_properties = [prop['name'] for prop in schema['properties'] if prop['name'] in properties_to_get]
    print(f"- Properties: {valid_properties}")
    print("=" * 80)
    
    # Query all objects in the class
    try:
        # Use the valid properties we defined earlier
        result = (
            client.query
            .get(class_name, valid_properties)
            .with_additional(["id"])
            .with_limit(1000)  # Adjust limit as needed
            .do()
        )
        
        if 'data' in result and 'Get' in result['data'] and class_name in result['data']['Get']:
            objects = result['data']['Get'][class_name]
            print(f"Total chunks found: {len(objects)}")
            print("=" * 80)
            
            # Print details of each chunk (all metadata fields except text)
            for i, obj in enumerate(objects, 1):
                print(f"\n--- Chunk {i} ---")
                for key, value in obj.items():
                    if key != "text":
                        print(f"{key}: {value}")
                
                # Check if text exists and print first 100 characters
                if "text" in obj and obj["text"]:
                    text_preview = obj["text"][:100] + "..." if len(obj["text"]) > 100 else obj["text"]
                    print(f"text_preview: {text_preview}")
                else:
                    print("text: [MISSING OR EMPTY]")
                print("-" * 50)
            
            # Summary by ref_doc_id or filename
            doc_counts = {}
            for obj in objects:
                doc_id = obj.get('ref_doc_id') or obj.get('file_path') or obj.get('filename_incident') or 'Unknown'
                doc_counts[doc_id] = doc_counts.get(doc_id, 0) + 1
            
            print(f"\nSummary by document:")
            for doc_id, count in doc_counts.items():
                print(f"  {doc_id}: {count} chunks")
                
        else:
            print("No objects found in the class.")
            print("Query result:", result)
            
    except Exception as e:
        print(f"Error querying Weaviate: {e}")
        
        # Try alternative query without specific properties
        try:
            print("\nTrying alternative query...")
            result = (
                client.query
                .get(class_name)
                .with_additional(["id"])
                .with_limit(10)
                .do()
            )
            print("Alternative query result:", result)
        except Exception as e2:
            print(f"Alternative query also failed: {e2}")
    
    finally:
        pass
        # client.close()

if __name__ == "__main__":
    test_existing_chunks()