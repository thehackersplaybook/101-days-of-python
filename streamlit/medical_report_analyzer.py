import streamlit as st
from openai import OpenAI, OpenAIError
import os
import fitz
from PIL import Image
import traceback

def validate_openai_key(openai_key: str) -> bool:
    """
    Validates the OpenAI API key by making a test request using the OpenAI v1 API.
    
    Args:
        openai_key (str): The OpenAI API key to validate.
        
    Returns:
        bool: True if the key is valid, False otherwise.
    """
    if not openai_key:
        return False
    try:
        OpenAI(api_key=openai_key).models.list()
        return True
    except OpenAIError:
        return False
    except Exception as e:
        print(f"Unexpected issue during API key validation: {e}")
        traceback.print_exc()
        return False
    
def display_pdf_first_page_as_image(uploaded_file):
    """
    Extracts the first page of the uploaded PDF and converts it into an image.

    Args:
        uploaded_file: The uploaded PDF file.

    Returns:
        PIL.Image: The first page of the PDF as an image.
    """
    try:
        # Open the uploaded PDF file
        pdf_document = fitz.open(stream=uploaded_file, filetype="pdf")
        first_page = pdf_document[0]  # Get the first page
        pix = first_page.get_pixmap()  # Render the page as a pixmap
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        return image
    except Exception as e:
        st.error(f"Error processing the PDF: {e}")
        traceback.print_exc()
        return None
    
def extract_text_from_pdf(uploaded_file):
    """
    Extracts text from the uploaded PDF file.

    Args:
        uploaded_file: The uploaded PDF file.

    Returns:
        str: The extracted text from the PDF.
    """
    try:
        pdf_document = fitz.open(stream=uploaded_file, filetype="pdf")
        extracted_text = ""
        for page in pdf_document:
            extracted_text += page.get_text()
        return extracted_text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        traceback.print_exc()
        return None
    
def medical_file_uploader():
        uploaded_file = st.file_uploader("", type=["pdf"])
        if uploaded_file:
            pdf_bytes = uploaded_file.read()
            first_page_image = display_pdf_first_page_as_image(uploaded_file = pdf_bytes)
            if first_page_image:
                st.sidebar.image(first_page_image, caption="Uploaded Medical Report", width=200)
            return pdf_bytes
        return None

def is_valid_medical_report(extracted_text):
    """
    Checks if the extracted text is a valid medical report.

    Args:
        extracted_text: The extracted text from the PDF.

    Returns:
        bool: True if the text is a valid medical report, False otherwise.
    """
    try:
        client = OpenAI()
        response = client.responses.create(
            model = "gpt-4o-mini",
            instructions = "Check if the extracted text is a medical report or not. If not then return 0 otherwise return 1.",
            input = [
                {
                    "role": "developer",
                    "content": "Check if the extracted text is a medical report or not."
                },
                {
                    "role": "user",
                    "content": extracted_text
                }
            ]
        )
        if response.output_text == "1":
            return True
        else:
            return False
    except Exception as e:
        print(f"Error in text generation: {e}")
        traceback.print_exc()
        return False
    
def medical_report_analyzer(extracted_text, openai_key):
    """
    Analyzes the uploaded medical report PDF file.

    Args:
        uploaded_file: The uploaded PDF file.

    Returns:
        str: The analysis result.
    """
    try:
        # Set OpenAI API key
        if not openai_key:
            raise ValueError("OpenAI API key is required.")
        if is_valid_medical_report(extracted_text) == False:
            report_error_message = "The uploaded file is not a valid medical report. Please upload a valid medical report."
            st.error(report_error_message)
            return None
        
        # Generate report analysis using OpenAI
        client = OpenAI()
        response = client.responses.create(
            model = "gpt-4.1",
            instructions = f"Analyze the medical report and talk like a doctor to provide medical insights.",
            input = [
                {
                    "role": "developer",
                    "content": "Analyze the medical report and provide detailed medical insights."
                },
                {
                    "role": "user",
                    "content": extracted_text
                }
            ]
        )
        return response.output_text
    except Exception as e:
        print(f"Error in text generation: {e}")
        traceback.print_exc()
        return None
    

# UI for the Streamlit app
def main():
    st.set_page_config(page_title="HealthifyAI", page_icon=":guardsman:", layout="wide")
    st.title("HealthifyAI - Medical Report Analyzer")
    st.caption("Upload a PDF medical report to extract and analyze the text.")

    # Sidebar for OpenAI API Key
    with st.sidebar:
        st.header("🔑 API Key Management")
        openai_key = st.text_input("Enter your OpenAI API Key:", type="password", key="api_key_input_sidebar", placeholder="sk-XXXXXXXXXXXXXXXXXXXXXXXXXX", help="Get your API key from https://platform.openai.com/signup")

        col1, col2 = st.columns(2)
        if col1.button("💾 Save API Key"):
            if not openai_key:
                st.warning("❌ Please fill in the API key field before saving.")
            else:
                with st.spinner("⏳ Validating API key..."):
                    is_valid = validate_openai_key(openai_key)
                    if is_valid:
                        st.toast("API key saved successfully! ✅")
                    else:
                        st.toast("Invalid OpenAI API key. Please check and try again. ❌")
        if col2.button("🔄 Reset API Key"):
            if not openai_key:
                st.warning("❌ No API key to reset.")
            else:
                with st.spinner("Resetting API key..."):
                    st.session_state.openai_key = None
                    st.success("OpenAI API key reset successfully!")
        st.markdown("---")

    tab1, tab2 = st.tabs(["🔍 Analyze Medical Report", "📄 Analyze Prescription"])

    with tab1:
        st.markdown("")
        st.subheader("🔍 Understand Your Medical Report")
        st.caption("Have some doubts about your medical report? Upload it here and let AI explain it for you.")

        # Use session state to track file upload and extracted text
        if "file_uploaded" not in st.session_state:
            st.session_state.file_uploaded = False
        if "extracted_text" not in st.session_state:
            st.session_state.extracted_text = ""

        pdf_bytes = medical_file_uploader()
        if pdf_bytes and not st.session_state.file_uploaded:
            with st.spinner("⏳ Extracting text from the PDF..."):
                extracted_text = extract_text_from_pdf(pdf_bytes)
                if extracted_text:
                    st.session_state.file_uploaded = True
                    st.session_state.extracted_text = extracted_text
                    st.toast("✅ File Uploaded Successfully!")
                else:
                    st.error("❌ Failed to upload file. Please try again.")

        if st.button("🧠 Analyze Report"):
            if not openai_key:
                st.warning("❌ Please enter your OpenAI API key")
            else:
                with st.spinner("⏳ Analyzing Report..."):
                    analysis_result = medical_report_analyzer(extracted_text= extracted_text, openai_key= openai_key)
                    if analysis_result:
                        st.success("✅ Analysis completed!")
                        st.write(analysis_result)
                    
    
if __name__ == "__main__":
    main()
