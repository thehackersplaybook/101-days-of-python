import streamlit as st
import platform
import psutil
import cpuinfo
import openai
import shutil
import os
import traceback
import time
import json

DEFAULT_MODEL = "gpt-4o"

import json
import os

def load_apps():
    file_path = os.path.join(os.path.dirname(__file__), "data/application_name.json")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, "r") as file:
        try:
            data = json.load(file)
            return data.get("applications", [])
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in {file_path}")


APPS = load_apps()


def validate_openai_api_key(openai_key) -> bool:
    """
    Validate the OpenAI API key by making an API request.
    
    Args:
        openai_key (str): OpenAI API key.

    Returns:
        bool: True if the API key is valid, False otherwise.
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
        traceback.print_exc()
        return False
    
def system_info() -> dict:
    """
    Function to display system information.

    Args:
        None

    Returns:
        dict: A dictionary containing the system details.
    """
    try:
        if not st.session_state.get("openai_key",None):
            st.error("⚠️ Please enter your OpenAI API Key to check the compatibility.")
            st.stop()

        system_details={
            "Operating System": f"{platform.system()} {platform.release()} ({platform.version()})",
                "Machine": platform.machine(),
                "Processor": platform.processor(),
                "CPU": cpuinfo.get_cpu_info().get("brand_raw", "Unknown"),
                "Architecture": cpuinfo.get_cpu_info().get("arch", "Unknown"),
                "Core Count": f"{psutil.cpu_count(logical=False)} physical, {psutil.cpu_count(logical=True)} logical",
                "Total RAM (GB)": round(psutil.virtual_memory().total / (1024**3), 2),
                "Available RAM (GB)": round(psutil.virtual_memory().available / (1024**3), 2),
                "Total Storage (GB)": round(shutil.disk_usage("/").total / (1024**3), 2),
                "Used Storage (GB)": round(shutil.disk_usage("/").used / (1024**3), 2),
                "Free Storage (GB)": round(shutil.disk_usage("/").free / (1024**3), 2),
        }
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            system_details["GPU"] = gpus[0].name if gpus else "No dedicated GPU found"
        except ImportError:
            system_details["GPU"] = "GPUtil library not installed"

        return system_details
    
    except Exception as e:
        return {"Error": str(e)}
    

def ai_specs_summary(system_details:dict) -> str:
    """
    Function to check the compatibility of the AI system with the given system details.
    
    Args:
        system_details (dict): A dictionary containing the system details.

    Returns:
        str: A summary of the AI system compatibility with the given system details.
    """

    formatted_system_details = f"""System Details:\n"""
    for key, value in system_details.items():
        formatted_system_details += f"- **{key}**: {value}\n"
        formatted_system_details += """
        You are an expert in system hardware analysis. Given the following system specifications, generate a well-structured markdown report with the following format:

### **Instructions for the Markdown Report:**
1. **Title**  
   - Start with an appropriate title such as "📊 System Analysis Report".
   - Provide a short introduction explaining what the report covers.

2. **System Specifications Table**  
   - Convert the given system specifications into a properly formatted Markdown table.
   - Ensure the table includes headings such as **Component, Details**.

3. **Detailed Component Analysis**  
   - Provide a breakdown of each component (CPU, RAM, Storage, GPU, OS, etc.).
   - Explain the significance of each component in real-world usage.
   - If any component is outdated, suggest an upgrade.

4. **Performance Suitability Analysis**  
   - Based on the hardware, determine the best use cases for the device.
   - Mention whether the system is suitable for **gaming, coding, video editing, studying, or general productivity**.
   - If it has a powerful GPU, indicate its suitability for AI/ML tasks.

