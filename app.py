import streamlit as st
import time
import os
from dotenv import load_dotenv
from openai import OpenAI

# ---------------- CONFIG ----------------
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TOTAL_TIME = 200 * 60
MARKS_CORRECT = 4
MARKS_WRONG = -1

st.set_page_config(page_title="NEET AI Exam Platform", layout="wide")

# ---------------- AI MCQ GENERATOR ----------------
def generate_mcqs(subject, count):
    prompt = f"""
    Generate {count} NEET exam MCQs strictly from NCERT {subject}.

    Rules:
    - 4 options (A, B, C, D)
    - One correct answer
    - After each question include:
        Answer:
        NCERT Line Explanation:
    - Use NCERT textbook language only
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content


# ---------------- TIMER ----------------
def exam_timer():
    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()

    elapsed = int(time.time() - st.session_state.start_time)
    remaining = max(TOTAL_TIME - elapsed, 0)

    mins = remaining // 60
    secs = remaining % 60

    st.sidebar.markdown(f"⏱ **Time Left:** {mins:02d}:{secs:02d}")

    if remaining == 0:
        st.session_state.exam_submitted = True
        st.error("⏰ Time Over! Exam auto-submitted.")


# ---------------- NEET EXAM MODE ----------------
def neet_exam_mode():
    st.title("📝 REAL NEET EXAM MODE")

    exam_timer()

    if "questions" not in st.session_state:
        with st.spinner("Generating NEET Question Paper (NCERT Based)..."):
            st.session_state.questions = {
                "Physics": generate_mcqs("Physics", 45),
                "Chemistry": generate_mcqs("Chemistry", 45),
                "Biology": generate_mcqs("Biology", 90),
            }
            st.session_state.exam_submitted = False

    section = st.selectbox(
        "Select Section",
        ["Physics", "Chemistry", "Biology"]
    )

    st.markdown(st.session_state.questions[section])

    if st.button("📤 Submit Exam"):
        st.session_state.exam_submitted = True


# ---------------- RESULT PAGE ----------------
def result_page():
    st.title("📊 NEET Exam Result")

    attempted = 180
    correct = 120
    wrong = 40
    unattempted = 20

    score = (correct * MARKS_CORRECT) + (wrong * MARKS_WRONG)

    st.success(f"🎯 Total Score: {score} / 720")

    col1, col2, col3 = st.columns(3)
    col1.metric("Correct", correct)
    col2.metric("Wrong", wrong)
    col3.metric("Unattempted", unattempted)


# ---------------- MAIN NAVIGATION ----------------
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "📝 Real NEET Exam", "📊 Result"]
)

if page == "🏠 Home":
    st.title("🎓 NEET AI Exam Platform")
    st.markdown("""
    ### Features:
    - Real NEET exam pattern (180 Q / 200 min)
    - AI-generated NCERT-based questions
    - NCERT line-by-line explanations
    """)

elif page == "📝 Real NEET Exam":
    neet_exam_mode()

elif page == "📊 Result":
    result_page()
