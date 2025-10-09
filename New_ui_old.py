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


# Sticky Title Container
# st.markdown(
#     """
#     <style>
#     .sticky-title {
#         position: fixed;
#         top: 56px; /* below Streamlit header */
#         left: 0;
#         width: 100vw;
#         z-index: 9999;
#         background: #ffffff;
#         border-bottom: 1.5px solid #ffffff;
#         padding: 12px 0 8px 0;
#         text-align: center;
#         font-size: 1.7em;
#         font-weight: 700;
#         color: #222;
#         box-shadow: 0 4px 24px rgba(0,0,0,0.10);
#         font-family: 'Segoe UI', sans-serif;
#     }
#     .stApp { padding-top: 100px !important; }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )
# st.markdown('<div class="sticky-title">Smart Automated Resolution Assistant</div>', unsafe_allow_html=True)

# import base64

# # Path to your local image
# image_path = IMG  # Change to your image file

# # Encode image to base64
# with open(image_path, "rb") as img_file:
#     encoded = base64.b64encode(img_file.read()).decode()
#         background-image: url('data:image/jpg;base64,{encoded}');
#         background-size: cover;
#         background-position: center center;
#         background-repeat: no-repeat;
#         background-attachment: fixed;
#         font-family: 'Segoe UI', sans-serif;


