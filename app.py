import streamlit as st
import time
from openai import OpenAI

# ================= CONFIG =================
st.set_page_config(
    page_title="NEET AI Exam Platform",
    layout="wide"
)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

TOTAL_TIME = 200 * 60
MARKS_CORRECT = 4
MARKS_WRONG = -1

# ================= NCERT LINKS =================
NCERT_LINKS = {
    "Physics": "https://ncert.nic.in/textbook.php?keph1=0-7",
    "Chemistry": "https://ncert.nic.in/textbook.php?kech1=0-6",
    "Biology": "https://ncert.nic.in/textbook.php?kebo1=0-19",
}

# ================= AI MCQ GENERATOR =================
def generate_mcqs(subject, count, mode="practice"):
    if mode == "exam":
        instruction = "Do NOT show answers or explanations."
    else:
        instruction = "Include Answer and NCERT Line Explanation."

    prompt = f"""
    Generate {count} NEET level MCQs strictly from NCERT {subject}.

    Rules:
    - 4 options (A, B, C, D)
    - One correct answer
    - {instruction}
    - Use NCERT textbook language
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content


# ================= TIMER =================
def exam_timer():
    if "start_time" not in st.session_state:
        st.session_state.start_time = time.time()

    elapsed = int(time.time() - st.session_state.start_time)
    remaining = max(TOTAL_TIME - elapsed, 0)

    mins, secs = divmod(remaining, 60)
    st.sidebar.markdown(f"⏱ **Time Left:** {mins:02d}:{secs:02d}")

    if remaining == 0:
        st.session_state.exam_submitted = True
        st.error("⏰ Time Over! Exam auto-submitted.")


# ================= HOME PAGE =================
def home_page():
    st.title("🎓 NEET AI Exam Platform")

    st.markdown("""
    ### What this app offers:
    - 📘 Official NCERT textbook access
    - 🧠 AI-powered MCQ practice
    - 📝 Real NEET exam simulation
    - 📊 Instant result & analysis
    """)

    st.subheader("📘 NCERT Textbooks (Official)")
    cols = st.columns(3)
    for col, (sub, link) in zip(cols, NCERT_LINKS.items()):
        with col:
            st.link_button(f"{sub} NCERT Book", link)


# ================= PRACTICE PAGE =================
def practice_page():
    st.title("🧠 MCQ Practice (NCERT Based)")

    subject = st.selectbox("Select Subject", list(NCERT_LINKS.keys()))
    count = st.slider("Number of Questions", 5, 50, 10)

    if st.button("🚀 Generate MCQs"):
        with st.spinner("Generating MCQs from NCERT..."):
            mcqs = generate_mcqs(subject, count, mode="practice")
            st.markdown(mcqs)


# ================= EXAM MODE =================
def exam_page():
    st.title("📝 REAL NEET EXAM MODE")

    exam_timer()

    if "exam_questions" not in st.session_state:
        with st.spinner("Generating NEET Question Paper..."):
            st.session_state.exam_questions = {
                "Physics": generate_mcqs("Physics", 45, "exam"),
                "Chemistry": generate_mcqs("Chemistry", 45, "exam"),
                "Biology": generate_mcqs("Biology", 90, "exam"),
            }
            st.session_state.exam_submitted = False

    section = st.selectbox(
        "Select Section",
        ["Physics", "Chemistry", "Biology"]
    )

    st.markdown(st.session_state.exam_questions[section])

    if st.button("📤 Submit Exam"):
        st.session_state.exam_submitted = True


# ================= RESULT PAGE =================
def result_page():
    st.title("📊 NEET Exam Result")

    # Dummy result (OMR logic can be added)
    correct, wrong, unattempted = 120, 40, 20
    score = (correct * MARKS_CORRECT) + (wrong * MARKS_WRONG)

    st.success(f"🎯 Score: {score} / 720")

    c1, c2, c3 = st.columns(3)
    c1.metric("Correct", correct)
    c2.metric("Wrong", wrong)
    c3.metric("Unattempted", unattempted)


# ================= NAVIGATION =================
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "📘 NCERT Books", "🧠 Practice MCQs", "📝 Real NEET Exam", "📊 Result"]
)

if page == "🏠 Home":
    home_page()

elif page == "📘 NCERT Books":
    home_page()

elif page == "🧠 Practice MCQs":
    practice_page()

elif page == "📝 Real NEET Exam":
    exam_page()

elif page == "📊 Result":
    result_page()
