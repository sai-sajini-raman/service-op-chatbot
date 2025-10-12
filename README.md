# SARA - Smart Automated Resolution Assistant

**AI-powered IT incident support chatbot with RAG (Retrieval-Augmented Generation) for rapid incident insights, triage, and resolution support.**

```
TEST-service-op-chatbot/
├── data/                    # Your knowledge base (Excel, PDFs, DOCX, TXT, MD)
├── rag_pipeline.py          # Core RAG engine with conversation memory
├── New_ui.py              # Streamlit web interface
├── ingest.py               # Data ingestion pipeline
├── config.py               # Central configuration
├── test_existing_chunks.py # Debug/testing utility
├── docker-compose.yml      # Weaviate setup
├── requirements.txt        # Python dependencies
├── current_class.txt       # Auto-generated class tracker
├── .env                    # Environment variables (create this)
└── README.md              # This file
```

## 🚀 Features

### **Core Capabilities**
- **🔍 Intelligent Search**: Hybrid search combining keyword (BM25) + semantic similarity
- **🧠 Conversation Memory**: Context-aware responses that remember previous exchanges
- **📊 Multi-format Support**: Excel, PDF, DOCX, TXT, Markdown files
- **⚡ Real-time Responses**: Fast retrieval with response time tracking
- **🎯 Auto-discovery**: Automatically finds and uses latest ingested data

### **Advanced RAG Pipeline**
- **Query Rewriting**: Enhances user queries using conversation context
- **Hybrid Retrieval**: Combines keyword and vector search for better results
- **Memory Management**: Per-conversation history with configurable window size
- **Source Attribution**: Clean filename citations for transparency

### **User Interfaces**
- **🌐 Web UI**: Modern Streamlit interface with guided onboarding
- **💻 CLI**: Command-line interface for direct testing
- **📱 Responsive**: Works on desktop and mobile devices

## 🛠️ Setup & Installation

### **1. Prerequisites**
- Python 3.8+
- Docker (for Weaviate)
- Google AI Studio API key for Gemini

### **2. Install Dependencies**
```bash
git clone <your-repo>
cd TEST-service-op-chatbot
pip install -r requirements.txt
```

### **3. Start Weaviate Database**
```bash
docker-compose up -d
```
*Weaviate will be available at http://localhost:8080*

### **4. Configure Environment**
Create a `.env` file:
```env
# Required
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Optional (defaults shown)
DATA_DIR=./data
WEAVIATE_HOST=localhost
WEAVIATE_PORT=8080
CHUNK_CLASS_PREFIX=Oct11_class
CHAT_WINDOW_SIZE=3
HYBRID_SEARCH_K=5
GEMINI_MODEL=models/gemini-2.0-flash-exp
```

### **5. Add Your Data**
Place your knowledge base files in the `data/` folder:
- **Excel**: `.xlsx` files (extracts metadata like portfolio, incident dates)
- **PDFs**: `.pdf` files (must have 8-digit incident number in filename like `90716711 - description.pdf`)
- **Documents**: `.docx`, `.txt`, `.md` files

### **6. Ingest Data**
```bash
python ingest.py
```
*This creates a timestamped class in Weaviate and updates `current_class.txt`*

### **7. Launch the Interface**

**Web Interface (Recommended):**
```bash
streamlit run New_ui.py
```

**Command Line Interface:**
```bash
python rag_pipeline.py
```

## 📋 Supported File Formats

### **Excel Files (.xlsx)**
- **Processes all sheets** automatically
- **Extracts metadata** from columns like:
  - Portfolio/Product Portfolio
  - Incident Reference/Incident Number
  - Reported Date/Incident Date
  - Priority, Category, Application, etc.
- **Flexible column mapping** - handles various naming conventions

### **PDF Files (.pdf)**
- **Filename-based incident extraction**: `90716711 - PIR - Description.pdf`
- **OCR support** via LlamaIndex PDFReader
- **Automatic text extraction** and chunking
- **Metadata enrichment** with incident numbers and file info

### **Other Formats**
- **DOCX**: Microsoft Word documents
- **TXT/MD**: Plain text and Markdown files

## 🎯 Usage Examples

