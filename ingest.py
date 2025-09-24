# ingest.py
import os
import pandas as pd
from sentence_transformers import SentenceTransformer
import weaviate
from config import EXCEL_PATH, EMBEDDING_MODEL, WEAVIATE_CLASS_NAME, WEAVIATE_URL


def parse_excel_to_chunks(excel_path):
    """Read all Excel files in the 'data' folder and split into text chunks."""
    data_dir = os.path.abspath("data")
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Data folder not found: {data_dir}")

    chunks = []
    excel_files = [f for f in os.listdir(data_dir) if f.lower().endswith(('.xlsx', '.xls'))]
    if not excel_files:
        raise FileNotFoundError(f"No Excel files found in {data_dir}")

    for excel_file in excel_files:
        file_path = os.path.join(data_dir, excel_file)
        with pd.ExcelFile(file_path) as xls:
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                for idx, row in df.iterrows():
                    text = " ".join([str(cell) for cell in row if pd.notnull(cell)])
                    if text.strip():
                        chunks.append({
                            "text": text,
                            "sheet": sheet_name,
                            "row": idx,
                            "source_file": excel_file
                        })
    if not chunks:
        raise ValueError("No data found in any Excel file in the data folder.")
    return chunks


def ingest_to_weaviate(chunks):
    """Ingest chunks into Weaviate v4."""
    
    # Connect to Weaviate (HTTP-only, skip gRPC)
    client = weaviate.Client("http://localhost:8080")

    # Create class if it does not exist (Weaviate v3)
    existing_classes = [cls["class"] for cls in client.schema.get()["classes"]]
    if WEAVIATE_CLASS_NAME not in existing_classes:
        class_obj = {
            "class": WEAVIATE_CLASS_NAME,
            "properties": [
                {"name": "text", "dataType": ["text"]},
                {"name": "sheet", "dataType": ["text"]},
                {"name": "row", "dataType": ["int"]}
            ]
        }
        client.schema.create_class(class_obj)

    # Initialize embedding model
    model = SentenceTransformer(EMBEDDING_MODEL)

    # Use legacy batch data insertion (Weaviate v3)
    for chunk in chunks:
        embedding = model.encode([chunk["text"]])[0].tolist()
        client.data_object.create(
            data_object={
                "text": chunk["text"],
                "sheet": chunk["sheet"],
                "row": int(chunk["row"])
            },
            class_name=WEAVIATE_CLASS_NAME,
            vector=embedding
        )
    
    return len(chunks)


def main():
    chunks = parse_excel_to_chunks(None)
    count = ingest_to_weaviate(chunks)
    print(f"✅ Ingested {count} chunks from all Excel files in 'data' into Weaviate.")


if __name__ == "__main__":
    main()
