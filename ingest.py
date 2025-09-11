# ingest.py
import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from config import EXCEL_PATH, EMBEDDING_MODEL, CHROMA_DB_PATH, CHROMA_COLLECTION_NAME
import os


def parse_excel_to_chunks(excel_path):
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Excel file not found: {excel_path}")
    xls = pd.ExcelFile(excel_path)
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


def ingest_to_chromadb(chunks):
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_or_create_collection(CHROMA_COLLECTION_NAME)
    model = SentenceTransformer(EMBEDDING_MODEL)
    for chunk in chunks:
        text = chunk["text"]
        metadata = {"sheet": chunk["sheet"], "row": chunk["row"]}
        id_ = f"{chunk['sheet']}_{chunk['row']}"
        embedding = model.encode([text])[0].tolist()
        collection.add(documents=[text], embeddings=[embedding], metadatas=[metadata], ids=[id_])
    return len(chunks)


def main():
    chunks = parse_excel_to_chunks(EXCEL_PATH)
    count = ingest_to_chromadb(chunks)
    print(f"Ingested {count} chunks into ChromaDB.")


if __name__ == "__main__":
    main()
