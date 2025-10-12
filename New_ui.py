import streamlit as st
import uuid
import time
from rag_pipeline import answer_query



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

    .chat-container {{
        max-height: 70vh;  /* Adjust as needed */
        overflow-y: auto;
        padding: 10px;
        display: flex;
        flex-direction: column;
    }}

    @keyframes slideInLeft {{
        0% {{
            opacity: 0;
            transform: translateX(-40px);
        }}
        100% {{
            opacity: 1;
            transform: translateX(0);
        }}
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
        animation: slideInLeft 0.8s ease-out;
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
    left, right = st.columns([2, 1])

    with left:
        st.markdown("""
        ## 👋 *Welcome!*
        **SARA** *is your AI-powered Smart Automated Resolution Assistant for rapid incident insights, triage, and resolution support.*

        **What can you do here?**

        🔍 **Search Past Incidents:** Instantly retrieve similar incidents from historical data (root causes, recovery actions, impacted teams, resolution timelines).

        📊 **Analyze Trends:** View incidents by time period, portfolio, or other dimensions to uncover recurring issues.

        🧠 **Accelerate Triage:** Get contextual insights to speed up decision-making and reduce downtime.

        🎓 **Team Collaboration:** Identify which teams were involved in past resolutions to streamline coordination.
        """)

    with right:
        st.subheader("💡 Try any of these:")
        options = [
            "Specific Portfolio where issue is seen",
            "Issues reported in a specific time period",
            "Specific Tool/Application Issue"
        ]
        for i, opt in enumerate(options):
            if st.button(opt, key=f"option_{i}"):
                st.session_state["conversation_id"] = str(uuid.uuid4())
                st.session_state["chat_history"] = []
                st.session_state["show_questions"] = False
                st.session_state["welcome"] = False
                st.session_state["selected_option"] = opt
                st.session_state["chat_history"].append({"role": "user", "content": opt})
                st.rerun()


if "selected_option" in st.session_state and not st.session_state["show_questions"] and not st.session_state["pending_query"]:

    if st.session_state["selected_option"] == "Specific Portfolio where issue is seen":
        portfolios =["Foods", "FH&B","Customer Channels","International","Group Technology Services","HR","InfoSec","Enterprise Integration", "SAP"]
       
        portfolio_list = "<br>".join([f"• <b>{p}</b>" for p in portfolios])
        assistant_message = f"Here are some of the common portfolios:<br><br>{portfolio_list}<br><br>You can pick any of these or mention another portfolio if it is not listed here and ask incident queries related to it."
        
        st.session_state["chat_history"].append({
            "role": "assistant",
            "content": assistant_message
        })
        
        # Send this initial exchange to RAG pipeline conversation memory
        try:
            from rag_pipeline import _conversation_histories
            if st.session_state["conversation_id"] not in _conversation_histories:
                _conversation_histories[st.session_state["conversation_id"]] = []
            
            # Add both user question and assistant response to RAG memory
            _conversation_histories[st.session_state["conversation_id"]].append(f"User: {st.session_state['selected_option']}")
            # Clean the HTML for RAG memory (strip HTML tags for better context)
            clean_assistant_msg = assistant_message.replace("<br>", "\n").replace("<b>", "").replace("</b>", "")
            _conversation_histories[st.session_state["conversation_id"]].append(f"Bot: {clean_assistant_msg}")
        except ImportError:
            pass  # RAG pipeline not available yet
        
        st.session_state["selected_option"] = None
        st.rerun()
    elif st.session_state["selected_option"] == "Issues reported in a specific time period":
        periods = ["Clock Change", "Peak period", "Last Year"]
        period_list = "<br>".join([f"• <b>{p}</b>" for p in periods])
        assistant_message = f"Here are a few sample time periods you can refer to:<br><br>{period_list}<br><br>You can choose any of these or if you need some other timeline, mention that and ask further incident details."
        
        st.session_state["chat_history"].append({
            "role": "assistant",
            "content": assistant_message
        })
        
        # Send this initial exchange to RAG pipeline conversation memory
        try:
            from rag_pipeline import _conversation_histories
            if st.session_state["conversation_id"] not in _conversation_histories:
                _conversation_histories[st.session_state["conversation_id"]] = []
            
            # Add both user question and assistant response to RAG memory
            _conversation_histories[st.session_state["conversation_id"]].append(f"User: {st.session_state['selected_option']}")
            # Clean the HTML for RAG memory
            clean_assistant_msg = assistant_message.replace("<br>", "\n").replace("<b>", "").replace("</b>", "")
            _conversation_histories[st.session_state["conversation_id"]].append(f"Bot: {clean_assistant_msg}")
        except ImportError:
            pass  # RAG pipeline not available yet
        
        st.session_state["selected_option"] = None
        st.rerun()
    elif st.session_state["selected_option"] == "Specific Tool/Application Issue":
        apps = ["Relex","ControlM","WCS","JDA Dispatcher","ASO", "POS"]
        
        app_list = "<br>".join([f"• <b>{a}</b>" for a in apps])
        assistant_message = f"Here are some of the commonly handled Tools/Applications:<br><br>{app_list}<br><br>You can pick any of these or mention another portfolio if it is not listed here and ask incident queries related to it."
        
        st.session_state["chat_history"].append({
            "role": "assistant",
            "content": assistant_message
        })
        
        # Send this initial exchange to RAG pipeline conversation memory
        try:
            from rag_pipeline import _conversation_histories
            if st.session_state["conversation_id"] not in _conversation_histories:
                _conversation_histories[st.session_state["conversation_id"]] = []
            
            # Add both user question and assistant response to RAG memory
            _conversation_histories[st.session_state["conversation_id"]].append(f"User: {st.session_state['selected_option']}")
            # Clean the HTML for RAG memory
            clean_assistant_msg = assistant_message.replace("<br>", "\n").replace("<b>", "").replace("</b>", "")
            _conversation_histories[st.session_state["conversation_id"]].append(f"Bot: {clean_assistant_msg}")
        except ImportError:
            pass  # RAG pipeline not available yet
        
        st.session_state["selected_option"] = None
        st.rerun()


# --- Sidebar Home Button ---
if not st.session_state["welcome"] and not st.session_state["show_questions"]:
    with st.sidebar:
        st.title("👧🏻 SARA")
        if st.button("Go to Home", key="home_btn"):
            st.session_state["chat_history"] = []
            st.session_state["show_questions"] = True
            st.session_state["welcome"] = True
            st.rerun()

# --- Chat Container (only after welcome) ---
if not st.session_state["welcome"] and not st.session_state["show_questions"]:
    st.markdown(
        """
        <style>
        .chat-container {
            max-height: 75vh; 
            overflow-y: auto;
            padding: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div id="chat-container" class="chat-container">', unsafe_allow_html=True)
    for idx, msg in enumerate(st.session_state["chat_history"]):
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-assistant">{msg["content"]}</div>', unsafe_allow_html=True)
            # Show latency if available
            if "latency" in st.session_state and st.session_state["latency"] is not None:
                st.markdown(f"⏱️ <b>Response time:</b> {st.session_state['latency']:.2f} seconds", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- Auto scroll to bottom ---
    st.markdown(
        """
        <script>
        const chatContainer = document.getElementById('chat-container');
        if(chatContainer){
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        </script>
        """,
        unsafe_allow_html=True,
    )

# --- Hint text on welcome ---
if st.session_state["welcome"]:
    st.markdown(
        """
        <style>
        /* Disable scrolling on the welcome page */
        .css-18e3th9 {  /* Streamlit main scrollable container */
            overflow: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <style>
        @keyframes fadeIn {
            0% { opacity: 0; transform: translateY(6px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        .hint-text {
            text-align: center;
            color: #555;
            font-size: 0.95em;
            margin-bottom: 6px;
            animation: fadeIn 1.2s ease-in-out;
            font-family: 'Segoe UI', sans-serif;
        }
        </style>
        <div class='hint-text'>
            💬 If you want to ask something directly, you can type it here below 👇
        </div>
        """,
        unsafe_allow_html=True,
    )

# --- Single chat_input for both welcome and post-welcome ---
user_query = st.chat_input("Type your message...")

if user_query:
    st.session_state["welcome"] = False
    st.session_state["show_questions"] = False  
    st.session_state["chat_history"].append({"role": "user", "content": user_query})
    st.session_state["pending_query"] = user_query
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

