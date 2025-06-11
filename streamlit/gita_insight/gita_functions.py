import pandas as pd
import streamlit as st
import chromadb
import traceback
import constants

# --- Initialize ChromaDB Client ---
chroma_client = chromadb.PersistentClient()
collection = chroma_client.get_or_create_collection(name="bhagavad_gita")

# --- Load Dataset ---
@st.cache_data
def load_dataset(path: str) -> pd.DataFrame:
    """
    Load a CSV file into a DataFrame.

    Args:
        path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame containing the data from the CSV file.
    """
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        st.error("File not found. Check the path.")
        return None
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        traceback.print_exc()
        return None
    
def save_dataset(df: pd.DataFrame, path: str) -> None:
    """
    Save the DataFrame to a CSV file.

    Args:
        df (pd.DataFrame): DataFrame to save.
        path (str): Path to save the CSV file.

    Returns:
        None
    """
    try:
        df.to_csv(path, index=False)
        st.success("Dataset saved.")
    except Exception as e:
        st.error(f"Error saving dataset: {e}")
        traceback.print_exc()


# --- Load DB ---
def load_bhagavad_gita() -> pd.DataFrame:
    """
    Load the Bhagavad Gita dataset from the specified path.

    Args :
        None

    Returns:
        pd.DataFrame: DataFrame containing the Bhagavad Gita shlokas and their meanings.
    """
    return load_dataset(constants.GITA_DATASET_PATH)

def load_bhagavad_gita_into_db():
    """
    Load the Bhagavad Gita dataset into the ChromaDB collection.
    """
    try:
        df = load_bhagavad_gita()
        documents, ids = [], []
        
        for _, row in df.iterrows():
            shloka_text = f"""
                ID: {row["ID"]}
                Chapter: {row['Chapter']}
                Verse: {row['Verse']}
                Shloka: {row['Shloka']}
                Hindi Meaning: {row['HinMeaning']}
                English Meaning: {row['EngMeaning']}
                Word Meanings: {row['WordMeaning']}
                Context: {row['context']}
            """
            documents.append(shloka_text)
            ids.append(str(row["ID"]))

        collection.upsert(documents=documents, ids=ids)
        return len(documents)
    except Exception as e:
        st.error(f"Error loading into DB: {e}")
        traceback.print_exc()
        return 0

# --- Query ---
def query_shloka(query: str, n: int = 5) -> list:
    """
    Query the ChromaDB collection for shlokas related to the user's query.

    Args:
        query (str): The user's query or situation.
        n (int): The number of shlokas to retrieve.

    Returns:
        list: List of shlokas related to the user's query.
    """
    try:
        results = collection.query(query_texts=[query], n_results=n)
        return results["documents"][0]
    except Exception as e:
        st.error(f"Query error: {e}")
        traceback.print_exc()
        return []