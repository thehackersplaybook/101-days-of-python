import streamlit as st
import re

def count_characters(text: str) -> dict[str, int]:
    """
    Counts characters in text (with and without spaces).
    
    Args:
        text (str): The input text.

    Returns:
        dict[str, int]: A dictionary with counts of characters with and without spaces.
    """
    return {
        "with_spaces": len(text),
        "without_spaces": len(text.replace(" ", "").replace("\n", "").replace("\t", ""))
    }

def count_words(text: str) -> int:
    """
    Counts words in the text.
    
    Args:
        text (str): The input text.

    Returns:
        int: The number of words in the text.
    """
    return len(text.split())

def count_lines(text: str) -> int:
    """
    Counts lines in the text.
    
    Args:
        text (str): The input text.

    Returns:
        int: The number of lines in the text.
    """
    return text.count("\n") + 1 if text else 0

def search_text(text: str, query: str) -> dict[str, str | int]:
    """
    Searches for a query in the text and highlights matches.
    
    Args:
        text (str): The input text.
        query (str): The search query.

    Returns:
        dict[str, str | int]: A dictionary with the count of matches and the highlighted text (if matches exist).
    """
    if not query.strip():
        return {
            "count": 0,
            "highlighted": None  # No highlighted text if query is empty
        }

    matches = re.findall(re.escape(query), text, re.IGNORECASE)
    if matches:
        highlighted_text = re.sub(
            re.escape(query), 
            lambda match: f'<span style="background-color: green; padding: 2px; border-radius: 4px;">{match.group()}</span>',
            text,
            flags=re.IGNORECASE
        )
        return {
            "count": len(matches),
            "highlighted": highlighted_text
        }
    else:
        return {
            "count": 0,
            "highlighted": ""  # Return an empty string if no matches
        }

def main():
    """Main function to create the Streamlit app."""
    
    st.set_page_config(page_title="Text Analyzer", page_icon="🔍", layout="wide")
    st.title("🔍 Text Analyzer")

    # Initialize session state
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    if "searched" not in st.session_state:
        st.session_state.searched = False
    if "text" not in st.session_state:  # Initialize text
        st.session_state.text = ""
    if "query" not in st.session_state:  # Initialize query
        st.session_state.query = ""

    # Text Input Section
    text: str = st.text_area("Enter your text here:", height=150)

    # Submit Button Logic
    if st.button("Submit"):
        if text.strip():  # Ensure text is not empty
            st.session_state.submitted = True
            st.session_state.text = text
        else:
            st.error("Please enter some text before submitting.")

    # Display Text Statistics
    if st.session_state.submitted:
        stats = count_characters(st.session_state.text)
        num_words = count_words(st.session_state.text)
        num_lines = count_lines(st.session_state.text)

        st.subheader("📊 Text Statistics")
        st.markdown("<hr style='border:1px solid grey; margin-top:5px; margin-bottom:30px'>", unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🔠 Characters", stats["with_spaces"])
        col2.metric("✂️ No Spaces", stats["without_spaces"])
        col3.metric("📝 Words", num_words)
        col4.metric("📄 Lines", num_lines)

    if st.session_state.submitted:
        # Search Section
        st.subheader("🔍 Search in Text")
        st.markdown("<hr style='border:1px solid grey; margin-top:5px; margin-bottom:20px'>", unsafe_allow_html=True)

        query: str = st.text_input("Enter a word or phrase to search:")

        if st.button("Search"):
            if not query.strip():
                st.error("Please enter a valid search term.")
            else:
                st.session_state.searched = True
                st.session_state.query = query

        # Display Search Results
        if st.session_state.searched:
            result = search_text(st.session_state.text, st.session_state.query)
        
            st.subheader("🔎 Search Results")
            st.markdown("<hr style='border:1px solid grey; margin-top:5px; margin-bottom:30px'>", unsafe_allow_html=True)
            st.markdown(f"📌 **Occurrences of `{st.session_state.query}`:** {result['count']}")
            if result["count"] > 0:
                st.markdown("**Highlighted Text:**")
                st.markdown(result["highlighted"], unsafe_allow_html=True)
            else:
                st.warning("No matches found.")
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




if __name__ == "__main__":
    main()
