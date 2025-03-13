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

def analyze_resume(candidate_resume: str, job_role: str) -> str:
    f"""
    Analyzes a resume and provides feedback, ratings, and an improved version based on the candidate's suitability for the target job role.
    Args:
        candidate_resume (str): The resume of the candidate to be analyzed.
        job_role (str): The target job role for which the resume is being evaluated.

    Returns:
        str: A markdown-formatted analysis including ratings, feedback, strengths & weaknesses,
             overall candidate fit score, and a rewritten version of the resume with improvements.
    """
    system_prompt = f"""
    The task is to analyze the resume of a candidate applying for the role of '{job_role}'.
    The resume of the candidate is {candidate_resume}.
        You are a professional resume analyzer. Your job is to review the following resume and evaluate how well the candidate fits the target job role.
        Rate the resume on a scale of 1-10 across different categories and provide actionable feedback for each category.
        Format your response in **markdown** with the following sections:

        # Resume Analyzer

        ## Candidate Fit Score
        Provide an overall **Candidate Fit Score** out of 10 based on how well the candidate matches the target job role.

        ## Ratings & Feedback
        Provide detailed ratings and suggestions for improvement on the following categories:

        📝 Structure & Formatting - Is the layout clean, consistent, and visually appealing? `(Score out of 10)`
        📄 Content Quality - Are the job roles, achievements, and skills clearly described? `(Score out of 10)`
        🔑 Keywords & ATS Optimization - Does the resume contain relevant keywords for the target job? `(Score out of 10)`
        🌟 Impact & Accomplishments - Are quantifiable achievements highlighted? `(Score out of 10)`
        💪 Personal Branding - Does the resume convey a unique personal brand? `(Score out of 10)`
        🎯 Relevance to Job Role - How closely does the candidate's experience and skills match the target job role? `(Score out of 10)`
        🔍 Grammar & Language - Is the writing clear, error-free, and professional? `(Score out of 10)`

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
            {"role": "user", "content": f"Resume:\n{candidate_resume}\n\nTarget Job Role: {job_role}"}
        ]
    )

    return response.choices[0].message.content


def add_header_footer(canvas: Canvas, doc: SimpleDocTemplate) -> None:
    """
    Adds a header and footer to each page of the PDF.

    Args:
        canvas (Canvas): The ReportLab canvas object.
        doc (SimpleDocTemplate): The document being generated.
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
    """
    return markdown_to_pdf(content, filename)


def extract_resume_content_from_file(pdf_file: Any) -> str:
    """
    Extracts text content from a PDF file.

    Args:
        pdf_file (str): The path to the PDF file.

    Returns:
        str: The extracted text content.
    """
    file_bytes = pdf_file.read()
    pdf_reader = PdfReader(io.BytesIO(file_bytes))
    resume_text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        resume_text += page.extract_text()
    return resume_text


def setup_streamlit_app() -> None:
    """
    Sets up the Streamlit application configuration.

    Args:
        None

    Returns:
        None
    """
    st.set_page_config(
        layout="wide", page_title="AI Interview Questions Generator", page_icon="💼"
    )
    st.title("💼 AI Interview Questions Generator")
    st.markdown(
        "Welcome to the AI Interview Questions Generator! This app will help you generate personalized interview questions for a job role. Simply fill in the required fields and click the 'Generate Questions' button to get started."
    )
    st.sidebar.header("📌 Customize Your Questions")

    interview_question = st.sidebar.checkbox("Interview Question", key="interivew_question")
    resume_analyzer =  st.sidebar.checkbox("Resume Analyzer", key="resume_analyzer")
    if interview_question:
        role = st.sidebar.text_input("🔍 Job Role", placeholder="e.g. Data Scientist")
        skills = ""
        experience = ""
        projects = ""
        num_questions = st.sidebar.slider("🔥 Number of Questions", 1, 20, 10)

        uploaded_file = st.sidebar.file_uploader(
            "📂 Upload & Parse Resume (Optional)", type=["pdf"], accept_multiple_files=False
        )

        resume_text = ""

        if uploaded_file is not None:
            resume_text = extract_resume_content_from_file(uploaded_file)
            st.success("✅ Resume Uploaded & Parsed Successfully!")
        else:
            skills = st.sidebar.text_area(
                "🛠️ Key Skills",
                placeholder="e.g. Python, Machine Learning, Data Structures",
                height=100,
            )
            experience = st.sidebar.text_area(
                "💼 Work Experience",
                placeholder="e.g. 2 years in software development",
                height=100,
            )
            projects = st.sidebar.text_area(
                "🚀 Projects", placeholder="e.g. Built a recommendation system", height=100
            )

        if st.sidebar.button("🚀 Generate Questions"):
            if (
                not role
                or (not skills and not resume_text)
                or (not experience and not resume_text)
                or (not projects and not resume_text)
            ):
                st.warning("⚠️ Please fill in all fields before generating questions.")
            questions = generate_questions(
                role=role,
                skills=skills,
                experience=experience,
                projects=projects,
                num_questions=num_questions,
                resume_content=resume_text,
            )
            st.success("✅ Questions Generated!")
            st.write("\n".join(questions))

            generate_pdf("\n".join(questions), "Interview_Questions.pdf")
            with open("Interview_Questions.pdf", "rb") as file:
                st.download_button(
                    "📄 Download Questions as PDF",
                    file,
                    "Interview_Questions.pdf",
                    "application/pdf",
                )
    if resume_analyzer:
        role = st.sidebar.text_input("🔍 Job Role", placeholder="e.g. Data Scientist")
        uploaded_file = st.sidebar.file_uploader(
            "📂 Upload & Parse Resume (Optional)", type=["pdf"], accept_multiple_files=False
        )
        resume_text = ""

        if uploaded_file is not None:
            resume_text = extract_resume_content_from_file(uploaded_file)
            st.success("✅ Resume Uploaded & Parsed Successfully!")

        if st.sidebar.button("🔍 Analyze Resume"):
            if not role or not resume_text:
                st.warning("⚠️ Please fill in all fields before analyzing resume.")
            analysis = analyze_resume(resume_text, role)
            st.success("✅ Resume Analyzed!")
            st.write(analysis)

            generate_pdf(analysis, "Resume_Analysis.pdf")
            with open("Resume_Analysis.pdf", "rb") as file:
                st.download_button(
                    "📄 Download Questions as PDF",
                    file,
                    "Resume_Analysis.pdf",
                    "application/pdf",
                )
        
if __name__ == "__main__":
    init()
    setup_streamlit_app()