5. **Conclusion & Recommendations**  
   - Provide a final summary of the device's strengths and weaknesses.
   - Suggest any necessary upgrades to improve performance.
   - If applicable, mention if the device is future-proof or will need an upgrade soon.
    """
    
    try:
        response = openai.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "You are a system hardware expert"},
                {"role": "user", "content": formatted_system_details}],
            max_tokens=1500
        )
        return response.choices[0].message.content.strip()

    except openai.OpenAIError as e:
        return f"❌ OpenAI API Error: {str(e)}"
    
def app_compatibility_check(app_name:str, sys_info:str) -> str:
    """
    Function to check the compatibility of the app with the given system details.
    
    Args:
        app_name (str): The name of the app to be checked.  

    Returns:
        str: A summary of the app compatibility with the given system details.
    """

    SYSTEM_PROMPT = f"""
    You are an intelligent system compatibility checker. Your task is to analyze the given application specification and compare it with the user's system specification stored in session data.

    ### **Task:**
    1. **Retrieve System Specifications**: Access system specifications stored in session data, including:
       - **Processor (CPU)**
       - **Graphics Card (GPU)**
       - **RAM**
       - **Storage Space**
       - **Operating System**

    2. **Retrieve Application Requirements**: Analyze the selected application's **minimum** and **recommended** system requirements.

    3. **Perform a Compatibility Check**:
       - Compare the system's CPU, GPU, RAM, and storage with the **minimum** and **recommended** requirements.
       - Identify if the system **meets, exceeds, or falls short** of the requirements.

    4. **Display the Comparison in Tabular Format**: The comparison should be structured as follows:

    | Component  | User's System  | App Minimum Requirement | App Recommended Requirement | Status |
    |------------|--------------|------------------------|----------------------------|--------|
    | **CPU**    | User's CPU   | App Min CPU           | App Recommended CPU        | ✅ / ❌ |
    | **GPU**    | User's GPU   | App Min GPU           | App Recommended GPU        | ✅ / ❌ |
    | **RAM**    | User's RAM   | App Min RAM           | App Recommended RAM        | ✅ / ❌ |
    | **Storage**| User's Storage | App Min Storage     | App Recommended Storage    | ✅ / ❌ |

    5. **Provide an Explanation**:
       - If the system meets or exceeds the recommended specs, state: *"Your system is fully compatible with the application. No upgrades needed."*
       - If the system meets the minimum specs but falls short of recommended specs, suggest:  
         *"Your system can run the application, but for optimal performance, consider upgrading [RAM/GPU/CPU]."*
       - If the system **does not meet the minimum requirements**, display:  
         *"Your system is not compatible with this application. You need to upgrade [specific component]."*

    6. **Suggest Possible Upgrades**:
       - If the system needs an upgrade, suggest specific components (e.g., "Upgrade RAM from 4GB to 8GB for smoother performance").
       - Provide cost-effective upgrade options if necessary.

    ### **Final Output Format**:
    - **Table**: Display the compatibility check in a structured format.
    - **Explanation**: A detailed summary of the compatibility result.
    - **Upgrade Suggestions**: If applicable, provide upgrade recommendations.

    Ensure the response is **clear, structured, and concise**, allowing users to quickly assess their system's compatibility with the application.
    """
    try:
        if not st.session_state.openai_key:
            st.error("⚠️ Please enter your OpenAI API Key to check the compatibility.")
            st.stop()

        response = openai.chat.completions.create(
            model= DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Application Name: {app_name}\nSystem Specifications:\n{sys_info}"}
            ],
            )
        return response.choices[0].message.content.strip()
    except openai.OpenAIError as e:
        return f"❌ OpenAI API Error: {str(e)}"


def main():
    """
    Main function for the System Compatibility Checker.
    """
    st.set_page_config(layout="wide", page_title="System Compatibility Checker", page_icon="💻")

    st.title("💻 System Compatibility Checker")
    st.caption("This tool detects your system specifications and checks if a software can run on your device.")

    st.sidebar.header("⚙️ Settings")

    if "openai_key" not in st.session_state:
        st.session_state.openai_key = ""

    new_api_key = st.sidebar.text_input(
        "🔑 Enter your OpenAI API Key",
        value=st.session_state.openai_key,
        type="password",
        key="openai_api_key_input",
            )

    col1, col2 = st.sidebar.columns(2)
    

    if col1.button("💾 Save API Key"):
        if new_api_key:
            if validate_openai_api_key(new_api_key):
                st.session_state.openai_key = new_api_key
                st.sidebar.success("🔑 API Key saved successfully!")
                st.session_state["openai_api_key"] = ""
            else:
                st.sidebar.error("❌ Invalid API Key! Please check and try again.")
        else:
            st.sidebar.error("⚠️ Please enter your OpenAI API Key!")

    if col2.button("🔄 Reset API Key"):
        st.session_state.openai_key = ""
        st.sidebar.warning("🔄 API Key reset!")
        st.session_state["openai_api_key"] = ""

    tab1, tab2 = st.tabs(["💻 System Information", "🔍 App Compatibility Checker"])

    with tab1:
        st.subheader("Check your system specifications and generate a report.")
        st.markdown(
                """
                <style>
                div.stButton > button {
                    height: 60px; /* Adjust button height */
                    width: 100%;  /* Full width */
                    font-size: 18px; /* Bigger text */
                    border-radius: 8px; /* Slightly rounded corners */
                }
                </style>
                """,unsafe_allow_html=True,
         )

        if st.button("Check System Info", key="check_system_info"):
            with st.spinner("Fetching system information..."):
                sys_info = system_info()
                st.session_state.system_details = sys_info
            st.sidebar.info("💻 System Details saved successfully!")

            with st.spinner("Generating System Specs Report..."):
                ai_summary = ai_specs_summary(sys_info)
                st.toast("📄 AI Specs Report Generated!")
            st.markdown(ai_summary,unsafe_allow_html=True)
            
    with tab2:
        st.header("🛠 App Compatibility Checker")
        st.write("Check compatibility of applications with your system.")

        app_name = [app["name"] for app in APPS]
        
        if "manual_entry" not in st.session_state:
            st.session_state.manual_entry = False
        if "selected_app" not in st.session_state:
            st.session_state.selected_app = app_name[0]
        

        col1,col2 = st.columns(2)

        with col1:
            selected_apps = st.selectbox("Select An App To Check Compatibility",options=app_name,index=0)
            if not st.session_state.manual_entry:
                st.session_state.selected_app = selected_apps

        with col2:
            if st.button("Enter Manually"):
                st.session_state.manual_entry = True

            if st.session_state.manual_entry:
                custom_app_name = st.text_input("Enter app name")

                if custom_app_name:
                    st.session_state.selected_app = custom_app_name
                    st.caption(f"You have selected {custom_app_name} for compatibility check.")

        if st.button("Check Compatibility", key="check_compatibility"):
            if "system_details" not in st.session_state or not st.session_state.system_details:
                sys_info = system_info()
                st.session_state.system_details = sys_info
            st.sidebar.info("💻 System Details saved successfully!")

            with st.spinner("Generating System Specs Report..."):
                ai_summary = ai_specs_summary(sys_info)
                st.toast("📄 AI Specs Report Generated!")
            st.markdown(ai_summary,unsafe_allow_html=True)
                
            
            with st.spinner("Checking Compatibility..."):
                sys_info = st.session_state.system_details
                app_name = st.session_state.selected_app
                compatibility_summary = app_compatibility_check(app_name, sys_info)
            st.markdown(compatibility_summary,unsafe_allow_html=True)

if __name__ == "__main__":
    main()
