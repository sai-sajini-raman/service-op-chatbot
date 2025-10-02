
# test.py
import streamlit as st
import uuid
import time

# --- Mock answer_query ---
def answer_query(query, conversation_id, user_id):
    time.sleep(1.0)  # simulate latency
    return {
        "answer": f"🔎 Mock response for query: '{query}'",
        "chunks": [{"sheet": "MockSheet", "row": 1, "distance": 0.01, "text": f"Details for {query}"}],
        "latency": 1.0,
    }

st.set_page_config(
    page_title="Sample Chatbot Agent",
    layout="wide",
    initial_sidebar_state="auto"
)

st.title("Sample Chatbot Agent")

# --- Custom CSS ---
st.markdown(
    """
    <style>
    :root {
        --primary-color: slateBlue;
        --background-color: mintCream;
        --secondary-background-color: darkSeaGreen;
        --base-radius: 9999px; /* full */
    }

    body, .stApp {
        background-color: var(--background-color);
        font-family: 'Segoe UI', sans-serif;
    }

    .new-chat-btn {
        position: absolute;
        top: 12px;
        left: 12px;
        z-index: 999;
    }

.scrollable-chat {
    position: absolute;
    top: 80px; /* adjust based on your title/question cards */
    bottom: 100px; /* leave space for input box */
    left: 0;
    right: 0;
    padding: 8px;
    overflow-y: auto;
}

div.stVerticalBlock > div.fixed-bottom-input {
    position: fixed !important;
    bottom: 0 !important;
    left: 0 !important;
    width: 100% !important;
    z-index: 1000 !important;
    padding: 12px !important;
    background: rgba(255,255,255,0.9) !important;
}

    .chat-bubble-left {
        background: rgba(255, 255, 255, 0.25);
        color: #222;
        border-radius: var(--base-radius);
        padding: 12px 18px;
        margin-bottom: 8px;
        max-width: 70%;
        display: inline-block;
        word-break: break-word;
        backdrop-filter: blur(8px) saturate(180%);
        -webkit-backdrop-filter: blur(8px) saturate(180%);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    .chat-bubble-right {
        background: rgba(72, 61, 139, 0.85); /* slateBlue translucent */
        color: #fff;
        border-radius: var(--base-radius);
        padding: 12px 18px;
        margin-bottom: 8px;
        max-width: 70%;
        display: inline-block;
        float: right;
        word-break: break-word;
        backdrop-filter: blur(8px) saturate(180%);
        -webkit-backdrop-filter: blur(8px) saturate(180%);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }

    .sources-bubble {
        background: rgba(144, 238, 144, 0.3); /* light green translucent */
        color: #222;
        border-radius: var(--base-radius);
        padding: 10px 16px;
        margin-bottom: 12px;
        max-width: 70%;
        display: inline-block;
        font-size: 0.95em;
        word-break: break-word;
        backdrop-filter: blur(6px) saturate(180%);
        -webkit-backdrop-filter: blur(6px) saturate(180%);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    .fixed-bottom-input {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100vw;
        background: rgba(255,255,255,0.85);
        padding: 16px 0 12px 0;
        z-index: 100;
        border-top: 1px solid #eee;
        box-shadow: 0px -4px 12px rgba(0,0,0,0.06);
        backdrop-filter: blur(6px) saturate(180%);
        -webkit-backdrop-filter: blur(6px) saturate(180%);
    }

    .send-btn {
        background: none;
        border: none;
        cursor: pointer;
        margin-left: 8px;
        font-size: 1.7em;
        color: var(--primary-color);
        transition: color 0.2s;
    }
    .send-btn:active {
        color: #5a3ea1;
    }

    /* --- Question Cards --- */
    div.stButton > button {
        background: linear-gradient(
            135deg,
            rgba(255, 255, 255, 0.12),
            rgba(255, 255, 255, 0.08)
        );
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        padding: 16px 22px;
        font-size: 1em;
        cursor: pointer;
        transition: all 0.25s ease-in-out;
        backdrop-filter: blur(14px) saturate(180%);
        -webkit-backdrop-filter: blur(14px) saturate(180%);
        color: #000;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
        text-align: center;
        min-width: 200px;
        margin: 6px;
    }

    div.stButton > button:hover {
        background: rgba(72, 61, 139, 0.35); /* slateBlue hover */
        border-color: rgba(72, 61, 139, 0.6);
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
        color: #fff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Session State Initialization ---
if "conversation_id" not in st.session_state:
    st.session_state["conversation_id"] = str(uuid.uuid4())
if "user_id" not in st.session_state:
    st.session_state["user_id"] = f"user_{str(uuid.uuid4())[:8]}"
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "sources_history" not in st.session_state:
    st.session_state["sources_history"] = []
if "latency" not in st.session_state:
    st.session_state["latency"] = None
if "user_query" not in st.session_state:
    st.session_state["user_query"] = ""
if "clear_input" not in st.session_state:
    st.session_state["clear_input"] = False
if "pending_query" not in st.session_state:
    st.session_state["pending_query"] = ""
if "show_questions" not in st.session_state:
    st.session_state["show_questions"] = True

# --- New Chat Button ---
new_chat_clicked = st.button("🗑️ New Chat", key="new_chat_btn", help="Start a new conversation", use_container_width=False)
if new_chat_clicked:
    st.session_state["conversation_id"] = str(uuid.uuid4())
    st.session_state["chat_history"] = []
    st.session_state["sources_history"] = []
    st.session_state["latency"] = None
    st.session_state["user_query"] = ""
    st.session_state["pending_query"] = ""
    st.session_state["clear_input"] = True
    st.session_state["show_questions"] = True
    st.rerun()

# --- Predefined Question Cards ---
if st.session_state["show_questions"] and not st.session_state["chat_history"]:
    st.subheader("💡 Try asking:")
    predefined_questions = [
        "What is the status of incident INC123?",
        "Show me today's critical incidents",
        "Which team is handling the payment failures?",
        "Give me a summary of recent major incidents"
    ]

    cols = st.columns(len(predefined_questions))
    for i, q in enumerate(predefined_questions):
        if cols[i].button(q, key=f"pre_q_{i}"):
            st.session_state["user_query"] = q
            st.session_state["clear_input"] = False
            st.session_state["show_questions"] = False
            st.session_state["pending_query"] = q
            st.rerun()

# --- Conversation Chat Bubbles ---
st.markdown("<div class='scrollable-chat'style='height:65vh; overflow-y:auto; margin-bottom:80px;>", unsafe_allow_html=True)
for idx, msg in enumerate(st.session_state["chat_history"]):
    if msg["role"] == "assistant":
        st.markdown(f'<div class="chat-bubble-left">{msg["content"]}</div>', unsafe_allow_html=True)
        if len(st.session_state["sources_history"]) > idx // 2:
            sources = st.session_state["sources_history"][idx // 2]
            if sources and len(sources) > 0:
                sources_html = ""
                for chunk in sources:
                    sheet = chunk.get("sheet")
                    row = chunk.get("row")
                    dist = chunk.get("distance")
                    text = chunk.get("text", "")[:100]
                    sources_html += f'<div>`{sheet}` | Row: `{row}` | Distance: `{dist:.4f}`<br>Text: {text}...</div><hr style="margin:2px 0">'
                st.markdown(f'<div class="sources-bubble">{sources_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble-right">{msg["content"]}</div>', unsafe_allow_html=True)
    st.markdown('<div style="clear:both;"></div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.get("latency") is not None:
    st.markdown(f"**Response time:** {st.session_state['latency']:.2f} seconds")

# --- Submit Query Function ---
def submit_query():
    if st.session_state["user_query"].strip():
        st.session_state["pending_query"] = st.session_state["user_query"].strip()
        st.session_state["user_query"] = ""  # clear input box
        st.rerun()

# --- Input Field at Bottom ---
input_placeholder = st.empty()
with input_placeholder.container():
    st.markdown('<div class="fixed-bottom-input">', unsafe_allow_html=True)
    col1, col2 = st.columns([12, 1])
    user_query = col1.text_input(
        "Type your message...",
        value=st.session_state.get("user_query", ""),   
        key="user_query",
        label_visibility="collapsed",
        placeholder="Ask your question...",
        on_change=submit_query   # pressing Enter will trigger this
    )
    col2.button("➤", key="send_btn", help="Send your message", on_click=submit_query)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Message Sending Logic ---
if st.session_state["pending_query"]:
    query = st.session_state["pending_query"]
    st.session_state["pending_query"] = ""

    with st.spinner("Retrieving answer..."):
        try:
            result = answer_query(query, st.session_state["conversation_id"], st.session_state["user_id"])
            st.session_state["chat_history"].append({"role": "user", "content": query})
            st.session_state["chat_history"].append({"role": "assistant", "content": result["answer"]})
            st.session_state["sources_history"].append(result["chunks"])
            st.session_state["latency"] = result["latency"]
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")
