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
    **SARA** *is your AI-powered Smart Automated Resolution Assistant for rapid incident insights, triage, and resolution support.*

    **What can you do here?**

    🔍**Search Past Incidents:** Instantly retrieve similar incidents from historical data root causes, recovery actions, impacted teams, and resolution timelines.

    📊**Analyze Trends:** View incidents by time period, portfolio, or other dimensions to uncover patterns and recurring issues.

    🧠**Accelerate Triage:** Get contextual insights to speed up decision-making and reduce downtime.

    🎓**Team Collaboration:** Identify which teams were involved in past resolutions to streamline coordination.
    """)




# --- Option Cards ---
import pandas as pd
import os
pending = bool(st.session_state.get("pending_query"))
if st.session_state["show_questions"]:
    st.subheader("💡 Select an option:")
    options = [
        "Specific Portfolio where issue is seen",
        "Issues reported in a specific time period",
        "Specific Tool/Application Issue"
    ]
    cols = st.columns(len(options))
    for i, opt in enumerate(options):
        if cols[i].button(opt, key=f"option_{i}"):
            st.session_state["conversation_id"] = str(uuid.uuid4())
            st.session_state["chat_history"] = []
            st.session_state["show_questions"] = False
            st.session_state["welcome"] = False
            st.session_state["selected_option"] = opt
            st.session_state["chat_history"].append({"role":"user","content": opt})
            st.rerun()

# --- Option Handling ---
if "selected_option" in st.session_state and not st.session_state["show_questions"] and not st.session_state["pending_query"]:
    excel_path = os.path.join("data", "Major Significant & Key Incidents KB-2.xlsx")
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        st.error(f"Error loading Excel: {e}")
        df = None

    if st.session_state["selected_option"] == "Specific Portfolio where issue is seen" and df is not None:
        portfolios = (
            df["Product Portfolio -Area of cause"]
            .dropna()
            .astype(str)
            .str.strip()
            .str.lower()
            .replace(["none", "nill", "nil", "nan"], "")
            .unique()
        )
        portfolios = sorted(set([p.title() for p in portfolios if p]))
        portfolio_list = "<br>".join([f"• <b>{p}</b>" for p in portfolios])
        st.session_state["chat_history"].append({
            "role": "assistant",
            "content": f"These are all the portfolios available:<br><br>{portfolio_list}<br><br>You can choose any of these portfolios and ask incident queries related to it."
        })
        st.session_state["selected_option"] = None
        st.rerun()
    elif st.session_state["selected_option"] == "Issues reported in a specific time period":
        periods = ["Clock Change", "Peak", "Last Year", "MMYY to MMYY"]
        st.session_state["chat_history"].append({
            "role": "assistant",
            "content": "Please select a time period:<br><br>" + ", ".join([f"<b>{p}</b>" for p in periods]) + "<br><br>After selecting, please provide further details about the issue."
        })
        st.session_state["selected_option"] = None
        st.rerun()
    elif st.session_state["selected_option"] == "Specific Tool/Application Issue" and df is not None:
        apps = (
            df["Application/Service Impacted?"]
            .dropna()
            .astype(str)
            .str.strip()
            .str.lower()
            .replace(["none", "nill", "nil", "nan"], "")
            .unique()
        )
        apps = sorted(set([a.title() for a in apps if a]))
        app_list = "<br>".join([f"• <b>{a}</b>" for a in apps])
        st.session_state["chat_history"].append({
            "role": "assistant",
            "content": f"Please select an application/service from the following list:<br><br>{app_list}<br><br>After selecting, please provide further details about the issue."
        })
        st.session_state["selected_option"] = None
        st.rerun()

# --- New Chat Button  ---

if not st.session_state["welcome"] and not st.session_state["show_questions"]:

    home_clicked = st.button("🏠 Home", key="home_btn", help="Go to home screen", use_container_width=False, disabled=pending)
    if home_clicked:
        st.session_state["chat_history"] = []
        st.session_state["show_questions"] = True
        st.session_state["welcome"] = True
        st.rerun()

if not st.session_state["welcome"]:
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
# if not st.session_state["welcome"] and not st.session_state["show_questions"]:


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
# ...existing code...

if st.session_state["pending_query"]:
    import time
    user_text = st.session_state["pending_query"].strip().lower()
    # Add more phrases as needed
    polite_phrases = ["thank you", "thanks", "ok", "okay", "thx", "ty", "thank u"]

    if any(phrase in user_text for phrase in polite_phrases):
        st.session_state["chat_history"].append({
            "role": "assistant",
            "content": "You're welcome! Please notify me if you need my help further."
        })
        st.session_state["pending_query"] = ""
        # st.session_state["latency"] = None
        st.rerun()
    else:
        import time
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
