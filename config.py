# config.py

# Path to the Excel knowledge source
EXCEL_PATH = "knowledge.xlsx"

# Embedding model name (HuggingFace)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# ChromaDB settings
import os
CHROMA_DB_PATH = os.path.abspath("chromadb/")
CHROMA_COLLECTION_NAME = "excel_chunks_v2"

# Weaviate settings
WEAVIATE_URL = "http://localhost:8080"  # needs to be updated hosted elsewhere
WEAVIATE_CLASS_NAME = "ExcelChunk"

# LLM settings
AZURE_API_KEY = "YOUR_AZURE_API_KEY"  # Set via environment variable or config
AZURE_ENDPOINT = "YOUR_AZURE_ENDPOINT"  # Set via environment variable or config
DEFAULT_MODEL = "gpt-4.1-mini"
FALLBACK_MODEL = "gpt-4.1"

# Retrieval settings
TOP_K = 5 # --------- DEBUG: Increased for candidate inspection ---------

# System prompt for LLM
SYSTEM_PROMPT = "You are a helpful assistant. Answer using the provided context and user query. Use only the most relevant context to answer the user query. Give good structured output that can be easily understood by the user If the context does not contain the answer, politely say it is out of your scope."