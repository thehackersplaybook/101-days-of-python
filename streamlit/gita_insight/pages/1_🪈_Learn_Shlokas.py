import streamlit as st
from Homepage import sidebar_api_key_manager

sidebar_api_key_manager(unique_key_suffix="learn_shlokas")


st.title("📖 Learn Shlokas")
st.markdown("Learn and memorize shlokas from the Bhagavad Gita.")
