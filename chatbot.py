import streamlit as st
import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page configuration for Streamlit
st.set_page_config(page_title="Chatbot with OpenAI", layout="wide", page_icon="🤖")

# Fetch OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")


# Page title and description
st.title("AI Chatbot")
st.markdown("## Welcome to the AI Chatbot! 🤖")

# Sidebar settings for model selection
st.sidebar.header("Settings")
model = st.sidebar.selectbox("Choose a model", ["gpt-4", "gpt-3.5-turbo"])

# Text input for user message
user_input = st.text_input("You:", placeholder="Type your message here...")

# Initialize chat session if not already
if 'messages' not in st.session_state:
    st.session_state['messages'] = [{"role": "system", "content": "You are a helpful assistant."}]

# Handle sending the message
if st.button('Send'):
    st.session_state['messages'].append({'role': 'user', 'content': user_input})

    try:
        # Fetch response from OpenAI API
        response = openai.ChatCompletion.create(
            model=model,
            messages=st.session_state['messages']
        )
        
        # Extract assistant's reply
        reply = response['choices'][0]['message']['content']
        
        # Append the assistant's reply to the conversation history
        st.session_state['messages'].append({'role': 'assistant', 'content': reply})
    except Exception as e:
        st.error(f"Error {e}")

# Display chat messages
for message in st.session_state['messages']:
    if message['role'] == 'user':
        st.markdown(f'###### **You**: {message["content"]}')
    elif message['role'] == 'assistant':
        st.markdown(f'###### **Bot**: {message["content"]}')

# Clear chat button
if len(st.session_state['messages']) > 1:
    if st.button('Clear Chat'):
        st.session_state['messages'] = [{"role": "system", "content": "You are a helpful assistant."}]

# Footer 
st.markdown(
        """
        <style>
        .bottom-right {
            position: fixed;
            bottom: 10px;
            right: 15px;
            font-size: 0.9em;
            color: gray;
        }
        </style>
        <div class="bottom-right">
            Made with ⚡ at 'The Hackers Playbook' ©. All rights reserved.
        </div>
        """,
        unsafe_allow_html=True
                )
