import streamlit as st
import openai
from dotenv import load_dotenv
import os
import traceback
load_dotenv(verbose=True, override=True, dotenv_path=".env")


def validate_openai_key(openai_key: str) -> bool:
    """
    Validates the OpenAI API key by making a test request.
    
    Args:
        api_key (str): The OpenAI API key to validate.
        
    Returns:
        bool: True if the key is valid, False otherwise.
    """
    try:
        if not openai_key:
            return False
        client = openai.Client(api_key=openai_key)
        client.models.list()
        return True
    except openai.OpenAIError:  
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return False
    
def image_generator(image:str, text_prompt:str, openai_key:str) ->str:
    """
    Generates a stunning Studio Ghibli-style image based on the provided image or text prompt using OpenAI's DALL-E model.

    Args:
        image (str): The image to be used as a reference.
        text_prompt (str): The text prompt for the image generation.
        openai_key (str): The OpenAI API key.

    Returns:
        str: The URL of the generated image.
    """
    try:
        openai.api_key = openai_key
        response = openai.Image.create(
            prompt=text_prompt,
            n=1,
            size="1024x1024",
            response_format="url"
        )
        image_url = response['data'][0]['url']
        return image_url
    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return None



def main():
    st.set_page_config(page_title="Ghibli Dreamer", page_icon=":art:",layout="wide")
    st.title(":art: Ghibli Dreamer")

    st.sidebar.header("Settings")
    st.sidebar.text_input("Enter your OpenAI API Key:", type="password", key="api_key")

    col1, col2 = st.sidebar.columns(2)
    
    if col1.button("💾 Save API Key"):
        with st.spinner("Validating API key..."):
            openai_key = st.session_state.api_key
            if validate_openai_key(openai_key):
                st.sidebar.success("OpenAI key saved successfully!")
            else:
                st.sidebar.error("Invalid OpenAI key. Please check and try again.")

    if col2.button("🔄 Reset API Key"):
        with st.spinner("Resetting API key..."):
            st.session_state.api_key = ""
            st.sidebar.success("OpenAI key reset successfully!")    
    
    col1, col2 = st.columns([1,3])
    with col1:
        st.image("./images/ghibli_upload_image.png", caption="Upload an image", width=300)
    with col2:
        upload_image = st.file_uploader("", type=["jpg", "jpeg", "png"], key="image_upload")

    prompt_input = st.text_area("Enter your text prompt:", placeholder="e.g. A cat in a forest", key="text_prompt")


    


if __name__ == "__main__":
    main()