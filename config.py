import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Gemini LLM
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")

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