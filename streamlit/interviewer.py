
import reportlab.lib
import streamlit as st
import traceback
import os
from typing import List, Any
import openai
from dotenv import load_dotenv
import markdown2
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageTemplate, Frame
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus.flowables import HRFlowable
import reportlab
from PyPDF2 import PdfReader
import io


## Constants
DEFAULT_NUM_QUESTIONS = 10
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"



def init():
    """Initializes the OpenAI API key

    Args:
        None

    Returns:
        None
    """

    load_dotenv(override=True, dotenv_path=".env")
    openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_questions(
    role: str,
    skills: List[str],
    experience: List[str],
    projects: List[str],
    num_questions=DEFAULT_NUM_QUESTIONS,
    resume_content="",
) -> List[str]:
    """
    Generate questions for a job role based on the specified skills, experience, and projects.

    Args:
        - role (str): The job role for which the questions are being generated.
        - num_questions (int): The number of questions to generate.
        - skills (List[str]): The key skills required for the job role.
        - experience (List[str]): The work experience required for the job role.
        - projects (List[str]): The projects that the candidate has worked on.

    Returns:
        - List[str]: A list of generated questions.
    """

    try:
        prompt = f"""
        Generate {num_questions} personalized interview questions for a candidate applying for the role of '{role}'.

        The questions should be a mix of technical, behavioral, and HR questions. 
        
        Focus on evaluating:
        - Skills: '''{",".join(skills)}'''
        - Work Experience: {",".join(experience)}, 
        - Projects: {",".join(projects)}. 
        
        Include scenario-based questions, problem-solving questions, and questions that assess the candidate's contribution to past projects.
        """

        if resume_content:
            prompt += f"""
            Generate {num_questions} personalized interview questions for a candidate applying for the role of '{role}'.

            The questions should be a mix of technical, behavioral, and HR questions. 
            
            Evaluate and generate the questions based on the resume.
            Resume: '''{resume_content}'''

            Include scenario-based questions, problem-solving questions, and questions that assess the candidate's contribution to past projects.
            """

        system = f"""
            You are Balesh, an intelligent and professional AI hiring manager. 
            You are sharp, can judge candidates by asking great questions and know how to optimize the hiring process of a company. 
            You ask professional, technical, behavioural and general (culture) questions to get the right, balanced evaluation of the candidate. 
            You will be evaluating candidates for multiple roles at a company, respond accordingly.
        """

        response = openai.chat.completions.create(
            model=DEFAULT_OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system,
                },
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content.split("\n")
    except Exception as e:
        print(f"Failed to generate questions: {e}")
        traceback.print_exc()
        return []

import openai

def analyze_resume(candidate_resume: str, job_role: str) -> str:
    """
    Analyzes a resume and provides feedback, ratings, and an improved version based on the candidate's suitability for the target job role.

    Args:
        candidate_resume (str): The resume of the candidate to be analyzed.
        job_role (str): The target job role for which the resume is being evaluated.

    Returns:
        str: A markdown-formatted analysis including ratings, feedback, strengths & weaknesses,
             overall candidate fit score, and a rewritten version of the resume with improvements.
    """

    system_prompt = """
    You are a professional resume analyzer. Your job is to review resumes and evaluate how well candidates fit their target job roles.
    Provide structured feedback, scores, and an improved resume version.
    """

    user_prompt = f"""
    The candidate is applying for the role of **'{job_role}'**. Below is their resume:

    ```
    {candidate_resume}
    ```

    Analyze the resume and return feedback in markdown format with the following sections:

    # Resume Analyzer

    ## Candidate Fit Score
    Provide an overall **Candidate Fit Score** out of 10 based on how well the candidate matches the target job role.

    ## Ratings & Feedback
    Provide detailed ratings and suggestions for improvement on the following categories:

    📝 Structure & Formatting - `(Score out of 10)`
    📄 Content Quality - `(Score out of 10)`
    🔑 Keywords & ATS Optimization - `(Score out of 10)`
    🌟 Impact & Accomplishments - `(Score out of 10)`
    💪 Personal Branding - `(Score out of 10)`
    🎯 Relevance to Job Role - `(Score out of 10)`
    🔍 Grammar & Language - `(Score out of 10)`

    ## Strengths & Weaknesses
    Provide a summary of what the resume does well and where it needs improvement.

    ## Final Assessment
    Give an **overall Candidate Fit Score** out of 10 based on the detailed analysis and suitability for the target job role.

    ## Improved Version
    Rewrite the resume with suggested improvements while maintaining the original intent and making it more impactful.
    """

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message.content


