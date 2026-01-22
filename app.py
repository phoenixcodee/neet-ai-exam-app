import streamlit as st
import requests

# ================= CONFIG =================
API_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_API_KEY = st.secrets["MISTRAL_API_KEY"]

HEADERS = {
    "Authorization": f"Bearer {MISTRAL_API_KEY}",
    "Content-Type": "application/json"
}

NCERT_LINK = "https://ncert.nic.in/textbook.php"

# ================= NCERT BOOK STRUCTURE =================
NCERT_BOOKS = {
    "11": {
        "Botany": ["Cell Structure", "Plant Physiology"],
        "Zoology": ["Animal Kingdom", "Human Physiology"],
        "Chemistry": ["Structure of Atom", "Chemical Bonding"],
        "Physics": ["Kinematics", "Laws of Motion"]
    },
    "12": {
        "Botany": ["Reproduction in Plants", "Biotechnology"],
        "Zoology": ["Human Reproduction", "Genetics"],
        "Chemistry": ["Electrochemistry", "Coordination Compounds"],
        "Physics": ["Electrostatics", "Current Electricity"]
    }
}

# ================= INTENT DETECTION =================
def detect_intent(text):
    text = text.lower()
    if "ncert" in text:
        return "ncert"
    if "mcq" in text:
        return "mcq"
    if any(word in text for word in ["calculate", "find", "numerical", "solve"]):
        return "problem"
    return "theory"

# ================= AUTO SUBJECT DETECTION =================
def detect_subject(text):
    text = text.lower()
    if any(w in text for w in ["cell", "dna", "plant", "leaf"]):
        return "Botany"
    if any(w in text for w in ["animal", "human", "heart"]):
        return "Zoology"
    if any(w in text for w in ["atom", "reaction", "ph", "mole"]):
        return "Chemistry"
    if any(w in text for w in ["force", "current", "voltage", "velocity"]):
        return "Physics"
    return "Biology"

# ================= THEORY ANSWER =================
def generate_theory(question, subject, ncert_class):
    prompt = f"""
You are a NEET expert teacher.
Answer strictly based on NCERT Class {ncert_class}.
Subject: {subject}
Explain clearly in exam-oriented style.
Question: {question}
"""
    return call_mistral(prompt, 600)

# ================= PROBLEM SOLVER =================
def solve_problem(question, subject, ncert_class):
    prompt = f"""
You are a NEET expert.
Solve the following NCERT-based problem step by step.

Rules:
- Write Given
- Formula
- Substitution
- Calculation
- Final Answer

Subject: {subject}
Class: {ncert_class}
Question: {question}
"""
    return call_mistral(prompt, 800)

# ================= MCQ GENERATOR =================
def generate_mcqs(subject, ncert_class):
    chapter = NCERT_BOOKS[ncert_class][subject][0]
    prompt = f"""
Generate 10 NEET-level MCQs strictly from NCERT.
Subject: {subject}
Class: {ncert_class}
Chapter: {chapter}
Provide answer key with explanation.
"""
    return call_mistral(prompt, 1200)

# ================= MISTRAL CALL =================
def call_mistral(prompt, tokens):
    payload = {
        "model": "mistral-medium-latest",
        "messages": [
            {"role": "system", "content": "You are a NEET tutor."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": tokens
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    return response.json()["choices"][0]["message"]["content"]

# ================= STREAMLIT UI =================
st.set_page_config(page_title="NEET AI Tutor", page_icon="📘")
st.title("📘 NEET AI Tutor (NCERT Based)")

# Book Selection
col1, col2 = st.columns(2)
with col1:
    ncert_class = st.selectbox("Select Class", ["11", "12"])
with col2:
    subject = st.selectbox("Select Subject", ["Botany", "Zoology", "Chemistry", "Physics"])

st.caption("Step-by-step Physics & Chemistry problem solving enabled ✅")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask NEET question / Solve numerical / Generate MCQs")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    intent = detect_intent(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            if intent == "ncert":
                response = f"📗 [Official NCERT Books]({NCERT_LINK})"

            elif intent == "mcq":
                response = generate_mcqs(subject, ncert_class)

            elif intent == "problem":
                response = solve_problem(user_input, subject, ncert_class)

            else:
                response = generate_theory(user_input, subject, ncert_class)

            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": r_
