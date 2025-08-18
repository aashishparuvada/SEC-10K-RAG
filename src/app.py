import streamlit as st
from agent_runner import make_agent, ask

# Initialise agent once
if "agent" not in st.session_state:
    st.session_state.agent = make_agent()
    st.session_state.chat_history = []

st.set_page_config(page_title="SEC 10-K RAG Agent", page_icon="📊", layout="wide")

st.title("📊 SEC 10-K RAG Agent")
st.caption("Ask financial questions about Google, Microsoft, NVIDIA (2022-2024)")

# Display chat history
for chat in st.session_state.chat_history:
    role, msg = chat
    with st.chat_message(role):
        st.markdown(msg)

# Chat input
if prompt := st.chat_input("Ask a financial question..."):
    # Show user message
    st.session_state.chat_history.append(("user", prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    # Run agent
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result_json = ask(st.session_state.agent, prompt)
            
            # Parse JSON and display nicely
            try:
                import json
                result = json.loads(result_json)
                
                # Display the main answer
                st.write("**Answer:**")
                st.write(result.get("answer", "No answer provided"))
                
                # Show reasoning if available
                if result.get("reasoning"):
                    st.write("**Reasoning:**")
                    st.write(result.get("reasoning"))
                
                # Show sources if available
                if result.get("sources"):
                    st.write("**Sources:**")
                    for i, source in enumerate(result["sources"], 1):
                        st.write(f"{i}. **{source.get('ticker', 'Unknown')} {source.get('year', 'Unknown')}** (Page {source.get('page', 'Unknown')})")
                        if source.get("excerpt"):
                            st.write(f"   *{source['excerpt'][:200]}...*")
                
                # Expandable section for full JSON
                with st.expander("Show full JSON response"):
                    st.json(result)
                    
                formatted_response = f"**Answer:** {result.get('answer', 'No answer provided')}"
                
            except json.JSONDecodeError:
                # Fallback for non-JSON responses
                st.markdown(result_json)
                formatted_response = result_json

    # Store assistant reply
    st.session_state.chat_history.append(("assistant", formatted_response))
