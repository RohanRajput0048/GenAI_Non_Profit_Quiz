import streamlit as st
import os
from dotenv import load_dotenv
from utils import get_llm_response

load_dotenv()

st.set_page_config(page_title="Non-Profit Educational Bot", page_icon="🤖")

st.title("🤖 Non-Profit Educational Bot")
st.markdown("Welcome! I am here to help you learn how to handle donor emails and scenarios.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
prompt = st.chat_input("Enter your response to the scenario or ask a question...")
if prompt:
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        # Call the backend logic
        with st.spinner("Thinking..."):
            response = get_llm_response(prompt, st.session_state.messages)
            response_placeholder.markdown(response)
            
    st.session_state.messages.append({"role": "assistant", "content": response})
