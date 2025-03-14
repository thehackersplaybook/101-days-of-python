import streamlit as st

st.title("📕 Book Tracker")
st.write("Welcome to the Book Tracker!")

# Initialize session state
if "books" not in st.session_state:
    st.session_state.books = []

books = st.session_state.books

# Sidebar form for adding books
st.sidebar.header("📖 Add a book")

title = st.sidebar.text_input("🔖 Title")
author = st.sidebar.text_input("✒️ Author")
status = st.sidebar.selectbox("Status", ["Reading", "Finished", "To Read"])

if st.sidebar.button("Add Book"):
    if title and author and status:
        st.session_state.books.append({"title": title, "author": author, "status": status})
        st.sidebar.success(f"Added {title} by {author} ({status})")
    else:
        st.sidebar.error("⚠️ Please fill in all fields")

# Main section
st.subheader("📚 Your Books")
search_query = st.text_input("Search by title or author").lower()

# Filter by status
filter_status = st.selectbox("Filter by Status", ["All", "To-Read", "Reading", "Finished"])

# Filter and search logic
filtered_books = [
    book for book in books
    if search_query in book["title"].lower() or search_query in book["author"].lower()
]
if filter_status != "All":
    filtered_books = [book for book in filtered_books if book["status"] == filter_status]

# Status color mapping
status_colors = {
    "Reading": "#6c757d",
    "Finished": "#28a745",  
    "To Read": "#996515"  
}

# Display books with red background for the book cards
if filtered_books:
    for book in filtered_books:
        st.markdown(
            f"""
            <div style="
                border: 1px;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 12px;
                box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
                background-color: #262730;
                font-family: Arial, sans-serif;
            ">
                <h4 style="margin-bottom: 5px; font-weight: 600; color: #e6e6e6;">📖 {book['title']}</h4>
                <p style="margin: 0; font-style: italic; color: #e6e6e6;">✒️ {book['author']}</p>
                <span style="
                    display: inline-block;
                    padding: 4px 10px;
                    border-radius: 20px;
                    background-color: {status_colors.get(book['status'], '#ccc')};
                    color: #e6e6e6;
                    font-size: 0.9em;
                    margin-top: 8px;
                    font-weight: 500;
                    letter-spacing: 0.5px;
                ">
                    {book['status']}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    st.info("No books found.")