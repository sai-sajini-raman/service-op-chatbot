import os
import pandas as pd
from sentence_transformers import SentenceTransformer
import weaviate
from config import EMBEDDING_MODEL, WEAVIATE_EXCEL_CLASS_NAME, WEAVIATE_DOCUMENT_CLASS_NAME, WEAVIATE_URL

import pdfplumber
import docx
import fitz
import pytesseract
from PIL import Image
import io

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
                def get_first_available(row, columns):
                    for col in columns:
                        if col in row and pd.notnull(row[col]):
                            return row[col]
                    return None

                for idx, row in df.iterrows():
                    row_data = {header: row[header] for header in headers}
                    chunk_text = ", ".join([f"{k}: {v}" for k, v in row_data.items() if pd.notnull(v)])

                    # Metadata extraction with fallback columns
                    incident_number = get_first_available(row, ["Incident", "Incident Reference"])
                    incident_date = get_first_available(row, ["Reported Date", "Incident Reported Date"])
                    portfolio = get_first_available(row, ["Product Portfolio -Area of cause", "Portfolio Impacted"])
                    application = get_first_available(row, ["Application/Service Impacted?"])

                    if chunk_text.strip():
                        chunks.append({
                            "text": chunk_text,
                            "sheet": sheet_name,
                            "row": idx,
                            "source_file": os.path.basename(file_path),
                            "portfolio": portfolio,
                            "incident_date": incident_date,
                            "incident_number": incident_number,
                            "application": application
                        })
    elif ext == ".pdf":
        

        doc = fitz.open(file_path)
        for i, page in enumerate(doc):
            pix = page.get_pixmap()
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            ocr_text = pytesseract.image_to_string(img)
            if ocr_text and ocr_text.strip():
                paragraphs = [p for p in ocr_text.split('\n') if p.strip()]
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
                {"name": "text", "dataType": ["text"]},
                {"name": "sheet", "dataType": ["text"]},
                {"name": "row", "dataType": ["int"]},
                {"name": "source_file", "dataType": ["text"]},
                {"name": "portfolio", "dataType": ["text"]},
                # {"name": "incident_date", "dataType": ["date"]},
                {"name": "incident_date", "dataType": ["text"]},
                {"name": "application", "dataType": ["text"]},
            ]
        }
        client.schema.create_class(class_obj)

def ingest_to_weaviate_by_type(excel_chunks, other_chunks):
    import math

    def sanitize_value(val):
        if isinstance(val, float):
            if math.isnan(val) or math.isinf(val):
                return None
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
                    "text": sanitize_value(chunk["text"]),
                    "sheet": sanitize_value(chunk["sheet"]),
                    "row": int(chunk["row"]),
                    "source_file": sanitize_value(chunk.get("source_file")),
                    "portfolio": sanitize_value(chunk.get("portfolio")),
                    "incident_date": str(sanitize_value(chunk.get("incident_date"))) if chunk.get("incident_date") is not None else None,
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