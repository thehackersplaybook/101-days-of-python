import streamlit as st
import pdfplumber
import openai
import sqlite3
from fpdf import FPDF
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv
import asyncio


load_dotenv()
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

st.set_page_config(page_title="Bharat HealthEasy.ai 🚑", page_icon="⚕️", layout="wide")
st.title("🩺 Bharat HealthEasy 🚑")
st.caption("Upload your Medical Reports and Get Easy Explanation")

if not os.path.exists(".env"):
    secret_key = Fernet.generate_key()
    with open(".env", "w") as file:
        file.write(f"SECRET_KEY={secret_key.decode()}\n")
    st.warning("🔑 Secret Key Generated — Restart App")

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    st.error("❌ SECRET_KEY Not Found")
    st.stop()

cipher = Fernet(SECRET_KEY)

openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    st.error("❌ OpenAI API Key Not Found in .env File")
    st.stop()

conn = sqlite3.connect("data/medical_reports.db")
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS reports 
             (id INTEGER PRIMARY KEY, filename TEXT, content BLOB, explanation TEXT)''')
conn.commit()

def extract_pdf_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
    return text.strip()

def explain_medical_report(text):
    with st.spinner("🤖 AI is Writing Medical Explanation..."):
        prompt = f"Explain this medical report in very simple language:\n{text}"
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert doctor explaining medical reports."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

uploaded_file = st.file_uploader("📄 Upload Medical Report (PDF Only)", type=["pdf"])

if uploaded_file is not None:
    st.success("✅ Report Uploaded Successfully")
    with st.spinner("🔍 Reading PDF Report..."):
        text = extract_pdf_text(uploaded_file)
    
    if not text:
        st.error("❌ PDF is Empty or Not Readable")
        st.stop()
        
    encrypted_text = cipher.encrypt(text.encode())

    explanation = explain_medical_report(text)

    c.execute("INSERT INTO reports (filename, content, explanation) VALUES (?, ?, ?)", 
              (uploaded_file.name, encrypted_text, explanation))
    conn.commit()

    st.subheader("📑 Report Content")
    st.write(text)

    st.subheader("🧠 AI Explanation")
    st.success(explanation)

    if st.button("📥 Download Full Report"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Bharat HealthEasy.ai Report", ln=True, align='C')
        pdf.multi_cell(0, 10, f"Original Report:\n{text}")
        pdf.multi_cell(0, 10, f"\nAI Explanation:\n{explanation}")
        pdf.output("Medical_Report.pdf")
        st.download_button("Download Report", data=open("Medical_Report.pdf", "rb"), file_name="Medical_Report.pdf")

if st.button("🗑️ Delete All Reports"):
    with st.spinner("🗑️ Deleting All Reports..."):
        c.execute("DELETE FROM reports")
        conn.commit()
        st.success("✅ All Reports Deleted")
        st.stop()

st.subheader("📂 Previous Reports")
c.execute("SELECT * FROM reports")
reports = c.fetchall()

for report in reports:
    with st.expander(f"{report[1]}"):
        decrypted_text = cipher.decrypt(report[2]).decode()
        st.write("### Original Report")
        st.write(decrypted_text)
        st.write("### AI Explanation")
        st.success(report[3])
