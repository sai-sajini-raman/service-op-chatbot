# ingest.py
import os
import pandas as pd
from sentence_transformers import SentenceTransformer
import weaviate
from config import EXCEL_PATH, EMBEDDING_MODEL, WEAVIATE_CLASS_NAME, WEAVIATE_URL


def parse_excel_to_chunks(excel_path):
    """Read Excel and split into text chunks."""
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Excel file not found: {excel_path}")

    with pd.ExcelFile(excel_path) as xls:
        chunks = []
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            for idx, row in df.iterrows():
                text = " ".join([str(cell) for cell in row if pd.notnull(cell)])
                if text.strip():
                    chunks.append({
                        "text": text,
                        "sheet": sheet_name,
                        "row": idx
                    })
        if not chunks:
            raise ValueError("No data found in Excel file.")
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
    chunks = parse_excel_to_chunks(EXCEL_PATH)
    count = ingest_to_weaviate(chunks)
    print(f"✅ Ingested {count} chunks into Weaviate.")


if __name__ == "__main__":
    main()
