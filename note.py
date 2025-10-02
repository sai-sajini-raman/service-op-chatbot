
# --- Chat rendering with inline spinner ---
with st.container():
    st.markdown("<div class='scrollable-chat' style='height:65vh; overflow-y:auto; margin-bottom:80px;'>", unsafe_allow_html=True)
    chat_len = len(st.session_state.get("chat_history", []))
    for idx, msg in enumerate(st.session_state.get("chat_history", [])):
        if msg["role"] == "assistant":
            st.markdown(f'<div class="chat-bubble-left">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-right">{msg["content"]}</div>', unsafe_allow_html=True)
            # Only show spinner after last user bubble, if pending_query is set
            if (
                idx == chat_len - 1
                and st.session_state.get("pending_query")
            ):
                st.markdown(
                    '<div class="chat-bubble-left" style="opacity:0.7;"><i>Retrieving answer...</i></div>',
                    unsafe_allow_html=True
                )
        st.markdown('<div style="clear:both;"></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)    