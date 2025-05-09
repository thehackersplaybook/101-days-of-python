import streamlit as st
from typing import List, Dict

def initialize_session_state() -> None:
    """
    Initializes the session state for storing books.
    """
    if "books" not in st.session_state:
        st.session_state.books = []

def add_book(title: str, author: str, status: str) -> None:
    """
    Adds a book to the session state if all fields are filled.

    Args:
        title (str): The title of the book.
        author (str): The author of the book.
        status (str): The status of the book.

Returns:        
        None
    
    Args:
        title (str): The title of the book.
        author (str): The author of the book.
        status (str): The status of the book.

Returns:        
        None
    
    Args:
        title (str): The title of the book.
        author (str): The author of the book.
        status (str): The status of the book.

Returns:        
        None
    
    Args:
        title (str): The title of the book.
        author (str): The author of the book.
        status (str): The status of the book.

Returns:        
        None
    
    Args:
        title (str): The title of the book.
        author (str): The author of the book.
        status (str): The status of the book.

Returns:        
        None
    
    Args:
        title (str): The title of the book.
        author (str): The author of the book.
        status (str): The status of the book.

    Returns:        
        None
    """
    if title and author and status:
        st.session_state.books.append({"title": title, "author": author, "status": status})
        st.sidebar.success(f"Added '{title}' by {author} ({status})")
    else:
        st.sidebar.error("⚠️ Please fill in all fields")

def filter_books(books: List[Dict[str, str]], search_query: str, filter_status: str) -> List[Dict[str, str]]:
    """
    Filters books based on search query and status.

    Args:
        books (List[Dict[str, str]]): List of books.
        search_query (str): Search query.
        filter_status (str): Filter status.

    Returns:        
        List[Dict[str, str]]: Filtered books.
    """
    search_query = search_query.lower()
    filtered_books = [
        book for book in books
        if search_query in book["title"].lower() or search_query in book["author"].lower()
    ]
    if filter_status != "All":
        filtered_books = [book for book in filtered_books if book["status"] == filter_status]
    
    # Check for empty categories
    if filter_status == "All" or filter_status == "Reading":
        reading_books = [book for book in filtered_books if book["status"] == "Reading"]
        if not reading_books:
            st.warning("No books in the 'Reading' category")
    if filter_status == "All" or filter_status == "Finished":
        finished_books = [book for book in filtered_books if book["status"] == "Finished"]
        if not finished_books:
            st.warning("No books in the 'Finished' category")
    if filter_status == "All" or filter_status == "To Read":
        to_read_books = [book for book in filtered_books if book["status"] == "To Read"]
        if not to_read_books:
            st.warning("No books in the 'To Read' category")
    
    return filtered_books

def display_books(books: List[Dict[str, str]]) -> None:
    """
    Displays books with formatted UI elements.

    Args:
        books (List[Dict[str, str]]): List of books.

    Returns:
        None
    """
    status_colors = {
        "Reading": "#6c757d",
        "Finished": "#28a745",
        "To Read": "#996515"
    }
    
    if books:
        for book in books:
            st.markdown(
                f"""
                <div style="
                    border: 1px solid #444;
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
        st.markdown("---")

def main():
    """Main function to run the Streamlit Book Tracker app."""
    st.set_page_config(page_title="Book Tracker", page_icon="📚", layout="wide")
    st.title("📕 Book Tracker")
    st.write("Welcome to the Book Tracker!")
    
    initialize_session_state()
    books = st.session_state.books
    
    # Sidebar form for adding books
    st.sidebar.header("📖 Add a book")
    title = st.sidebar.text_input("🔖 Title")
    author = st.sidebar.text_input("✒️ Author")
    status = st.sidebar.selectbox("Status", ["Reading", "Finished", "To Read"])
    
    if st.sidebar.button("Add Book"):
        add_book(title, author, status)
    
    # Main section
    st.subheader("📚 Your Books")
    search_query = st.text_input("Search by title or author")
    filter_status = st.selectbox("Filter by Status", ["All", "To Read", "Reading", "Finished"])
    
    filtered_books = filter_books(books, search_query, filter_status)
    display_books(filtered_books)

if __name__ == "__main__":
    main()
