import streamlit as st
import uuid
from rag_pipeline import answer_query

st.set_page_config(page_title="Major Incident Triaging Agent", layout="wide")
st.title("Major Incident Triaging Chatbot")
st.markdown(
    """
    <style>
    .new-chat-btn {
        position: absolute;
        top: 12px;
        left: 12px;
        z-index: 999;
    }
    .scrollable-chat {
        max-height: 65vh;
        overflow-y: auto;
        margin-bottom: 130px;
    }
    .chat-bubble-left {
        background-color: #f1f0f0;
        color: #222;
        border-radius: 16px 16px 16px 2px;
        padding: 10px 16px;
        margin-bottom: 4px;
        max-width: 70%;
        display: inline-block;
        word-break: break-word;
    }
    .chat-bubble-right {
        background-color: #0078FF;
        color: #fff;
        border-radius: 16px 16px 2px 16px;
        padding: 10px 16px;
        margin-bottom: 4px;
        max-width: 70%;
        display: inline-block;
        float: right;
        word-break: break-word;
    }
    .sources-bubble {
        background-color: #e0edff;
        color: #222;
        border-radius: 0px 0px 16px 16px;
        padding: 8px 16px;
        margin-bottom: 10px;
        max-width: 70%;
        display: inline-block;
        font-size: 0.95em;
        word-break: break-word;
    }
    .fixed-bottom-input {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100vw;
        background: #fff;
        padding: 16px 0 12px 0;
        z-index: 100;
        border-top: 1px solid #eee;
        box-shadow: 0px -4px 10px rgba(0,0,0,0.04);
    }
    .input-container {
        display: flex;
        align-items: center;
        max-width: 700px;
        margin: 0 auto;
        width: 90vw;
    }
    .input-field {
        flex: 1;
        padding: 10px 16px;
        font-size: 1.1em;
        border-radius: 16px;
        border: 1px solid #ccc;
        outline: none;
    }
    .send-btn {
        background: none;
        border: none;
        cursor: pointer;
        margin-left: 8px;
        font-size: 1.7em;
        color: #0078FF;
        transition: color 0.2s;
    }
    .send-btn:active {
        color: #0056b3;
    }

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

# st.title("💬 Major Incident Triaging Agent Chatbot")

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

# --- New Chat Button Top-Left ---
new_chat_clicked = st.button("🗑️ New Chat", key="new_chat_btn", help="Start a new conversation", use_container_width=False)
if new_chat_clicked:
    st.session_state["conversation_id"] = str(uuid.uuid4())
    st.session_state["chat_history"] = []  # Clear chat history
    st.session_state["sources_history"] = []
    st.session_state["latency"] = None
    st.session_state["user_query"] = ""
    st.session_state["pending_query"] = ""
    st.session_state["clear_input"] = True
    st.session_state["show_questions"] = True
    st.rerun()  # <-- This reruns so the cleared chat appears immediately

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

# --- Conversation Chat Bubbles in Scrollable Container ---
st.markdown("<div class='scrollable-chat'>", unsafe_allow_html=True)
for idx, msg in enumerate(st.session_state["chat_history"]):
    if msg["role"] == "assistant":
        st.markdown(
            f'<div class="chat-bubble-left">{msg["content"]}</div>',
            unsafe_allow_html=True,
        )
        # Show sources bubble for the bot message
        # if len(st.session_state["sources_history"]) > idx // 2:
        #     sources = st.session_state["sources_history"][idx // 2]
        #     if sources and len(sources) > 0:
        #         sources_html = ""
        #         for chunk in sources:
        #             sheet = chunk.get("sheet")
        #             row = chunk.get("row")
        #             dist = chunk.get("distance")
        #             text = chunk.get("text", "")[:100]
        #             sources_html += f'<div>`{sheet}` | Row: `{row}` | Distance: `{dist:.4f}`<br>Text: {text}...</div><hr style="margin:2px 0">'
        #         st.markdown(
        #             f'<div class="sources-bubble">{sources_html}</div>',
        #             unsafe_allow_html=True,
        #         )
    else:
        st.markdown(
            f'<div class="chat-bubble-right">{msg["content"]}</div>',
            unsafe_allow_html=True,
        )
    st.markdown('<div style="clear:both;"></div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# if st.session_state.get("latency") is not None:
#     st.markdown(f"**Response time:** {st.session_state['latency']:.2f} seconds")


def send_message():
    user_query = st.session_state.get("user_query", "")
    if user_query:
        with st.spinner("Retrieving answer..."):
            try:
                # result = "answer"
                # st.session_state["pending_query"] = user_query
                result = answer_query(
                    user_query,
                    st.session_state["conversation_id"],
                    st.session_state["user_id"],
                )
                st.session_state["chat_history"].append({"role": "user", "content": user_query})
                st.session_state["chat_history"].append({"role": "assistant", "content": result["answer"]})
                st.session_state["sources_history"].append(result["chunks"])
                st.session_state["latency"] = result["latency"]
                st.session_state["user_query"] = ""  # Clear input after sending
                st.session_state["clear_input"] = True  # Set flag to clear input box
            except Exception as e:
                st.session_state["user_query"] = ""  # Ensure input is cleared on error
                st.session_state["clear_input"] = True
                st.error(f"Error: {e}")

# --- Input field at bottom ---
input_placeholder = st.empty()
with input_placeholder.container():
    st.markdown('<div class="fixed-bottom-input">', unsafe_allow_html=True)
    col1, col2 = st.columns([12, 1])

    col1.text_input(
        "Type your message...",
        key="user_query",
        label_visibility="collapsed",
        placeholder="Ask your question...",
        on_change=send_message
    )
    col2.button("➤", key="send_btn", help="Send your message", on_click=send_message)
    st.markdown('</div>', unsafe_allow_html=True)

