import streamlit as st  # Importing Streamlit library for creating UI
st.set_page_config(page_title= "Counter App", layout="centered",page_icon="⏱️")  # Setting the page title and layout

# Title of the app
st.title("Professional Counter App")
st.markdown("A simple and elegant counter application.")

# Initialize the counter & History 
if 'counter' not in st.session_state:
    st.session_state.counter = 0
if 'history' not in st.session_state:
    st.session_state.history = {
        "Increment" : [],
        "Decrement" : [],
        "Reset" : []
    }

st.write("### Current Count")
# Display the current counter value
st.metric(label="Counter", value=st.session_state.counter)

# Update the history
def update_history(action):
    """
    Function to update the history of actions
    Args:
        action (str): The action performed
    Returns:
        None
        """
    st.session_state.history[action].append(f"{action}: {st.session_state.counter}")

# Function to increment counter
def increment_counter():
    """
    Function to increment the counter.
    Args:
        None
    Returns:
        None
    """
    st.session_state.counter += 1
    update_history("Increment")

# Function to decrement counter
def decrement_counter():
    """
    Function to decrement the counter.
    Args:
        None
    Returns:
        None
    """
    st.session_state.counter -= 1
    update_history("Decrement")

# Function to reset counter
def reset_counter():
    """
    Function to reset the counter to 0
    Args:
        None
    Returns:
        None
    """
    st.session_state.counter = 0
    update_history("Reset")


# Columns for buttons
st.write("### Actions")
col1, col2, col3 = st.columns([1, 1, 1])  

with col1:
    # Increment button
    st.button("🔼 Increment", on_click=increment_counter)

with col2:
    # Decrement button
    st.button("🔽 Decrement", on_click=decrement_counter)
with col3:
    # Reset button
    st.button("🔄 Reset Counter", on_click=reset_counter)

# History of actions
st.subheader("Action History")
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    #Increment History
    st.write("Increment")
    if st.session_state.history["Increment"]:
        for action in reversed(st.session_state.history["Increment"][-5:]):  # Show only last 5 entries
            st.write(action)

with col2:
    #Decrement History
    st.write("Decrement")
    if st.session_state.history["Decrement"]:
        for action in reversed(st.session_state.history["Decrement"][-5:]):  # Show only last 5 entries
            st.write(action)

with col3:
    #Reset History
    st.write("Reset")
    if st.session_state.history["Reset"]:
        for action in reversed(st.session_state.history["Reset"][-5:]):  # Show only last 5 entries
            st.write(action)

#Footer
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

