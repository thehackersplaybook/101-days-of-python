import streamlit as st
import openai
import random
import os
import re
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("⚠️ OpenAI API Key is missing! Please check your .env file.")
else:
    openai.api_key = OPENAI_API_KEY  

if "test_active" not in st.session_state:
    st.session_state.test_active = False
if "mcqs" not in st.session_state:
    st.session_state.mcqs = []
if "answers" not in st.session_state:
    st.session_state.answers = []
if "current_index" not in st.session_state:
    st.session_state.current_index = 0
if "correct_answers" not in st.session_state:
    st.session_state.correct_answers = 0
if "name" not in st.session_state:
    st.session_state.name = ""
if "exam_name" not in st.session_state:
    st.session_state.exam_name = ""

def generate_mcqs(subject: str, num_questions: int, difficulty: int) -> list:
    """
    Generates multiple-choice questions for a given subject and difficulty level.

    Args:
        subject (str): The subject for which the questions are generated.
        num_questions (int): The number of questions to generate.
        difficulty (int): The difficulty level of the questions (1=Easy, 5=Hard).
        
    Returns:        
        list: The generated questions.
    """

    prompt = f"""
    You are an expert professor generating {num_questions} MCQs for "{subject}". 
    Difficulty: {difficulty} (1=Easy, 5=Hard). 
    Each question has 4 options with only one correct answer.
    
    Format:
    Q: <question>
    A) <option1>
    B) <option2>
    C) <option3>
    D) <option4>
    Answer: <correct_option>
    """

    try:
        with st.spinner("Generating AI-powered questions...",show_time=True):
            response = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )

            if not response.choices or not response.choices[0].message.content.strip():
                st.warning("⚠️ AI response was empty! Using sample questions instead.")
                return generate_sample_mcqs(subject, num_questions)

            return parse_questions(response.choices[0].message.content)

    except Exception as e:
        st.error(f"⚠️ Error generating questions: {e}. Using sample questions instead.")
        return generate_sample_mcqs(subject, num_questions)

def parse_questions(text: str) -> list:
    """
    Parses the text and extracts the multiple-choice questions.

    Args:
        text (str): The text containing the multiple-choice questions.
        
    Returns:        
        list: The parsed multiple-choice questions.
    """

    mcqs = []
    
    pattern = re.findall(r"Q\d+: (.*?)\nA\) (.*?)\nB\) (.*?)\nC\) (.*?)\nD\) (.*?)\nAnswer: (.*?)\n", text, re.DOTALL)

    for match in pattern:
        question, opt_a, opt_b, opt_c, opt_d, answer = match
        options = [opt_a, opt_b, opt_c, opt_d]
        correct_answer = re.sub(r"^[A-D]\) ", "", answer.strip())

        mcqs.append({
            "question": question.strip(),
            "options": options,
            "answer": correct_answer
        })

    return mcqs

def generate_sample_mcqs(subject: str, num_questions: int) -> list:
    """
    Generates sample multiple-choice questions for a given subject and number of questions.

    Args:
        subject (str): The subject for which the questions are generated.
        num_questions (int): The number of questions to generate.
        
    Returns:        
        list: The generated questions.
    """
    
    mcqs = []
    for i in range(num_questions):
        question = f"Sample Question {i+1} for {subject}?"
        options = ["Option A", "Option B", "Option C", "Option D"]
        correct_option = random.choice(options)
        mcqs.append({"question": question, "options": options, "answer": correct_option})
    return mcqs

st.set_page_config(page_title="AI MCQ Test", page_icon="📝", layout="wide")
st.title("📝 AI-Powered MCQ Assessment")
st.caption("Challenge your knowledge with AI-generated multiple-choice questions tailored to your subject and difficulty level.")

if not st.session_state.test_active:
    st.sidebar.header("⚙️ Test Configuration")

    with st.sidebar.form("test_settings"):
        st.subheader("🔍 Test Details")
        st.session_state.name = st.text_input("👤 Enter Your Name", placeholder="John Doe")
        st.session_state.exam_name = st.text_input("📚 Subject / Exam Name", placeholder="E.g., Data Structures, Physics")
        
        st.subheader("🎯 Customization Options")
        num_questions = st.number_input("❓ Number of Questions", min_value=1, max_value=50, value=10, step=1)
        difficulty = st.slider("📊 Difficulty Level", 1, 5, 3)

        start_test = st.form_submit_button("🚀 Start Test")

    if start_test:
        if not st.session_state.name or not st.session_state.exam_name:
            st.warning("⚠️ Please enter both your name and the exam name.")
        else:
            st.session_state.mcqs = generate_mcqs(st.session_state.exam_name, num_questions, difficulty)

            if not st.session_state.mcqs: 
                st.error("⚠️ Failed to generate questions. Please try again.")
            else:
                st.session_state.test_active = True
                st.session_state.current_index = 0
                st.session_state.correct_answers = 0
                st.session_state.answers = [None] * num_questions
                st.rerun()

if st.session_state.test_active:
    mcqs = st.session_state.mcqs
    index = st.session_state.current_index

    if index < len(mcqs):
        question_data = mcqs[index]
        st.subheader(f"Q{index+1}: {question_data['question']}")

        selected_option = st.radio(
            "Choose an answer:",
            question_data["options"],
            index=None,
            key=f"q{index}"
        )

        if st.button("Next"):
            if selected_option:
                st.session_state.answers[index] = selected_option
                if selected_option == question_data["answer"]:
                    st.session_state.correct_answers += 1
                st.session_state.current_index += 1
                st.rerun()
            else:
                st.warning("⚠️ Please select an option before proceeding!")

    else:
        st.success("🎉 Test Completed!")
        score = st.session_state.correct_answers
        total = len(mcqs)
        accuracy = (score / total) * 100 if total > 0 else 0  

        st.metric("📊 Score", f"{score} / {total}")
        st.progress(int(accuracy))
        st.caption(f"🎯 Accuracy: {accuracy:.2f}%")

        st.divider()

        if st.button("🔄 Restart Test"):
            st.session_state.test_active = False
            st.session_state.current_index = 0
            st.session_state.correct_answers = 0
            st.session_state.mcqs = []
            st.session_state.answers = []
            st.session_state.name = ""
            st.session_state.exam_name = ""
            st.rerun()
