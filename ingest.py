import os
import pandas as pd
from sentence_transformers import SentenceTransformer
import weaviate
from config import EMBEDDING_MODEL, WEAVIATE_EXCEL_CLASS_NAME, WEAVIATE_DOCUMENT_CLASS_NAME, WEAVIATE_URL

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
                df.columns = df.columns.str.strip()
                for idx, row in df.iterrows():
                    row_data = {header: row[header] for header in headers}
                    chunk_text = ", ".join([f"{k}: {v}" for k, v in row_data.items() if pd.notnull(v)])
                    # # Convert incident_date to ISO format
                    # raw_date = df.loc[idx].get("Reported Date", None)
                    # incident_date = None
                    # if pd.notnull(raw_date):
                    #     try:
                    #         incident_date = pd.to_datetime(raw_date).date().isoformat()
                    #     except Exception:
                    #         incident_date = str(raw_date)
                    if chunk_text.strip():
                        chunks.append({
                            "text": chunk_text,
                            "sheet": sheet_name,
                            "row": idx,
                            "source_file": os.path.basename(file_path),
                            "incident_date": row.get("Reported Date", None),
                            "incident_number": row.get("Incident", None),
                            "incident_category": row.get("Inc Category", None),
                            "problem_record": row.get("Problem Record", None),
                            "portfolio": row.get("Product Portfolio -Area of cause", None),
                            "application": row.get("Application/Service Impacted?", None)
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
    """Detects all supported files in data/ and parses them to chunks, grouped by file type."""
    data_dir = os.path.abspath("data")
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Data folder not found: {data_dir}")
    
    excel_chunks = []
    other_chunks = []
    
    for fname in os.listdir(data_dir):
        if fname.lower().endswith(('.xlsx', '.xls', '.pdf', '.docx')):
            file_path = os.path.join(data_dir, fname)
            chunks = parse_to_chunks(file_path)
            
            # Separate Excel files from others
            if fname.lower().endswith(('.xlsx', '.xls')):
                excel_chunks.extend(chunks)
            else:
                other_chunks.extend(chunks)
    
    if not excel_chunks and not other_chunks:
        raise ValueError("No supported files found or no data parsed in the data folder.")
    
    return excel_chunks, other_chunks

def create_class_if_not_exists(client, class_name):
    """Create a Weaviate class if it doesn't exist."""
    existing_classes = [cls["class"] for cls in client.schema.get()["classes"]]
    if class_name not in existing_classes:
        class_obj = {
            "class": class_name,
            "properties": [
                {"name": "text", "dataType": ["text"], "indexFilterable": True},
                {"name": "sheet", "dataType": ["text"], "indexFilterable": True},
                {"name": "row", "dataType": ["int"], "indexFilterable": True},
                {"name": "source_file", "dataType": ["text"], "indexFilterable": True},
                {"name": "incident_date", "dataType": ["text"], "indexFilterable": True},
                {"name": "incident_number", "dataType": ["text"], "indexFilterable": True},
                {"name": "incident_category", "dataType": ["text"], "indexFilterable": True},
                {"name": "problem_record", "dataType": ["text"], "indexFilterable": True},
                {"name": "portfolio", "dataType": ["text"], "indexFilterable": True},
                {"name": "application", "dataType": ["text"], "indexFilterable": True}
                # "indexSearchable": True
            ]
        }
        client.schema.create_class(class_obj)

def ingest_to_weaviate_by_type(excel_chunks, other_chunks):
    import math

    def sanitize_value(val):
        if isinstance(val, float):
            if math.isnan(val) or math.isinf(val):
                return None
        if isinstance(val, str):
            return val.strip().lower()
        return val
    """Ingest chunks into separate Weaviate classes by file type."""
    from config import WEAVIATE_EXCEL_CLASS_NAME, WEAVIATE_DOCUMENT_CLASS_NAME
    
    client = weaviate.Client("http://localhost:8080")
    model = SentenceTransformer(EMBEDDING_MODEL)
    
    # Use class names from config
    excel_class = WEAVIATE_EXCEL_CLASS_NAME
    other_class = WEAVIATE_DOCUMENT_CLASS_NAME
    
    total_count = 0
    
    # Ingest Excel chunks
    if excel_chunks:
        create_class_if_not_exists(client, excel_class)
        for chunk in excel_chunks:
            embedding = model.encode([chunk["text"]])[0].tolist()
            client.data_object.create(
                data_object={
                    "text": chunk["text"],
                    "sheet": sanitize_value(chunk["sheet"]),
                    "row": int(chunk["row"]),
                    "source_file": sanitize_value(chunk.get("source_file")),
                    "incident_date": str(sanitize_value(chunk.get("incident_date"))) if chunk.get("incident_date") is not None else None,
                    "incident_number": str(sanitize_value(chunk.get("incident_number"))) if chunk.get("incident_number") is not None else None,
                    "incident_category": sanitize_value(chunk.get("incident_category")),
                    "problem_record": str(sanitize_value(chunk.get("problem_record"))) if chunk.get("problem_record") is not None else None,
                    "portfolio": sanitize_value(chunk.get("portfolio")),
                    "application": sanitize_value(chunk.get("application"))
                },
                class_name=excel_class,
                vector=embedding
            )
        total_count += len(excel_chunks)
        print(f"✅ Ingested {len(excel_chunks)} Excel chunks into '{excel_class}'")
    
    # Ingest other file chunks
    if other_chunks:
        create_class_if_not_exists(client, other_class)
        for chunk in other_chunks:
            embedding = model.encode([chunk["text"]])[0].tolist()
            client.data_object.create(
                data_object={
                    "text": chunk["text"],
                    "sheet": chunk["sheet"],
                    "row": int(chunk["row"])
                },
                class_name=other_class,
                vector=embedding
            )
        total_count += len(other_chunks)
        print(f"✅ Ingested {len(other_chunks)} document chunks into '{other_class}'")
    
    return total_count

def main():
    excel_chunks, other_chunks = parse_all_data_folder()
    count = ingest_to_weaviate_by_type(excel_chunks, other_chunks)
    print(f"✅ Ingested {count} total chunks into separate Weaviate classes.")

if __name__ == "__main__":
    main()