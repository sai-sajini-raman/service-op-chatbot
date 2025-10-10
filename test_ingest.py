
import weaviate
from config import WEAVIATE_EXCEL_CLASS_NAME

def print_one_chunk_metadata():
    client = weaviate.Client("http://localhost:8080")
    # Query for one chunk
    result = client.query.get(
        WEAVIATE_EXCEL_CLASS_NAME,
        [
            "incident_date",
            "incident_number",
            "incident_category",
            "problem_record",
            "portfolio",
            "application",
            "sheet",
            "source_file",
            "row",
            "text"
        ]
    ).with_limit(1).do()
    chunk = result.get("data", {}).get("Get", {}).get(WEAVIATE_EXCEL_CLASS_NAME, [])
    if chunk:
        print("Metadata for one chunk:")
        for k, v in chunk[0].items():
            print(f"{k}: {v}")
    else:
        print("No chunks found in Weaviate.")

if __name__ == "__main__":
    print_one_chunk_metadata()