def add_header_footer(canvas: Canvas, doc: SimpleDocTemplate) -> None:
    """
    Adds a header and footer to each page of the PDF.

    Args:
        canvas (Canvas): The ReportLab canvas object.
        doc (SimpleDocTemplate): The document being generated.

    Returns:
        None
    """

    canvas.saveState()
    _, height = A4

    # Header
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawString(50, height - 50, "📄 Enterprise Report")

    # Footer with page number
    canvas.setFont("Helvetica", 10)
    canvas.setFillColor(colors.grey)
    canvas.drawString(50, 30, f"Page {doc.page}")

    canvas.restoreState()


def get_styled_paragraph(text: str, style_name: str) -> Paragraph:
    """
    Returns a styled paragraph for the PDF.

    Args:
        text (str): The content of the paragraph.
        style_name (str): The predefined style name.

    Returns:
        Paragraph: A formatted paragraph object.
    """

    styles = getSampleStyleSheet()

    custom_styles = {
        "Title": ParagraphStyle(
            "Title",
            fontName="Helvetica-Bold",
            fontSize=18,
            spaceAfter=12,
            textColor=colors.darkblue,
            alignment=1,  # Centered
        ),
        "Heading1": ParagraphStyle(
            "Heading1",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=18,
            spaceAfter=12,
            textColor=colors.darkblue,
        ),
        "Heading2": ParagraphStyle(
            "Heading2",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=16,
            spaceAfter=10,
            textColor=colors.darkred,
        ),
        "Heading3": ParagraphStyle(
            "Heading3",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=14,
            spaceAfter=8,
            textColor=colors.darkgreen,
        ),
        "BodyText": ParagraphStyle(
            "BodyText",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=12,
            leading=16,
            spaceAfter=8,
        ),
        "CodeBlock": ParagraphStyle(
            "CodeBlock",
            parent=styles["Normal"],
            fontName="Courier",
            fontSize=11,
            backColor=colors.lightgrey,
            spaceBefore=5,
            spaceAfter=5,
            leftIndent=20,
        ),
        "ListItem": ParagraphStyle(
            "ListItem",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=12,
            leftIndent=20,
            bulletIndent=15,
            spaceAfter=5,
        ),
    }

    return Paragraph(text, custom_styles.get(style_name, styles["Normal"]))


def markdown_to_pdf(content: str, filename: str) -> None:
    """
    Converts Markdown content to a professionally styled PDF.

    Args:
        content (str): The markdown content to be converted.
        filename (str): The output PDF file name.

    Returns:
        None
    """

    try:
        # Setup the document
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            leftMargin=50,
            rightMargin=50,
            topMargin=80,
            bottomMargin=50,
        )

        elements: List[Paragraph] = []

        elements.append(get_styled_paragraph("📄 Interview Questions", "Title"))
        elements.append(Spacer(1, 12))

        # Convert Markdown to HTML
        md_html = markdown2.markdown(content, extras=["tables", "fenced-code-blocks"])
        md_lines = md_html.split("\n")

        for line in md_lines:
            line = line.strip()
            if not line:
                continue  # Skip empty lines

            if line.startswith("<h1>"):
                elements.append(
                    get_styled_paragraph(
                        line.replace("<h1>", "").replace("</h1>", ""), "Heading1"
                    )
                )
            elif line.startswith("<h2>"):
                elements.append(
                    get_styled_paragraph(
                        line.replace("<h2>", "").replace("</h2>", ""), "Heading2"
                    )
                )
            elif line.startswith("<h3>"):
                elements.append(
                    get_styled_paragraph(
                        line.replace("<h3>", "").replace("</h3>", ""), "Heading3"
                    )
                )
            elif line.startswith("<pre><code>") and line.endswith("</code></pre>"):
                code_text = line.replace("<pre><code>", "").replace("</code></pre>", "")
                elements.append(get_styled_paragraph(code_text, "CodeBlock"))
            elif line.startswith("<ul><li>"):
                list_item = line.replace("<ul><li>", "• ").replace("</li></ul>", "")
                elements.append(get_styled_paragraph(list_item, "ListItem"))
            elif line.startswith("<hr />"):
                elements.append(
                    HRFlowable(width="100%", thickness=1, color=colors.grey)
                )
            else:
                elements.append(get_styled_paragraph(line, "BodyText"))

            elements.append(Spacer(1, 6))  # Add small spacing between elements

        # Define page template with header/footer
        frame = Frame(
            doc.leftMargin, doc.bottomMargin, doc.width, doc.height - 50, id="normal"
        )
        template = PageTemplate(id="page", frames=[frame], onPage=add_header_footer)
        doc.addPageTemplates([template])

        # Build the document
        doc.build(elements)
        print(f"✅ PDF successfully generated: {filename}")

    except Exception as e:
        print(f"❌ Error generating PDF: {e}")


