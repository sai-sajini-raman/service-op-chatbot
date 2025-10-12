<<<<<<< HEAD
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
=======
# config.py

# Path to the Excel knowledge source
# EXCEL_PATH = "knowledge.xlsx"
EXCEL_PATH = "data/"

# Embedding model name (HuggingFace)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# ChromaDB settings
import os
CHROMA_DB_PATH = os.path.abspath("chromadb/")
CHROMA_COLLECTION_NAME = "excel_chunks_ingest_v2"

# Weaviate settings
WEAVIATE_URL = "http://localhost:8080"  # needs to be updated hosted elsewhere

WEAVIATE_CLASS_NAME = "Excelpdfchunks_v4"

# LLM settings
# AZURE_API_KEY = "YOUR_AZURE_API_KEY" 
# AZURE_ENDPOINT = "YOUR_AZURE_ENDPOINT" 
DEFAULT_MODEL = "gpt-4.1-mini"
FALLBACK_MODEL = "gpt-4.1"
>>>>>>> 376396da3a0af583750614f36a751c757cc6dddc

# Gemini LLM
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")

<<<<<<< HEAD
# Data folder
DATA_DIR = os.getenv("DATA_DIR", "./data")

# Weaviate settings
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
WEAVIATE_HOST = os.getenv("WEAVIATE_HOST", "localhost")
WEAVIATE_PORT = int(os.getenv("WEAVIATE_PORT", 8080))

# Chat memory window size
CHAT_WINDOW_SIZE = int(os.getenv("CHAT_WINDOW_SIZE", 3))

# Hybrid search config
HYBRID_SEARCH_K = int(os.getenv("HYBRID_SEARCH_K", 5))  # top-k results

# Metadata extraction for Excel
EXCEL_METADATA_FIELDS = {
    "portfolio": {
        "type": "string",
        "possible_names": [
            "Product Portfolio -Area of cause", "Portfolio Impacted"
        ]
    },
    "incident_date": {
        "type": "date",
        "possible_names": [
            "Incident Reported Date", "Reported Date"
        ]
    },
    "incident_number": {
        "type": "string",
        "possible_names": [
            "Incident Reference", "Incident"
        ]
    },
    "incident_category": {
        "type": "string",
        "possible_names": [
            "Inc Category"
        ]
    },
    "incident_priority": {
        "type": "string",
        "possible_names": [
            "Priority"
        ]
    },
    "application": {
        "type": "string",
        "possible_names": [
            "Application/Service Impacted?"
        ]
    },
    "problem_record": {
        "type": "string",
        "possible_names": [
            "Problem Record"
        ]
    }
}

# Document chunk size for ingestion
CHUNK_SIZE = 1024  # adjust as needed

# Gemini model name (use default if not specified)
GEMINI_MODEL = "models/gemini-2.0-flash-exp"

# Weaviate class name prefix for chunk storage
CHUNK_CLASS_PREFIX = "Oct11_class"

def get_current_class_name():
    """Get the current class name for querying"""
    import weaviate
    import os
    
    # Method 1: Try to read from saved file
    try:
        with open("current_class.txt", "r") as f:
            class_name = f.read().strip()
            if class_name:
                print(f"Using class name from file: {class_name}")
                return class_name
    except FileNotFoundError:
        print("No saved class name found, checking Weaviate...")
    
    # Method 2: Query Weaviate for the most recent class
    try:
        client = weaviate.Client(url=f"http://{WEAVIATE_HOST}:{WEAVIATE_PORT}")
        existing_classes = [schema['class'] for schema in client.schema.get()['classes']]
        
        # Filter classes that start with our prefix
        matching_classes = [c for c in existing_classes if c.startswith(CHUNK_CLASS_PREFIX)]
        
        if matching_classes:
            # Sort by class name (includes timestamp) and get the latest
            latest_class = sorted(matching_classes)[-1]
            print(f"Found latest class in Weaviate: {latest_class}")
            return latest_class
        else:
            print(f"No classes found with prefix '{CHUNK_CLASS_PREFIX}'")
            return None
            
    except Exception as e:
        print(f"Error connecting to Weaviate: {e}")
        return None
=======
# System prompt for LLM
SYSTEM_PROMPT = """You are a helpful assistant. Answer using the provided context and user query. Give good structured output that can be easily understood by the user. 

Follow these instructions:
Based on the user query, answer with the following aspects(if applicable):
- When it happened previously?
- What was the issue? (brief description, on-point)
- What was the business impact? (also mention the application/service impacted)
- What are the teams invloved?
- What is the possible root cause/root causes (RCA) for this issue?
- What are the resolution steps taken?
Display the incidents from most relevent to least (smallest distance=closest match).
If your are listing incident, represent the incident IDs/numbers as heading before any data about the incidents.

Note: Use only the retrieved context to answer the user query. Don't make up answers. Be concise and to the point. If the context does not help you answer the query(distance > 0.65), politely say that you did not find best results in the provided documentation, and that you would be able to answer it with the given knowledge base. """

# # Hugging Face Auto-label settings
# USE_HF_AUTOLABEL = True  # <- toggle this flag for auto-suggestions

# Predefined candidate categories for Hugging Face
CANDIDATE_LABELS = [
    "Delay in Foods Final Order/Batch issue",
    "Duplicate ASNs",
    "Foods Logistics",
    "NDC Allocations Impact",
    "RDC Allocations Impact",
    "Inflated Orders",
    "NDC Allocations",
    "Frozen Allocations",
    "Open Pos",
    "Blue Yonder Issue",
    "Order plan issues",
    "Pricing issues",
    "NDC/Ambient Allocations",
    "RDC/Depot Allocations",
    "Open Text Issue",
    "FIND application issue",
    "SRD Ranging Issue",
    "Foods Platform Unavailability"
]
>>>>>>> 376396da3a0af583750614f36a751c757cc6dddc
