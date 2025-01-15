import streamlit as st  # Importing Streamlit library for creating UI
st.set_page_config(page_title= "Counter App", layout="centered",page_icon="⏱️")  # Setting the page title and layout

# Title of the app
st.title("Professional Counter App")
st.markdown("A simple and elegant counter application.")

# Initialize the counter & History 
if 'counter' not in st.session_state:
    st.session_state.counter = 0
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
    st.session_state.history[action].append(f"{action}: {st.session_state.counter}")

# Columns for buttons
st.write("### Actions")
col1, col2, col3 = st.columns([1, 1, 1])  

with col1:
    # Increment button
    if st.button("🔼 Increment"):
        st.session_state.counter += 1
        update_history("Increment")

with col2:
    # Decrement button
    if st.button("🔽 Decrement"):
        st.session_state.counter -= 1
        update_history("Decrement")

with col3:
    # Reset button
    if st.button("🔄 Reset Counter"):
        st.session_state.counter = 0
        update_history("Reset")

# History of actions
st.subheader("Action History")
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    #Increment History
    st.write("Increment")
    for action in st.session_state.history["Increment"]:
        st.write(action)

with col2:
    #Decrement History
    st.write("Decrement")
    for action in st.session_state.history["Decrement"]:
        st.write(action)

with col3:
    #Reset History
    st.write("Reset")
    for action in st.session_state.history["Reset"]:
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

