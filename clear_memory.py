import weaviate
from config import WEAVIATE_EXCEL_CLASS_NAME

client = weaviate.Client("http://localhost:8080")

# Delete all objects in the memory class (Context_v2)
def clear_WEAVIATE_EXCEL_CLASS_NAME():
    print(f"Deleting all objects in class: {WEAVIATE_EXCEL_CLASS_NAME}")
    while True:
        result = client.query.get(WEAVIATE_EXCEL_CLASS_NAME, ["_additional { id }"]).with_limit(1000).do()
        objects = result.get("data", {}).get("Get", {}).get(WEAVIATE_EXCEL_CLASS_NAME, [])
        if not objects:
            break
        for obj in objects:
            obj_id = obj["_additional"]["id"]
            client.data_object.delete(uuid=obj_id, class_name=WEAVIATE_EXCEL_CLASS_NAME)
            print(f"Deleted object {obj_id}")
    print(f"All objects in {WEAVIATE_EXCEL_CLASS_NAME} have been deleted.")

if __name__ == "__main__":
    clear_WEAVIATE_EXCEL_CLASS_NAME()
