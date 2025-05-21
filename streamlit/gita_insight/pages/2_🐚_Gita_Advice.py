import streamlit as st
from Homepage import sidebar_api_key_manager
from openai_utils import ask_gita

# Sidebar for API Key Management
sidebar_api_key_manager(unique_key_suffix="chatbot")

# Initialize session state for messages and chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # Stores all past conversations

# Sidebar Chat History
with st.sidebar:
    st.title("🗂️ Chat History")
    for i, chat in enumerate(st.session_state.chat_history):
        with st.expander(f"Chat {i + 1}: {chat['title']}"):
            for message in chat["messages"]:
                role = "🧑‍💻 User" if message["role"] == "user" else "🤖 Assistant"
                st.markdown(f"**{role}:** {message['content']}")

# Chatbot Title
st.title("🕉️ Gita Chatbot")
st.markdown("Engage in a conversation with the Bhagavad Gita for spiritual and practical guidance.")

# Display chat history in the main container
with st.container():
    chat_history = st.empty()  # Placeholder for chat history
    with chat_history.container():
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

# Chat input fixed at the bottom
if user_input := st.chat_input("Ask the Gita for guidance..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate and display Gita's response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()  # Placeholder for the streaming response
        full_response = ""  # To accumulate the full response

        with st.spinner("Seeking wisdom from the Gita..."):
            if not st.session_state.get("saved_api_key"):
                response = "🔐 Please enter and save your OpenAI API key in the sidebar."
                response_placeholder.markdown(response)
                full_response = response
            else:
                # Stream the response in chunks
                for chunk in ask_gita(user_input, api_key=st.session_state.saved_api_key):
                    full_response += chunk
                    response_placeholder.markdown(full_response)  # Update the response dynamically

        # Add assistant message to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Save the conversation to chat history when the session ends
if st.button("💾 Save Conversation"):
    if st.session_state.messages:
        # Generate a title for the conversation based on the first user input
        title = st.session_state.messages[0]["content"][:30] + "..." if len(st.session_state.messages[0]["content"]) > 30 else st.session_state.messages[0]["content"]
        st.session_state.chat_history.append({"title": title, "messages": st.session_state.messages.copy()})
        st.session_state.messages = []  # Clear the current conversation
        st.success("Conversation saved to history!")