import streamlit as st
import json
import os
from streamlit.runtime.scriptrunner import RerunException  # Updated import for rerun

st.set_page_config(page_title="NEET Offline Practice", layout="centered")

# -------------------- LOAD DATA --------------------
def load_mcq(subject):
    """Load MCQs JSON file safely from 'mcq' folder"""
    path = os.path.join(os.path.dirname(__file__), "mcq", f"{subject.lower()}.json")
    if not os.path.exists(path):
        st.error(f"MCQ file for '{subject}' not found!\nExpected at: {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_layout():
    """Load layout configuration JSON safely"""
    path = os.path.join(os.path.dirname(__file__), "config", "layout.json")
    if not os.path.exists(path):
        st.error(f"Layout file not found!\nExpected at: {path}")
        return {}
    with open(path, "r", encoding="utf-8") as f:
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
    except RerunException:
        pass

# -------------------- HOME PAGE --------------------
def home():
    st.title(layout.get("app_title", "NEET Offline Practice"))
    st.subheader("NCERT Based | Real Exam Pattern")

    for idx, item in enumerate(layout.get("home_menu", [])):
        if st.button(item.get("title", f"Menu {idx}"), key=f"home_{idx}"):
            go(item.get("page", "Home"))
        st.caption(item.get("description", ""))

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

    subjects = layout.get("subjects", ["Biology", "Physics", "Chemistry"])
    subject = st.selectbox("Select Subject", subjects)

    # Load MCQs
    mcqs = load_mcq(subject)
    if not mcqs:
        st.warning("No MCQs found for this subject.")
        return

    # Initialize answers if not already set
    if subject not in st.session_state.answers:
        st.session_state.answers[subject] = {}

    for i, q in enumerate(mcqs):
        st.markdown(f"**Q{i+1}. {q['question']}**")
        options = list(q["options"].keys())
        default_index = 0
        if i in st.session_state.answers[subject]:
            default_index = options.index(st.session_state.answers[subject][i])
        st.session_state.answers[subject][i] = st.radio(
            "Choose option:",
            options,
            key=f"{subject}_{i}",
            index=default_index
        )

    if st.button("✅ Submit"):
        calculate_result(subject, mcqs)

# -------------------- RESULT PAGE --------------------
def calculate_result(subject, mcqs):
    score = 0
    scheme = layout.get("marking_scheme", {"correct": 1, "wrong": 0})

    for i, q in enumerate(mcqs):
        selected = st.session_state.answers[subject].get(i)
        if selected == q["answer"]:
            score += scheme.get("correct", 1)
        elif selected:
            score += scheme.get("wrong", 0)

    st.session_state.score = score
    st.session_state.total = len(mcqs) * scheme.get("correct", 1)
    st.session_state.page = "Result"

    try:
        st.experimental_rerun()
    except RerunException:
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
