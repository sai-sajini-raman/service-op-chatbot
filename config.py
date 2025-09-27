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

# Retrieval settings
TOP_K = 5 # --------- DEBUG: Increased for candidate inspection ---------

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
