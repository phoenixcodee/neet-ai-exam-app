import streamlit as st
import json

st.set_page_config(page_title="NEET Offline Practice", layout="centered")

# -------------------- LOAD DATA --------------------
def load_mcqs(subject):
    with open(f"mcqs/{subject.lower()}.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_layout():
    with open("config/layout.json", "r") as f:
        return json.load(f)

layout = load_layout()

# -------------------- NCERT BOOK LINKS --------------------
ncert_links = {
    "Biology": "https://ncert.nic.in/textbook.php?lebo1=0-22",
    "Physics": "https://ncert.nic.in/textbook.php?leph1=0-2",
    "Chemistry": "https://ncert.nic.in/textbook.php?lech1=0-2"
}

# -------------------- SESSION STATE --------------------
if "page" not in st.session_state:
    st.session_state.page = "Home"

if "score" not in st.session_state:
    st.session_state.score = 0

if "total" not in st.session_state:
    st.session_state.total = 0

if "answers" not in st.session_state:
    st.session_state.answers = {}

# -------------------- NAVIGATION --------------------
def go(page):
    st.session_state.page = page
    try:
        st.experimental_rerun()
    except st.script_runner.RerunException:
        pass

# -------------------- HOME PAGE --------------------
def home():
    st.title(layout["app_title"])
    st.subheader("NCERT Based | Real Exam Pattern")

    for idx, item in enumerate(layout["home_menu"]):
        if st.button(item["title"], key=f"home_{idx}"):
            go(item["page"])
        st.caption(item["description"])

# -------------------- BOOKS PAGE --------------------
def books_page():
    st.title("📚 NCERT Official Textbooks")

    for subject, link in ncert_links.items():
        st.markdown(f"### {subject}")
        st.markdown(f"[🔗 Open Official NCERT Book]({link})")

    st.button("⬅ Back", on_click=go, args=("Home",))

# -------------------- PRACTICE PAGE --------------------
def practice_page():
    st.title("📝 MCQ Practice")

    subject = st.selectbox("Select Subject", layout["subjects"])

    # Load MCQs
    mcq = load_mcq(subject)

    # Initialize answers if not already set
    if subject not in st.session_state.answers:
        st.session_state.answers[subject] = {}

    for i, q in enumerate(mcqs):
        st.markdown(f"**Q{i+1}. {q['question']}**")
        st.session_state.answers[subject][i] = st.radio(
            "Choose option:",
            list(q["options"].keys()),
            key=f"{subject}_{i}",
            index=list(q["options"].keys()).index(
                st.session_state.answers[subject].get(i, list(q["options"].keys())[0])
            )
        )

    if st.button("✅ Submit"):
        calculate_result(subject, mcqs)

# -------------------- RESULT PAGE --------------------
def calculate_result(subject, mcqs):
    score = 0
    scheme = layout["marking_scheme"]

    for i, q in enumerate(mcqs):
        selected = st.session_state.answers[subject].get(i)
        if selected == q["answer"]:
            score += scheme["correct"]
        elif selected:
            score += scheme["wrong"]

    st.session_state.score = score
    st.session_state.total = len(mcqs) * scheme["correct"]
    st.session_state.page = "Result"

    try:
        st.experimental_rerun()
    except st.script_runner.RerunException:
        pass

def result_page():
    st.title("📊 Result")

    st.success(f"Score: {st.session_state.score} / {st.session_state.total}")

    if st.session_state.score >= st.session_state.total * 0.6:
        st.balloons()
        st.success("🏆 PASSED (Certificate Eligible)")

    st.button("🏠 Home", on_click=go, args=("Home",))

# -------------------- ROUTER --------------------
if st.session_state.page == "Home":
    home()
elif st.session_state.page == "Books":
    books_page()
elif st.session_state.page == "Practice":
    practice_page()
elif st.session_state.page == "Result":
    result_page()
