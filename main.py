# main.py
import streamlit as st
from rag_pipeline import answer_query

import os
import uuid

if "conversation_id" not in st.session_state:
    st.session_state["conversation_id"] = str(uuid.uuid4())
if "user_id" not in st.session_state:
    st.session_state["user_id"] = f"user_{str(uuid.uuid4())[:8]}"
st.set_page_config(page_title="Major Incident Triaging Agent - POC", layout="wide")
st.title("Major Incident Triaging Agent (POC)")

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
                result = answer_query(query,st.session_state["conversation_id"], st.session_state["user_id"])
                st.session_state["chat_history"].append({"user": query, "bot": result["answer"]})
                st.session_state["sources"] = result["chunks"]
                st.session_state["latency"] = result["latency"]
                # Do not clear the input field here to avoid session state error
            except Exception as e:
                error = e
            

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Response")
    for chat in reversed(st.session_state["chat_history"]):

        st.markdown(f"**Bot:** \n{chat['bot']}")
        st.markdown("---")

with col2:
    st.subheader(" ")
    # st.subheader("Retrieved Sources")
    # sources = st.session_state.get("sources", [])
    # if sources and len(sources) > 0:
    #     for chunk in sources:
    #         sheet = chunk.get("sheet")
    #         row = chunk.get("row")
    #         dist = chunk.get("distance")
    #         if dist is not None:
    #             st.markdown(f"`{sheet}` | Row: `{row}` | Distance: `{dist:.4f}`")
    #         else:
    #             st.markdown(f"`{sheet}` | Row: `{row}` | Distance: N/A")
    #         st.markdown(f"Text: {chunk.get('text', '')[:100]}...")
    #         st.markdown("---")
    # else:
    #     st.info("No relevant sources as of now.")
    # if st.session_state.get("latency"):
    #     st.markdown(f"**Latency:** {st.session_state['latency']:.2f} seconds")