st.markdown(
    f"""
    <style>
    :root {{
        --primary-color: slateBlue;
        --background-color: #F7F7F7;
        --secondary-background-color: darkSeaGreen;
        --base-radius-right: 16px 16px 2px 16px;
        --base-radius-left: 16px 16px 16px 2px;
    }}

    body, .stApp {{
        background-color: var(--background-color);
        font-family: 'Segoe UI', sans-serif;
        

    }}

    .new-chat-btn {{
        float: right;
        margin-top: 10px;
        margin-right: 24px;
        margin-bottom: 18px;
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
        border-color: rgba(72, 61, 139, 0.35);
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
if "text_input" not in st.session_state:
    st.session_state["text_input"] = False
    

# --- Welcome Message ---

if st.session_state["welcome"]:
    st.markdown("""
    ## 👋 *Welcome!*
    *SARA is your AI-powered Smart Automated Resolution Assistant for rapid incident insights, triage, and resolution support.*


    **What can you do here?**
    - Instantly get the status of any incident.
    - Find out which teams or services are affected.
    - Ask about recent, trending, or resolved incidents.

    """)



# --- Predefined Question Cards ---
pending = bool(st.session_state.get("pending_query"))
if st.session_state["show_questions"]:
# and not st.session_state["chat_history"]:
    st.subheader("💡 Try asking:")
    predefined_questions = [
        "Specific portfolio-based issue",
        "Show me today's critical incidents",
        "I am facing NDC allocation issues. What do I do?",
        "Donnington ecomm order fulfillment issue. What are the possible root causes?"
    ]

    cols = st.columns(len(predefined_questions))
    for i, q in enumerate(predefined_questions):
        if cols[i].button(q, key=f"pre_q_{i}"):
            # Same flow as user input
            st.session_state["conversation_id"] = str(uuid.uuid4())
            st.session_state["chat_history"] = []
            st.session_state["show_questions"] = False
            st.session_state["welcome"] = False
           
            st.session_state["user_query"] = q
            st.session_state["pending_query"] = q
            # st.session_state["welcome"] = False
            st.session_state["chat_history"].append({"role": "user", "content": q})
            st.rerun()

# --- New Chat Button  ---

if not st.session_state["welcome"] and not st.session_state["show_questions"]:

    home_clicked = st.button("🏠 Home", key="home_btn", help="Go to home screen", use_container_width=False, disabled=pending)
    if home_clicked:
        st.session_state["chat_history"] = []
        st.session_state["show_questions"] = True
        st.session_state["welcome"] = True
        st.rerun()


new_chat_clicked = st.button("New Chat", key="new_chat_btn", help="Start a new conversation", use_container_width=False, disabled=pending)
if new_chat_clicked:
    st.session_state["conversation_id"] = str(uuid.uuid4())
    st.session_state["chat_history"] = []
    st.session_state["show_questions"] = False
    st.session_state["welcome"] = False
    # st.session_state["sources_history"] = []
    # st.session_state["latency"] = None
    # st.session_state["user_query"] = ""
    # st.session_state["pending_query"] = ""
    st.session_state["chat_history"].append({"role": "assistant", "content": "Hi! I'm Sara, your triaging assistant. How can i help you?"})
    st.rerun()

# --- Chat History ---
for idx, msg in enumerate(st.session_state["chat_history"]):
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble-assistant">{msg["content"]}</div>', unsafe_allow_html=True)
        # --- Retrieved chunks display is commented out ---
        # # --- Show retrieved chunks and sources for this assistant response ---
        # # Find the corresponding result if available
        # # We'll use sources_history to store the chunks for each assistant response
        # ai_idx = [i for i, m in enumerate(st.session_state["chat_history"][:idx+1]) if m["role"] == "assistant"]
        # if "sources_history" in st.session_state and ai_idx:
        #     # Map assistant message index to sources_history index
        #     src_idx = len(ai_idx) - 1
        #     if src_idx < len(st.session_state["sources_history"]):
        #         chunks = st.session_state["sources_history"][src_idx]
        #         if chunks and len(chunks) > 0:
        #             sources_html = ""
        #             for chunk in chunks:
        #                 sheet = chunk.get("sheet")
        #                 row = chunk.get("row")
        #                 dist = chunk.get("distance")
        #                 text = chunk.get("text", "")[:120]
        #                 sources_html += f'<div>`{sheet}` | Row: `{row}` | Distance: `{dist:.4f}`<br>Text: {text}...</div><hr style="margin:2px 0">'
        #             st.markdown(f'<div class="sources-bubble"><b>Retrieved Chunks:</b><br>{sources_html}</div>', unsafe_allow_html=True)
        #         else:
        #             st.markdown(f'<div class="sources-bubble">No retrieved chunks for this response.</div>', unsafe_allow_html=True)
        # # Show latency if available
        if "latency" in st.session_state and st.session_state["latency"] is not None:
            st.markdown(f"⏱️ <b>Response time:</b> {st.session_state['latency']:.2f} seconds", unsafe_allow_html=True)

# if st.session_state.get("latency") is not None:
#     st.markdown(f"⏱️ **Response time:** {st.session_state['latency']:.2f} seconds")

# --- Sticky Input (chat_input is auto-fixed at bottom) ---
if not st.session_state["welcome"] and not st.session_state["show_questions"]:
    user_query = st.chat_input("Type your message...")

    if user_query:
        # Step 1: Add user query immediately
        
        st.session_state["welcome"] = False
        st.session_state["show_questions"] = False  
        st.session_state["chat_history"].append({"role": "user", "content": user_query})
        
        st.session_state["pending_query"] = user_query
        # result = {"answer": "Answer"}   
        
        st.rerun()




# --- Pending Query Processing ---
if st.session_state["pending_query"]:
    import time
    # time.sleep(2)  # Delay before showing the message
    st.markdown(f'<div class="chat-bubble-assistant">{"Retrieving answer..."}</div>', unsafe_allow_html=True)
    try:
        result = answer_query(
                        st.session_state["pending_query"],
                        st.session_state["conversation_id"],
                        st.session_state["user_id"],
                    )
        # Store chunks for this response for debug display
        if "sources_history" not in st.session_state:
            st.session_state["sources_history"] = []
        st.session_state["sources_history"].append(result.get("chunks", []))
        st.session_state["latency"] = result.get("latency")
        st.session_state["chat_history"].append({"role": "assistant", "content": result["answer"]})
        st.session_state["pending_query"] = ""  # clear
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")
