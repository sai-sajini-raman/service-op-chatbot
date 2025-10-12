# RAG Chatbot (Console)

    rag-chatbot/
    ├── data/                    # Your knowledge base (excels, pdfs, docs)
    ├── main.py                  # Console chatbot entrypoint
    ├── ingest.py                # Data ingestion pipeline
    ├── config.py                # Central config (paths, keys, settings)
    ├── requirements.txt         # Python dependencies
    ├── README.md                # Usage instructions & setup


## Features

- Uses LlamaIndex for retrieval, memory, and orchestration
- Gemini LLM (Google AI Studio API key) for query rewriting and response
- Hybrid search (keyword + vector) with Weaviate backend (v4 client)
- Knowledge base from 'data' folder (Excel, PDF, DOCX, TXT, MD)
- Excel: Extracts 'portfolio' (string), 'incident_date' (date) as metadata, **supports multiple possible column names**
- Chat memory: Window size 3 (most recent exchanges)
- Console/terminal chat interface

## Setup

1. Clone repo and `cd rag-chatbot`
2. Place your data files in the `data/` folder.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set your Gemini API key in a `.env` file:
   ```
   GEMINI_API_KEY=your_real_key
   ```
5. Optional: Set class prefix, host, port in `.env`:
   ```
   CHUNK_CLASS_PREFIX=MyChatbot
   WEAVIATE_HOST=localhost
   WEAVIATE_PORT=8080
   ```
6. Ingest your data:
   ```bash
   python ingest.py
   ```
7. Run the chatbot:
   ```bash
   python main.py
   ```

## Configuration

Edit `config.py` or use `.env` for paths, window size, Weaviate host/port, etc.

## Notes

- Make sure Weaviate is running locally (`docker-compose up` in your Weaviate folder).
- You can extend the ingestion pipeline for more metadata or file types.
- v4 client integration for Weaviate.