### **Web Interface Queries**
- *"Tell me about contactless payment issues"*
- *"What incidents affected the Foods portfolio in April?"*
- *"Show me recent connectivity problems"*
- *"What was the root cause of incident 90716711?"*

### **Portfolio-based Search**
- Foods, FH&B, Customer Channels
- International, Group Technology Services
- HR, InfoSec, Enterprise Integration, SAP

### **Time-based Queries**
- *"Issues during clock change period"*
- *"Peak period incidents last month"*
- *"What happened in December 2024?"*

### **Application-specific Issues**
- Relex, ControlM, WCS, JDA Dispatcher
- ASO, POS systems

## 🔧 Configuration

### **Memory Settings**
```python
CHAT_WINDOW_SIZE = 3  # Number of recent exchanges to remember
```

### **Search Parameters**
```python
HYBRID_SEARCH_K = 5   # Top-k results to retrieve
```

### **Weaviate Settings**
```python
WEAVIATE_HOST = "localhost"
WEAVIATE_PORT = 8080
```

## 🚀 Adding New Data

1. **Add files** to the `./data` folder
2. **Run ingestion**: `python ingest.py`
3. **Automatic discovery**: The system automatically uses the newest data
4. **No restart required**: Web interface immediately sees new data

## 🧪 Testing & Debugging

### **Test Chunk Retrieval**
```bash
python test_existing_chunks.py
```

### **CLI Testing**
```bash
python rag_pipeline.py
```

### **Check Current Class**
```bash
cat current_class.txt
```

## 🔍 How It Works

### **1. Ingestion Pipeline**
- Processes files from `data/` folder
- Extracts text and metadata
- Creates embeddings using SentenceTransformer
- Stores in Weaviate with auto-generated class names

### **2. Query Processing**
- **Conversation Context**: Maintains per-conversation memory
- **Query Rewriting**: Enhances queries using chat history
- **Hybrid Search**: Combines keyword + semantic search
- **Response Generation**: Uses Gemini to synthesize answers

### **3. Memory Management**
- **Per-conversation tracking**: Each chat session has isolated memory
- **Context window**: Configurable number of recent exchanges
- **Smart integration**: Web UI interactions feed into RAG memory

## 🛡️ Technical Architecture

- **Backend**: LlamaIndex RAG pipeline with Weaviate vector database
- **Frontend**: Streamlit with responsive design
- **LLM**: Google Gemini 2.0 Flash for generation
- **Embeddings**: SentenceTransformer (all-MiniLM-L6-v2)
- **Search**: Hybrid (BM25 + vector similarity)
- **Memory**: ChatMemoryBuffer with conversation isolation

## 📊 Performance

- **Response Time**: Typically 1-3 seconds
- **Chunk Retrieval**: Top-5 most relevant documents
- **Memory Efficiency**: Sliding window prevents memory bloat
- **Scalability**: Handles hundreds of documents efficiently

## 🎨 Customization

### **Change Model**
Update `GEMINI_MODEL` in config.py or .env file

### **Adjust Chunk Size**
Modify `CHUNK_SIZE` in config.py

### **Custom Metadata**
Edit `EXCEL_METADATA_FIELDS` in config.py for your Excel column names

### **UI Styling**
Customize CSS in New_ui.py for branding

## 🔧 Troubleshooting

### **"No class found" Error**
```bash
python ingest.py  # Re-run ingestion
```

### **Weaviate Connection Issues**
```bash
docker-compose restart  # Restart Weaviate
```

### **Missing Dependencies**
```bash
pip install -r requirements.txt
```

### **API Key Issues**
Check your `.env` file has a valid `GEMINI_API_KEY`

## 📚 API Reference

### **Core Function**
```python
from rag_pipeline import answer_query

result = answer_query(
    query="Your question",
    conversation_id="unique_session_id", 
    user_id="user_identifier"
)

# Returns:
# {
#     "answer": "AI response text",
#     "chunks": [retrieved_documents],
#     "latency": 1.23,
#     "sources": ["file1.pdf", "file2.xlsx"]
# }
```

## 🤝 Contributing

1. **Add new file readers** in `ingest.py`
2. **Enhance metadata extraction** in `config.py`
3. **Improve UI components** in `New_ui.py`
4. **Extend query processing** in `rag_pipeline.py`



---

**SARA** - *Because every incident deserves intelligent resolution* 🎯