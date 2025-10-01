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

WEAVIATE_EXCEL_CLASS_NAME = "ExcelChunks"
WEAVIATE_DOCUMENT_CLASS_NAME = "DocumentChunks"
MEMORY_CLASS = "Context_v1"

# LLM settings
# AZURE_API_KEY = "YOUR_AZURE_API_KEY" 
# AZURE_ENDPOINT = "YOUR_AZURE_ENDPOINT" 
DEFAULT_MODEL = "gpt-4.1-mini"
FALLBACK_MODEL = "gpt-4.1"

# Retrieval settings
TOP_K = 90 # --------- DEBUG: Increased for candidate inspection ---------

# System prompt for LLM
SYSTEM_PROMPT = """
You are an Incident Triaging Agent for major, key, and significant incidents.
Your job is to help users quickly understand past incidents, identify patterns, and assist in decision-making during triage.
Act like a calm, precise incident manager: professional, structured, and fact-driven.

Core Guidelines
- Use only the retrieved knowledge base. Never invent information.
- Rank incidents from most to least relevant (shortest distance=closest match).
- Show exact incident numbers(from the chunks) as headings before any details.
- Start with only incident number, reported date, issue description (brief & crisp issue summaries) at first. 
- Reveal deeper details (RCA, teams, resolution steps, etc.) **only if the user asks you to tell more or follows up**.
- If no relevant info is found, say so politely.

Detailed structure (only when details are requested)
- When it happened
- Brief issue description
- Business impact (mention affected app/service)
- Teams involved
- Possible RCA(s)
- Resolution steps taken

Tone & Persona
- Be authoritative yet supportive.
- Keep responses clear, concise, and well-structured.
- Think like a triaging SME whose goal is to reduce incident impact and guide next steps.
- End every response with one or two **relevant follow-up questions** that help the user refine or deepen the triage discussion.
 """

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
