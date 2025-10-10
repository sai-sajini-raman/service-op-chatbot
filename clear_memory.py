import weaviate
from config import MEMORY_CLASS

client = weaviate.Client("http://localhost:8080")

# Delete all objects in the memory class (Context_v2)
def clear_MEMORY_CLASS():
    print(f"Deleting all objects in class: {MEMORY_CLASS}")
    while True:
        result = client.query.get(MEMORY_CLASS, ["_additional { id }"]).with_limit(1000).do()
        objects = result.get("data", {}).get("Get", {}).get(MEMORY_CLASS, [])
        if not objects:
            break
        for obj in objects:
            obj_id = obj["_additional"]["id"]
            client.data_object.delete(uuid=obj_id, class_name=MEMORY_CLASS)
            print(f"Deleted object {obj_id}")
    print(f"All objects in {MEMORY_CLASS} have been deleted.")

if __name__ == "__main__":
    clear_MEMORY_CLASS()
