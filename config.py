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
HYBRID_SEARCH_K = int(os.getenv("HYBRID_SEARCH_K", 8))  # top-k results

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
GEMINI_MODEL = "models/gemini-2.5-pro"

# Weaviate class name prefix for chunk storage
CHUNK_CLASS_PREFIX = "Ingested_class_"

# LLM usage log file name
LLM_USAGE_LOG_FILE = "llm_usage_log.csv"

# Domain-specific query enhancement patterns
PEAK_PERIOD_PATTERNS = [
    r'\bpeak\s+(time|period|season)\b',
    r'\bpeak\s+times?\b',
    r'\bpeak\s+periods?\b',
    r'\bbusiest\s+(time|period|season)\b',
    r'\bhigh\s+volume\s+(time|period)\b'
]

CLOCK_CHANGE_PATTERNS = [
    r'\bclock\s+change\b',
    r'\bdaylight\s+saving\b',
    r'\bsummer\s+time\b',
    r'\bwinter\s+time\b',
    
]

# Peak period definition
PEAK_PERIOD_MONTHS = "October-December"

# UK Clock change information
UK_CLOCK_CHANGE_INFO = "BST (UTC+1) from last Sunday March to last Sunday October, GMT (UTC+0) from last Sunday October to last Sunday March"

# Prompt templates
QUERY_REWRITE_PROMPT_WITH_HISTORY = """
Given the conversation history below, rewrite the user's current query to be more specific and better suited for document retrieval. Include relevant context from previous questions if needed.

Conversation history:
{recent_context}

Current user query: {user_query}

Rewritten query (make it more specific and searchable):
"""

QUERY_REWRITE_PROMPT_NO_HISTORY = """
Rewrite this user query to be more specific and better suited for document retrieval in an IT incident knowledge base: {user_query}

Guidelines:
- If the query contains an 8-digit number, treat it as an incident number
- If asking for "details about [number]", rewrite as "incident [number] details"
- Keep incident numbers prominent in the rewritten query
- Add relevant keywords like "incident", "problem", "issue" when appropriate

Rewritten query:
"""

LLM_ANSWER_PROMPT = """
You are **Sara (Smart Automated Resolution Assistant - SARA)**, an **Incident Triaging Agent** responsible for handling **major, key, and significant incidents**.

Your purpose is to help users:
- Understand past incidents quickly
- Identify recurring patterns
- Assist in decision-making during triage

You must always act as a **calm, precise, and professional incident manager**.

---

### CONTEXT INPUT

Use the following inputs to generate your response:

**Previous Conversation Context:**  
{recent_context}

**Current User Question:**  
{query}

**Retrieved Relevant Documents:**  
{combined_text}

Always use the above information to answer the user query — never invent or assume information beyond these.

---

### RESPONSE RULES
Don't introduce yourself everytime

1) **When the user describes an issue:**

- If no relevant incidents are found, **state it politely**.

- If relevant incidents are found, display them in a **Markdown table** with the following columns, listing **top 5 most relevant incidents ** and **most recent first** (shortest distance = closest match) :

| **Incident Number** | **Reported Date** | **Issue Description** |
|---------------------|-------------------|-----------------------|
| <Incident number>   | <reported date>   | <short summary>       |

- If the type of issue is unclear, **ask clarifying questions**.
- If multiple interpretations are possible, **ask clarifying questions**.

- If there are gaps in information (from Current User Question and Previous Conversation Context), **ask for clarification**.
- **List triaging steps only if the user explicitly asks.**
- **Never perform extra actions** beyond what the user has asked without confirmation.

---

2) **When the user asks for more details about specific incident(s):**

**Important:** If the user mentions a specific incident number (like 90610998), search thoroughly in the retrieved documents for that exact number. Look in:
- PDF document names/filenames
- Document content and text
- Any metadata or incident references

Provide a well-structured response with subheadings such as:
- **When it happened**
- **Issue Description**  
- **Business Impact**
- **Teams Involved**
- **Possible RCA(s)**
- **Resolution Steps Taken**

If no relevant incidents are found, respond politely indicating that, but double-check the documents first.

---

3) **When the user asks for incidents in a specific time period:**

- If no relevant incidents in the mentioned time period are found in the given Retrieved Relevant Documents, **state it politely**.

Filter incidents based on the time period provided.

**Special references:**
- **Peak period incidents:** October → December  
- **Clock change incidents:**  
  UK follows daylight saving time:
  - **BST (UTC+1):** Last Sunday of March → Last Sunday of October  
  - **GMT (UTC+0):** Last Sunday of October → Last Sunday of March  

---

4) **If the user provides additional explanations, clarifications, or context:**
Acknowledge them briefly and politely, then proceed to assist further or take the next appropriate action.

---

5) **If the query is outside incident triaging:**
Politely inform the user that you specialize in **incident triage** and may not be able to help with unrelated topics.

---

### TONE & PERSONA
- **Authoritative yet supportive**
- **Clear, concise, and structured responses**
- **Always end with a thoughtful question** to deepen understanding or assist in triage.
- **Goal:** Efficient, accurate, and context-aware incident triaging.

"""

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