import streamlit as st
import uuid
import time
from rag_pipeline import answer_query
from config import IMG


st.set_page_config(
    page_title="Triaging Agent", 
    layout="wide"
    # initial_sidebar_state="auto"
)

st.title("Major Incident Triaging Chatbot")

# import base64

# # Path to your local image
# image_path = IMG  # Change to your image file

# # Encode image to base64
# with open(image_path, "rb") as img_file:
#     encoded = base64.b64encode(img_file.read()).decode()
        # background-image: url('data:image/jpg;base64,{encoded}');
        # background-size: cover;
        # background-position: center center;
        # background-repeat: no-repeat;
        # background-attachment: fixed;
        # font-family: 'Segoe UI', sans-serif;


st.markdown(
    f"""
    <style>
    :root {{
        --primary-color: slateBlue;
        --background-color: mintCream;
        --secondary-background-color: darkSeaGreen;
        --base-radius-right: 16px 16px 2px 16px;
        --base-radius-left: 16px 16px 16px 2px;
    }}

    body, .stApp {{
        background-color: var(--background-color);
        font-family: 'Segoe UI', sans-serif;

    }}

    .new-chat-btn {{
        position: absolute;
        top: 12px;
        left: 12px;
        z-index: 999;
    }}

    .chat-bubble-assistant {{
        background: rgba(255, 255, 255, 0.25);
        color: #222;
        border-radius: var(--base-radius-left);
        padding: 10px 16px;
        margin-bottom: 4px;
        max-width: 70%;
        display: inline-block;
        word-break: break-word;
        backdrop-filter: blur(8px) saturate(180%);
        -webkit-backdrop-filter: blur(8px) saturate(180%);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }}

    .chat-bubble-user {{
        background: rgba(72, 61, 139, 0.85); /* slateBlue translucent */
        color: #fff;
        border-radius: var(--base-radius-right);
        padding: 10px 16px;
        margin-bottom: 4px;
        max-width: 70%;
        display: inline-block;
        float: right;
        word-break: break-word;
        backdrop-filter: blur(8px) saturate(180%);
        -webkit-backdrop-filter: blur(8px) saturate(180%);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }}

    .sources-bubble {{
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
    }}

    .send-btn {{
        background: none;
        border: none;
        cursor: pointer;
        margin-left: 8px;
        font-size: 1.7em;
        color: var(--primary-color);
        transition: color 0.2s;
    }}
    .send-btn:active {{
        color: #5a3ea1;
    }}

    /* --- Question Cards --- */
    div.stButton > button {{
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
    }}

    div.stButton > button:hover {{
        background: rgba(72, 61, 139, 0.35); /* slateBlue hover */
        border-color: rgba(72, 61, 139, 0.6);
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
        color: #fff;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Session State Initialization ---
if "conversation_id" not in st.session_state:
    st.session_state["conversation_id"] = str(uuid.uuid4())
if "user_id" not in st.session_state:
    st.session_state["user_id"] = f"user_{str(uuid.uuid4())[:8]}"
if "welcome" not in st.session_state:
    st.session_state["welcome"] = True
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "sources_history" not in st.session_state:
    st.session_state["sources_history"] = []
if "user_query" not in st.session_state:
    st.session_state["user_query"] = ""
if "pending_query" not in st.session_state:
    st.session_state["pending_query"] = ""
if "latency" not in st.session_state:
    st.session_state["latency"] = None
if "show_questions" not in st.session_state:
    st.session_state["show_questions"] = True


if st.session_state["welcome"]:
    st.markdown("""
    ### 👋 *Welcome! I'm Sara.*
    *I am your AI-powered Smart Automated Resolution Assistant for rapid incident insights, triage, and resolution support.*


    **What can you do here?**
    - Instantly get the status of any incident.
    - Find out which teams or services are affected.
    - Ask about recent, trending, or resolved incidents.

    """)


if st.session_state["show_questions"]:
    st.subheader("Try asking:")
    predefined_questions = [
        "What is the status of incident INC123?",
        "Show me today's critical incidents",
        "List the major incidents in the past year",
        "Give me a summary of recent major incidents"
    ]
    cols = st.columns(len(predefined_questions))
    for i, q in enumerate(predefined_questions):
        if cols[i].button(q, key=f"pre_q_{i}"):
            # st.session_state["welcome"] = False
            # st.session_state["show_questions"] = False
            st.session_state["user_query"] = q
            st.session_state["pending_query"] = q
            st.session_state["chat_history"].append({"role": "user", "content": q})
            st.rerun()

for idx, msg in enumerate(st.session_state["chat_history"]):
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble-assistant">{msg["content"]}</div>', unsafe_allow_html=True)

user_query = st.text_input("Type your question:", value=st.session_state["user_query"], key="user_query_input")
st.session_state["user_query"] = user_query

if st.session_state["user_query"]:
    st.session_state["chat_history"].append({"role": "user", "content": user_query})
    st.session_state["pending_query"] = user_query

    # st.session_state["user_query"] = ""
    st.rerun()

if st.session_state["pending_query"]:
    with st.spinner("Retrieving answer..."):
        try:
            result = {"answer": "Answer"}
            # result = answer_query(
            #     st.session_state["pending_query"],
            #     st.session_state["conversation_id"],
            #     st.session_state["user_id"],
            # )
            st.session_state["chat_history"].append({"role": "assistant", "content": result["answer"]})
            st.session_state["welcome"] = False
            st.session_state["show_questions"] = False
            st.session_state["clear_input"] = True
            st.session_state["pending_query"] = ""
            st.session_state["user_query"] = ""
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")