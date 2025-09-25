import os
import pandas as pd
from sentence_transformers import SentenceTransformer
import weaviate
from config import EXCEL_PATH, EMBEDDING_MODEL, WEAVIATE_CLASS_NAME, WEAVIATE_URL

import pdfplumber
import docx

def parse_to_chunks(file_path):
    """Parse the file at file_path into text chunks depending on type (Excel, PDF, Word), including column headers in chunk text for tabular data."""
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    chunks = []

    if ext in [".xlsx", ".xls"]:
        with pd.ExcelFile(file_path) as xls:
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                headers = df.columns.tolist()
                for idx, row in df.iterrows():
                    row_data = {header: row[header] for header in headers}
                    chunk_text = ", ".join([f"{k}: {v}" for k, v in row_data.items() if pd.notnull(v)])
                    if chunk_text.strip():
                        chunks.append({
                            "text": chunk_text,
                            "sheet": sheet_name,
                            "row": idx,
                            "source_file": os.path.basename(file_path)
                        })
    elif ext == ".pdf":
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text and text.strip():
                    paragraphs = [p for p in text.split('\n') if p.strip()]
                    for j, para in enumerate(paragraphs):
                        if para.strip():
                            chunks.append({
                                "text": para.strip(),
                                "sheet": f"page_{i+1}",
                                "row": j,
                                "source_file": os.path.basename(file_path)
                            })
    elif ext == ".docx":
        doc = docx.Document(file_path)
        for i, para in enumerate(doc.paragraphs):
            text = para.text.strip()
            if text:
                chunks.append({
                    "text": text,
                    "sheet": "docx",
                    "row": i,
                    "source_file": os.path.basename(file_path)
                })
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    if not chunks:
        raise ValueError(f"No data found in {file_path}.")

    return chunks

def parse_all_data_folder():
    """Detects all supported files in data/ and parses them to chunks."""
    data_dir = os.path.abspath("data")
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Data folder not found: {data_dir}")
    chunks = []
    for fname in os.listdir(data_dir):
        if fname.lower().endswith(('.xlsx', '.xls', '.pdf', '.docx')):
            file_path = os.path.join(data_dir, fname)
            chunks.extend(parse_to_chunks(file_path))
    if not chunks:
        raise ValueError("No supported files found or no data parsed in the data folder.")
    return chunks

def ingest_to_weaviate(chunks):
    """Ingest chunks into Weaviate v4."""
    client = weaviate.Client("http://localhost:8080")
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
    model = SentenceTransformer(EMBEDDING_MODEL)
    for chunk in chunks:
        embedding = model.encode([chunk["text"]])[0].tolist()
        resp = client.data_object.create(
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
    chunks = parse_all_data_folder()
    count = ingest_to_weaviate(chunks)
    print(f"✅ Ingested {count} chunks from all supported files in 'data' into Weaviate.")

if __name__ == "__main__":
    main()