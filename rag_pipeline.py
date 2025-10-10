import os
import time
from sentence_transformers import SentenceTransformer
import weaviate
from config import WEAVIATE_URL, WEAVIATE_EXCEL_CLASS_NAME, WEAVIATE_DOCUMENT_CLASS_NAME, EMBEDDING_MODEL, TOP_K, SYSTEM_PROMPT, DEFAULT_MODEL, FALLBACK_MODEL, MEMORY_CLASS

context_class = MEMORY_CLASS

PAIR_LIMIT = 2  # Only keep the most recent 2 user-bot pairs

def store_context(content, role, conversation_id, user_id):
    """
    Store a conversation entry in Context_v1 with timestamp.
    Assumes Context_v1 schema already exists.
    """
    client = weaviate.Client("http://localhost:8080")
    context_data = {
        "content": content,
        "role": role,
        "conversationId": conversation_id,
        "userId": user_id,
        "timestamp": int(time.time()),
    }
    try:
        client.data_object.create(data_object=context_data, class_name=context_class)
        print(f"Stored {role} message in {context_class} successfully")
    except Exception as e:
        print(f"Error storing message in {context_class}: {str(e)}")

def get_context_history(conversation_id):
    """
    Retrieve all context history for a given conversation_id from Context_v1.
    Returns messages sorted by timestamp ascending, but only the last PAIR_LIMIT pairs.
    """
    client = weaviate.Client("http://localhost:8080")
    try:
        result = (
            client.query
            .get(context_class, ["content", "role", "conversationId", "userId", "timestamp"])
            .with_where({
                "path": ["conversationId"],
                "operator": "Equal",
                "valueString": conversation_id
            })
            .with_limit(PAIR_LIMIT * 2)
            .do()
        )
        messages = result.get("data", {}).get("Get", {}).get(context_class, [])
        messages = sorted(messages, key=lambda x: x["timestamp"])
        # Only keep the last PAIR_LIMIT pairs (user/assistant alternation)
        # Each pair is [user, assistant], so take the last PAIR_LIMIT*2 messages
        return messages[-(PAIR_LIMIT * 2):]
    except Exception as e:
        print(f"Error retrieving context history: {str(e)}")
        return []

def trim_context_history_if_needed(conversation_id):
    """
    Truncate old context entries if more than PAIR_LIMIT pairs (4 messages) exist.
    """
    client = weaviate.Client("http://localhost:8080")
    try:
        result = (
            client.query
            .get(context_class, ["content", "role", "conversationId", "userId", "timestamp", "id"])
            .with_where({
                "path": ["conversationId"],
                "operator": "Equal",
                "valueString": conversation_id
            })
            .with_limit(100)
            .do()
        )
        messages = result.get("data", {}).get("Get", {}).get(context_class, [])
        messages = sorted(messages, key=lambda x: x["timestamp"])
        # If more than PAIR_LIMIT*2 messages, delete the oldest ones
        if len(messages) > PAIR_LIMIT * 2:
            to_delete = messages[:len(messages) - PAIR_LIMIT * 2]
            for msg in to_delete:
                try:
                    client.data_object.delete(
                        id=msg["id"], class_name=context_class
                    )
                except Exception as e:
                    print(f"Error deleting old context msg: {str(e)}")
    except Exception as e:
        print(f"Error trimming context history: {str(e)}")


