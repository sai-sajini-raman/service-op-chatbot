# config.py

# Path to the Excel knowledge source
# EXCEL_PATH = "knowledge.xlsx"
EXCEL_PATH = "MSI_MKI_knowledge100.xlsx"

# Embedding model name (HuggingFace)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# ChromaDB settings
import os
CHROMA_DB_PATH = os.path.abspath("chromadb/")
CHROMA_COLLECTION_NAME = "excel_chunks_ingest_v2"

# Weaviate settings
WEAVIATE_URL = "http://localhost:8080"  # needs to be updated hosted elsewhere

WEAVIATE_CLASS_NAME = "Excelpdfchunks_v3"

# LLM settings
# AZURE_API_KEY = "YOUR_AZURE_API_KEY" 
# AZURE_ENDPOINT = "YOUR_AZURE_ENDPOINT" 
DEFAULT_MODEL = "gpt-4.1-mini"
FALLBACK_MODEL = "gpt-4.1"

# Retrieval settings
TOP_K = 5 # --------- DEBUG: Increased for candidate inspection ---------

# System prompt for LLM
SYSTEM_PROMPT = "You are a helpful assistant. Answer using the provided context and user query. Give good structured output that can be easily understood by the user. If the query is about any kind of issue, answer with the following aspects: When it happened previously?, What is the possible root cause/root causes (RC) for this issue?, What can be the possible resolution? Note: Use only the retrieved context to answer the user query.  If the context does not help you answer the query, politely say that you did not find best results in the provided Knowledge Base, and you would be able to answer it if the user provides more documents on that. Don't make up answers. Be concise and to the point."