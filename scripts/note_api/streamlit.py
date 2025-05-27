import streamlit as st
import requests
API_URL = "http://127.0.0.1:3000"

st.set_page_config(page_title="Note Taking App", layout="wide")
st.title("📝 Note Taking App")


tab1, tab2, tab3 = st.tabs(["Create Note", "Delete Note", "Update Note"])

with tab1:  
    st.subheader("➕ Add New Note")
    title = st.text_input("Title")
    content = st.text_area("Content")
    tags = st.text_input("Tags (optional)")
    if st.button("Create Note"):
        payload = {"title": title, "content": content, "tags": tags}
        response = requests.post(f"{API_URL}/notes/", json=payload)
        if response.status_code == 201:
            st.success("✅ Note created successfully!")
        else:
            st.error("❌ Failed to create note.")
            print(f"Error: {response.status_code} - {response.text}")

with tab2:
    st.subheader("Delete Note")
    delete_note_id = st.number_input("Enter Note ID to delete", min_value=1, step=1, key="delete_note_id")
    if st.button("Delete Note"):   
        response = requests.delete(f"{API_URL}/notes/{delete_note_id}")
        if response.status_code in (200, 204):
            st.success("✅ Note deleted successfully!")
        else:
            st.error(f"❌ Failed to delete note")
            print(f"Error: {response.status_code} - {response.text}")

with tab3:
    st.subheader("Update Note")
    update_note_id = st.number_input("Enter Note ID to update", min_value=1, step=1, key="update_note_id")
    new_title = st.text_input("New Title")
    new_content = st.text_area("New Content")
    new_tags = st.text_input("New Tags (optional)")
    if st.button("Update Note"):  
        payload = {"title": new_title, "content": new_content, "tags": new_tags}
        response = requests.put(f"{API_URL}/notes/{update_note_id}", json=payload)
        if response.status_code == 200:
            st.success("✅ Note updated successfully!")
        else:
            st.error("❌ Failed to update note.")

with st.sidebar:
    response = requests.get(f"{API_URL}/notes/")
    if response.status_code == 200:
        notes = response.json()
        if notes:
            st.sidebar.subheader("Notes List")
        for note in notes:
            with st.expander(note["title"]):
                st.markdown(f"**ID:** {note['id']}")
                st.markdown(f"**Content:** {note['content']}")
                st.markdown(f"**Tags:** {note.get('tags', '')}")
                st.caption(f"🕒 Created: {note['created_at']}")
                st.caption(f"🛠 Updated: {note['updated_at']}")
    else:
        st.error("❌ Unable to fetch notes.")
