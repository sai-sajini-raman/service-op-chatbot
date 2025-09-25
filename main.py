# main.py
import streamlit as st
from rag_pipeline import answer_query
from config import EXCEL_PATH
import os

st.set_page_config(page_title="RAG Chatbot - POC", layout="wide")
st.title("RAG Chatbot (POC)")

if not os.path.exists(EXCEL_PATH):
    st.error(f"Excel file not found: {EXCEL_PATH}")
    st.stop()


if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "sources" not in st.session_state:
    st.session_state["sources"] = []
if "user_query" not in st.session_state:
    st.session_state["user_query"] = ""


#--------- Streamlit Form for robust input handling ---------
with st.form(key="chat_form"):
    query = st.text_input("Type your question:", value=st.session_state["user_query"], key="user_query")
    submitted = st.form_submit_button("Send")
    if submitted and query:
        with st.spinner("Retrieving answer..."):
            result = None
            error = None
            try:
                result = answer_query(query)
                st.session_state["chat_history"].append({"user": query, "bot": result["answer"]})
                st.session_state["sources"] = result["chunks"]
                st.session_state["latency"] = result["latency"]
                # Do not clear the input field here to avoid session state error
            except Exception as e:
                error = e
            #--------- DEBUG: Show retrieved chunks structure in sidebar ---------
            #--------- DEBUG: Show all candidate chunks ---------
            st.sidebar.subheader("[DEBUG] All Candidate Chunks")
            if result is not None:
                chunks_val = result.get("chunks", None)
                st.sidebar.write(f"chunks value: {chunks_val}")
                st.sidebar.write(f"Type: {type(chunks_val)}")
                if chunks_val is not None and hasattr(chunks_val, "__len__") and len(chunks_val) > 0:
                    for idx, item in enumerate(chunks_val):
                        st.sidebar.write(f"Candidate {idx}: {item}")
            if error is not None:
                st.sidebar.error(f"Error: {error}")
            #--------- END DEBUG ---------
            #--------- END DEBUG ---------
#--------- END Streamlit Form ---------

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Chat History")
    for chat in reversed(st.session_state["chat_history"]):
        st.markdown(f"**User:** {chat['user']}")
        st.markdown(f"**Bot:** {chat['bot']}")
        st.markdown("---")

with col2:
    st.subheader("Retrieved Sources & Latency")
    sources = st.session_state.get("sources", [])
    if sources and len(sources) > 0:
        for chunk in sources:
            dist = chunk.get("distance")
            st.markdown(f"Sheet: `{chunk.get('sheet')}` | Row: `{chunk.get('row')}` | Score: `{dist:.4f}`" if dist is not None else "Score: N/A")
            st.markdown(f"Text: {chunk.get('text', '')[:100]}...")
            st.markdown("---")
    else:
        st.info("No relevant sources found for your query.")
    if st.session_state.get("latency"):
        st.markdown(f"**Latency:** {st.session_state['latency']:.2f} seconds")