def retrieve_chunks(query, top_k=TOP_K, filter_dict=None):
    client = weaviate.Client("http://localhost:8080")
    model = SentenceTransformer(EMBEDDING_MODEL)
    query_emb = model.encode([query])[0].tolist()

    where_clause = None
    if filter_dict:
        operands = []
        for field, values in filter_dict.items():
            if values:
                operands.append({
                    "path": [field],
                    "operator": "ContainsAny",
                    "valueString": values if isinstance(values, list) else [values]
                })
        if operands:
            where_clause = {
                "operator": "And",
                "operands": operands
            }
    metadata_fields = [
        "text", "sheet", "row", "incident_date", "incident_number", "incident_category",
        "problem_record", "portfolio", "application", "source_file"
    ]
    excel_query = client.query.get(WEAVIATE_EXCEL_CLASS_NAME, metadata_fields)
    if where_clause:
        excel_query = excel_query.with_where(where_clause)
    excel_results = (
        excel_query
        .with_near_vector({"vector": query_emb})
        .with_limit(top_k)
        .with_additional(["distance"])
        .do()
    )

    doc_query = client.query.get(WEAVIATE_DOCUMENT_CLASS_NAME, metadata_fields)
    # if where_clause:
    #     doc_query = doc_query.with_where(where_clause)
    doc_results = (
        doc_query
        .with_near_vector({"vector": query_emb})
        .with_limit(top_k)
        .with_additional(["distance"])
        .do()
    )
    chunks = []
    excel_hits = excel_results.get("data", {}).get("Get", {}).get(WEAVIATE_EXCEL_CLASS_NAME, [])
    doc_hits = doc_results.get("data", {}).get("Get", {}).get(WEAVIATE_DOCUMENT_CLASS_NAME, [])
    all_hits = excel_hits + doc_hits
    for hit in all_hits:
        chunks.append({
            "text": hit.get("text"),
            "sheet": hit.get("sheet"),
            "row": hit.get("row"),
            "incident_date": hit.get("incident_date"),
            "incident_number": hit.get("incident_number"),
            "incident_category": hit.get("incident_category"),
            "problem_record": hit.get("problem_record"),
            "portfolio": hit.get("portfolio"),
            "application": hit.get("application"),
            "source_file": hit.get("source_file"),
            "distance": hit.get("_additional", {}).get("distance")
        })
    return chunks

def build_prompt(context_chunks, user_query, conversation_history):

    history_txt = ""
    from datetime import date
    today = date.today()
    previous_query = ""
    for msg in conversation_history:
        history_txt += f"{msg['role'].capitalize()}: {msg['content']}\n"
        if msg['role'] == 'user':
            previous_query += f"{msg['content']} + "

    # Special handling: if context_chunks is a single dict from Excel row, format nicely
    if len(context_chunks) == 1 and isinstance(context_chunks[0]['text'], dict):
        row = context_chunks[0]['text']
        context = "\n".join([f"**{k}:** {v}" for k, v in row.items()])
    else:
        context = "\n".join([f"[{c['sheet']}:{c['row']}] {c['text']}" for c in context_chunks])

    prompt = (
        f"{today}\n"
        f"{SYSTEM_PROMPT}\n\n"
        f"Conversation History:\n{history_txt}\n"
        f"Context:\n{context}\n\n"
        f"User Query: {user_query}"
        f"Answer the 'User Query' using the above 'Context' to answer the query and 'Conversation History' to maintain conversation."
    )
    return prompt

def build_filter_prompt(user_query, metadata_dict):
    metadata_info = "\n".join([f"- {field}: {', '.join(map(str, vals))}" for field, vals in metadata_dict.items() if vals])
    prompt = (
        f"You are an expert at analyzing user queries to extract relevant metadata filters.\n"
        f"Given the user query and the available metadata fields with their possible values, identify which metadata fields and values are relevant to the query.\n\n"
        f"User Query: {user_query}\n\n"
        f"Allowed Metadata Fields and Values:\n{metadata_info}\n\n"
        f"PROVIDE ONLY PORTFOLIO FILTERS. Do not provide any other metadata fields. Provide incident_number filter only if user asks for a specific incident number\n"
        f"provide filter only if it is available in the provided metadata fields and values\n"
        f"Output a JSON object with field names as keys and lists of relevant values. If no relevant metadata, return an empty JSON object."
        f"Example:\n"
        f"1) User Query: Show allocation issues in Foods portfolio\n"
        f'Output: {{"portfolio":["food commercial trading","foods commercial trading","food supply chain","foods supply chain","foods"]}}\n\n'
        f"2) User Query: I want to know about C&H issues\n"
        f'Output: {{"portfolio":["c&h & intl supply chain","c&h commercial trading"]}}\n\n'

    )
    return prompt

def get_metadata_uniques(class_name, metadata_fields):
    import weaviate
    client = weaviate.Client("http://localhost:8080")
    # Query all objects, requesting only metadata fields
    result = client.query.get(class_name, metadata_fields).with_limit(1000).do()
    objects = result.get("data", {}).get("Get", {}).get(class_name, [])
    
    metadata_dict = {field: set() for field in metadata_fields}
    for obj in objects:
        for field in metadata_fields:
            val = obj.get(field)
            if val is not None:
                metadata_dict[field].add(val)
    # Convert sets to lists
    metadata_dict = {field: list(vals) for field, vals in metadata_dict.items()}
    return metadata_dict