def generate_pdf(content: str, filename: str) -> None:
    """
    Generates a professional PDF from the given text content.

    Args:
        content (str): The text content to include in the PDF.
        filename (str): The output PDF file name.

    Returns:
        None
    """
    
    return markdown_to_pdf(content, filename)


def extract_resume_content_from_file(uploaded_file: Any) -> str:
    """
    Extracts text content from a PDF file.

    Args:
        uploaded_file (str): The path to the PDF file.

    Returns:
        str: The extracted text content.
    """

    if uploaded_file is None:
        st.error("No file uploaded. Please upload a valid PDF file.")
        return ""

    file_bytes = uploaded_file.read()
    if not file_bytes:
        st.error("The uploaded file is empty. Please upload a valid PDF file.")
        return ""

    try:
        pdf_reader = PdfReader(io.BytesIO(file_bytes))
        resume_text = ""
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            resume_text += page.extract_text()
        return resume_text.strip()
    except Exception as e:
        st.error(f"Error extracting resume content: {e}")
        return ""


def setup_streamlit_app() -> None:
    """
    Sets up the Streamlit application configuration.

    Args:
        None

    Returns:
        None
    """
    st.set_page_config(
        layout="wide", page_title="AI Career Hub", page_icon="💼"
    )

    if "mode" not in st.session_state:
        st.session_state.mode = "default" 
    if "response" not in st.session_state:
        st.session_state.response = "" 

    st.sidebar.header("🎯 Choose your mode")
    if st.session_state.mode == "default":
        selected_mode = st.sidebar.selectbox(
            "Choose an AI-powered tool:",
            ["Interview Questions", "Resume Analyzer"],
            index=0,  
            key="selected_mode",
            help="Select the mode for your AI Career Hub experience."
        )
        st.sidebar.divider() 
        st.sidebar.markdown(f"### **Mode Selected:** `{selected_mode}`")
    else:
        if st.sidebar.button("🔄 Reset"):
            st.session_state.mode = "default"
            st.session_state.response = ""
            st.rerun()
            
    if st.session_state.mode == "default":
        if selected_mode == "Interview Questions":
            st.title("💼 AI-Powered Interview Question Generator")
            st.markdown(
            """
            **Streamline hiring or ace your next interview with AI-generated, role-specific questions.**  

            **How it works:**  
            1️⃣ Enter the **Job Role**  
            2️⃣ Upload a **PDF Resume** or **Enter Content Manually**  
            3️⃣ Choose the **Number of Questions**  
            4️⃣ Click **"Generate Questions"** for AI-driven insights  

            **Perfect for:** Recruiters, hiring managers & job seekers seeking **precise, AI-powered questions.**
            """,
            unsafe_allow_html=True,
            )
            role = st.text_input("🔍 Job Role", placeholder="e.g. Data Scientist", key="interview_role")
            resume_text = ""

            col1, col2 = st.columns([1,1])
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
                """,
                unsafe_allow_html=True,
            )
            with col1:
                file_upload = st.button("📂 Upload PDF Resume", key="upload_resume")
                if file_upload:
                    st.session_state.show_file_uploader = True 
            with col2:
                canditate_resume = st.button("📄Enter Resume Content Manually", key="resume_content")
                if canditate_resume:
                    st.session_state.show_file_uploader = False

            if st.session_state.get("show_file_uploader", False):
                uploaded_file = st.file_uploader(
                "📂 Upload PDF Resume", type=["pdf"], accept_multiple_files=False
                )

                if uploaded_file is not None:
                    st.session_state.uploaded_file = uploaded_file

                if "uploaded_file" in st.session_state:
                    with st.spinner("Uploading resume..."):
                        resume_text = extract_resume_content_from_file(uploaded_file)
                        if resume_text.strip(): 
                            st.sidebar.success("✅ Resume Uploaded & Parsed Successfully!")
                        else:
                            st.sidebar.error("⚠️ The uploaded file is empty or unreadable. Please upload a valid PDF file.")
            
            if not st.session_state.get("show_file_uploader", False):
                col1, col2, col3 = st.columns(3)

                with col1:
                    skills = st.text_area(
                    "🛠️ Key Skills",
                    placeholder="e.g. Python, Machine Learning, Data Structures",
                    height=150,
                    key="skills",
                        )
                with col2:
                    experience = st.text_area(
                    "💼 Work Experience",
                    placeholder="e.g. 2 years in software development",
                    height=150,
                    key="experience",
                )
                with col3:
                    projects = st.text_area(
                    "🚀 Projects",
                    placeholder="e.g. Built a recommendation system",
                    height=150,
                    key="projects",
                )
                num_questions = st.slider("🔥 Number of Questions", 1, 20, 10)

            if st.button("🚀 Generate Questions"):
                if not role or (not skills and not resume_text) or (not experience and not resume_text) or (not projects and not resume_text):
                    st.warning("⚠️ Please fill in all fields before generating questions.")
                else:
                    with st.spinner("Generating questions..."):
                        questions = generate_questions(
                        role=role,
                        skills=skills,
                        experience=experience,
                        projects=projects,
                        num_questions=num_questions,
                        resume_content=resume_text,
                    )
                    st.success("✅ Questions Generated!")
                    st.session_state.response = "\n".join(questions)
                    st.session_state.mode = "generate_questions"
                    st.rerun()

                    generate_pdf("\n".join(questions), "Interview_Questions.pdf")
                    with open("Interview_Questions.pdf", "rb") as file:
                        st.download_button(
                            "📄 Download Questions as PDF",
                            file,
                            "Interview_Questions.pdf",
                            "application/pdf",
                        )

        elif selected_mode == "Resume Analyzer":

            st.title("📄 AI-Powered Resume Analyzer")
            st.markdown(
            """
            **Get instant AI-driven insights from your resume in seconds.**  

            **How it works:**  
            1️⃣ Enter the **Job Role**  
            2️⃣ Upload a **PDF Resume**  
            3️⃣ Click **"Analyze Resume"** for AI-powered insights  

            **Perfect for:** Job seekers, recruiters & hiring managers looking for **quick and precise resume analysis.**
            """,
            unsafe_allow_html=True,
        )

            resume_text = ""
            role = st.text_input("🔍 Job Role", placeholder="e.g. Data Scientist", key="resume_analyzer_role")
            uploaded_file = st.file_uploader(
                "📂 Upload & Parse Resume", type=["pdf"], accept_multiple_files=False
            )
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
                """,
                unsafe_allow_html=True,
            )

            if uploaded_file is not None:
                resume_text = extract_resume_content_from_file(uploaded_file)
                if resume_text.strip():
                    st.sidebar.success("✅ Resume Uploaded & Parsed Successfully!")
                else:
                    st.error("⚠️ The uploaded file is empty or unreadable. Please upload a valid PDF file.")

            if st.button("🔍 Analyze Resume"):
                if not role or not resume_text:
                    st.warning("⚠️ Please fill in all fields before analyzing resume.")
                else:
                    with st.spinner("Analyzing resume..."):
                        analysis = analyze_resume(resume_text, role)
                        st.success("✅ Resume Analyzed!")
                        st.session_state.response = analysis
                        st.session_state.mode = "analyze_resume"
                        st.rerun()


                generate_pdf(analysis, "Resume_Analysis.pdf")
                with open("Resume_Analysis.pdf", "rb") as file:
                    st.download_button(
                        "📄 Download Analysis as PDF",
                        file,
                        "Resume_Analysis.pdf",
                        "application/pdf",
                )
    elif st.session_state.mode == "generate_questions":
        st.title("📄 Generated Interview Questions")
        st.markdown(st.session_state.response)
        st.sidebar.button("🔄 Reset",key="reset_1")

    elif st.session_state.mode == "analyze_resume":
        st.title("📄 Resume Analysis")
        st.markdown(st.session_state.response)
        st.sidebar.button("🔄 Reset",key="reset_2")
        
if __name__ == "__main__":
    init()
    setup_streamlit_app()