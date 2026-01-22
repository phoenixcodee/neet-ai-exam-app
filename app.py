import streamlit as st
import requests

# ================= CONFIG =================
API_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_API_KEY = st.secrets["MISTRAL_API_KEY"]

HEADERS = {
    "Authorization": f"Bearer {MISTRAL_API_KEY}",
    "Content-Type": "application/json"
}

# ================= NCERT LINKS =================
NCERT_BOOK_LINKS = {
    "11": "https://ncert.nic.in/textbook.php?lebo1=0-16",
    "12": "https://ncert.nic.in/textbook.php?lebo1=17-32"
}

# ================= INTENT DETECTION =================
def detect_intent(text):
    text = text.lower()

    if "ncert" in text or "book" in text or "textbook" in text:
        return "ncert"
    if "mcq" in text:
        return "mcq"
    if any(word in text for word in ["calculate", "solve", "numerical", "find"]):
        return "problem"
    return "theory"

# ================= CLASS DETECTION (MANUAL ONLY) =================
def detect_class(text):
    text = text.lower()
    if "class 11" in text or "11th" in text:
        return "11"
    if "class 12" in text or "12th" in text:
        return "12"
    return None

# ================= SUBJECT DETECTION =================
def detect_subject(text):
    text = text.lower()

    if any(w in text for w in ["plant", "leaf", "photosynthesis", "xylem"]):
        return "Botany"
    if any(w in text for w in ["animal", "heart", "kidney", "human"]):
        return "Zoology"
    if any(w in text for w in ["atom", "reaction", "ph", "mole"]):
        return "Chemistry"
    if any(w in text for w in ["force", "current", "voltage", "velocity"]):
        return "Physics"

    return "Biology"

# ================= MISTRAL API CALL =================
def call_mistral(prompt, max_tokens):
    payload = {
        "model": "mistral-medium-latest",
        "messages": [
            {"role": "system", "content": "You are a NEET expert tutor."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": max_tokens
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)
    return response.json()["choices"][0]["message"]["content"]

# ================= THEORY =================
def generate_theory(question, subject, ncert_class):
    prompt = f"""
Answer strictly from NCERT.
Class: {ncert_class}
Subject: {subject}
Explain clearly in NEET exam style.

Question:
{question}
"""
    return call_mistral(prompt, 600)

# ================= PROBLEM SOLVER =================
def solve_problem(question, subject, ncert_class):
    prompt = f"""
Solve the NCERT-based problem step by step.

Rules:
- Given
- Formula
- Substitution
- Calculation
- Final Answer

Class: {ncert_class}
Subject: {subject}

Question:
{question}
"""
    return call_mistral(prompt, 800)

# ================= MCQ GENERATOR =================
def generate_mcqs(subject, ncert_class):
    prompt = f"""
Generate 10 NEET-level MCQs strictly from NCERT.

Class: {ncert_class}
Subject: {subject}

Rules:
- 4 options each
- Correct answer
- Short explanation
"""
    return call_mistral(prompt, 1200)

# ================= STREAMLIT UI =================
st.set_page_config(page_title="NEET AI Tutor", page_icon="📘")
st.title("📘 NEET AI Tutor (NCERT Based)")
st.caption("Manual Class Selection • Step-by-Step Numericals")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input(
    "Examples: 'NCERT Class 11 book', 'Solve this numerical', 'Generate MCQs'"
)

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    intent = detect_intent(user_input)
    ncert_class = detect_class(user_input)
    subject = detect_subject(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            if intent == "ncert":
                if ncert_class:
                    response = f"📘 [NCERT Class {ncert_class} Textbooks (Official)]({NCERT_BOOK_LINKS[ncert_class]})"
                else:
                    response = "❗ Please specify the class (Class 11 or Class 12)."

            elif intent == "mcq":
                if ncert_class:
                    response = generate_mcqs(subject, ncert_class)
                else:
                    response = "❗ Please mention Class 11 or Class 12 for MCQs."

            elif intent == "problem":
                if ncert_class:
                    response = solve_problem(user_input, subject, ncert_class)
                else:
                    response = "❗ Please mention Class 11 or Class 12 for problem solving."

            else:  # THEORY
                if ncert_class:
                    response = generate_theory(user_input, subject, ncert_class)
                else:
                    response = "❗ Please mention Class 11 or Class 12 for theory explanation."

            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

st.markdown("---")
st.markdown("🎯 NEET Focused • NCERT Strict • User-Controlled Output")