def call_llm(prompt):
    import os
    from dotenv import load_dotenv
    from google import genai
    from google.genai import types

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")

    client = genai.Client(api_key=api_key)
    model_name = "gemini-2.5-flash-lite"  # You can make this configurable if needed

    # Gemini expects contents as a list of strings (the prompt)
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt],
            config=types.GenerateContentConfig(
                temperature=0.7,
                top_p=0.9,
                top_k=40,
            ),
        )
        return response.text.strip() if response.text else "No response text returned."
    except Exception as e:
        return f"Error generating response: {str(e)}"

import re
import pandas as pd
def answer_query(user_query, conversation_id, user_id):
    start = time.time()
    store_context(user_query, "user", conversation_id, user_id)
    history = get_context_history(conversation_id)
    trim_context_history_if_needed(conversation_id)

    # Regex for all "incident" + 8 digits
    matches = re.findall(r'incident[\s:-]*(\d{8})', user_query, re.IGNORECASE)
    matches = False
    if matches:
        incident_numbers = set(matches)
        import glob
        context_chunks = []
        sources = []
        excel_files = glob.glob('data/*.xlsx')
        for incident_number in incident_numbers:
            found = False
            for excel_path in excel_files:
                try:
                    df = pd.read_excel(excel_path)
                    if 'Incident' not in df.columns:
                        continue
                    row = df[df['Incident'] == int(incident_number)]
                    if not row.empty:
                        context_chunks.append({
                            "text": row.iloc[0].to_dict(),
                            "sheet": excel_path,
                            "row": int(row.index[0]),
                            "distance": 0.0
                        })
                        sources.append((excel_path, int(row.index[0])))
                        found = True
                        break  # Stop after first match for this incident number
                except Exception as e:
                    print(f"Excel lookup failed in {excel_path}: {e}")
        if context_chunks:
            prompt = build_prompt(context_chunks, user_query, history)
            answer = call_llm(prompt)
            store_context(answer, "assistant", conversation_id, user_id)
            trim_context_history_if_needed(conversation_id)
            latency = time.time() - start
            return {
                "answer": answer,
                "sources": sources,
                "chunks": context_chunks,
                "latency": latency
            }
   
    # Analyze user query
    metadata_fields = [
        "incident_date", "incident_number", "incident_category", 
        "problem_record", "portfolio", "application", 
        "sheet", "source_file", "row"
    ]
    metadata_dict = get_metadata_uniques(WEAVIATE_EXCEL_CLASS_NAME, metadata_fields)
    prompt_f = build_filter_prompt(user_query, metadata_dict)
    json_filter = call_llm(prompt_f)
    import json
    try:
        analysed_json = json.loads(json_filter)
    except Exception as e:
        analysed_json = None
        print(f"Failed to parse LLM output as JSON: {e}")
    # Fallback to embedding search
    retrieved_chunks = retrieve_chunks(user_query, filter_dict=analysed_json)
    filtered_chunks = [c for c in retrieved_chunks if c.get('distance') is not None and c.get('distance') < 0.8]

    # Fallback to filterless search if no chunks or filtered chunks are found
    if len(retrieved_chunks) == 0 or len(filtered_chunks) == 0:
        retrieved_chunks = retrieve_chunks(user_query, filter_dict=None)
        filtered_chunks = [c for c in retrieved_chunks if c.get('distance') is not None and c.get('distance') < 0.8]

    sorted_chunks = sorted(
        filtered_chunks,
        key=lambda c: c.get('distance') if c.get('distance') is not None else float('inf')
    )
    prompt = build_prompt(sorted_chunks, user_query, history)
    answer = call_llm(prompt)
    store_context(answer, "assistant", conversation_id, user_id)
    trim_context_history_if_needed(conversation_id)
    latency = time.time() - start
    sources = [(c['sheet'], c['row']) for c in sorted_chunks]
    return {
        "answer": answer,
        "sources": sources,
        "chunks": sorted_chunks,
        "latency": latency
    }