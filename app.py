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
    if any(w in text for w in ["solve", "calculate", "numerical", "find"]):
        return "problem"
    return "theory"

# ================= SUBJECT DETECTION =================
def detect_subject(text):
    text = text.lower()
    if any(w in text for w in ["force", "current", "voltage", "motion", "energy"]):
        return "Physics"
    if any(w in text for w in ["atom", "reaction", "mole", "ph"]):
        return "Chemistry"
    if any(w in text for w in ["plant", "leaf", "photosynthesis"]):
        return "Botany"
    if any(w in text for w in ["animal", "heart", "human"]):
        return "Zoology"
    return "Biology"

# ================= AUTO CLASS DETECTION (BACKGROUND) =================
def auto_detect_class_for_problem(text, subject):
    text = text.lower()

    if subject == "Physics":
        class11 = ["motion", "velocity", "acceleration", "work", "energy", "laws of motion"]
        class12 = ["electric", "current", "potential", "capacitance", "magnetic", "ray optics"]

    elif subject == "Chemistry":
        class11 = ["mole", "atomic", "periodic", "thermodynamics", "equilibrium"]
        class12 = ["electrochemistry", "coordination", "kinetics", "surface chemistry"]

    else:
        class11 = ["cell", "tissue", "plant", "animal"]
        class12 = ["genetics", "reproduction", "biotechnology"]

    if any(k in text for k in class12):
        return "12"
    return "11"

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
def generate_theory(question, subject):
    prompt = f"""
Answer strictly from NCERT.
Explain clearly in NEET exam style.

Subject: {subject}

Question:
{question}
"""
    return call_mistral(prompt, 600)

# ================= PROBLEM SOLVER =================
def solve_problem(question, subject):
    ncert_class = auto_detect_class_for_problem(question, subject)

    if ncert_class == "11":
        scope = "Use ONLY NCERT Class 11 formulas and simple explanations."
    else:
        scope = "Use ONLY NCERT Class 12 formulas with detailed derivation."

    prompt = f"""
You are a NEET expert teacher.

{scope}

Follow this format strictly:
1. Given
2. Formula
3. Substitution
4. Calculation
5. Final Answer

Subject: {subject}
NCERT Class: {ncert_class}

Problem:
{question}
"""
    return call_mistral(prompt, 900)

# ================= MCQ GENERATOR =================
def generate_mcqs(subject):
    ncert_class = auto_detect_class_for_problem(subject, subject)
    prompt = f"""
Generate 10 NEET-level MCQs strictly from NCERT.

Subject: {subject}
NCERT Class: {ncert_class}

Provide answers with brief explanation.
"""
    return call_mistral(prompt, 1200)

# ================= STREAMLIT UI =================
st.set_page_config(page_title="NEET AI Tutor", page_icon="📘")
st.title("📘 NEET AI Tutor (NCERT Based)")
st.caption("Smart Class Detection • Step-by-Step Numericals")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask NEET questions or solve problems")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    intent = detect_intent(user_input)
    subject = detect_subject(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            if intent == "ncert":
                response = (
                    "📘 [NCERT Class 11 Books](https://ncert.nic.in/textbook.php?lebo1=0-16)\n\n"
                    "📗 [NCERT Class 12 Books](https://ncert.nic.in/textbook.php?lebo1=17-32)"
                )

            elif intent == "mcq":
                response = generate_mcqs(subject)

            elif intent == "problem":
                response = solve_problem(user_input, subject)

            else:
                response = generate_theory(user_input, subject)

            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

st.markdown("---")
st.markdown("🎯 NEET Focused • NCERT Strict • Intelligent Class Handling")
