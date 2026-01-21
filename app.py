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

# ================= NCERT CHAPTERS =================
# This is used to pick a default chapter for MCQs automatically
NCERT_CHAPTERS = {
    "11": {
        "Biology": ["The Cell", "Plant Physiology", "Human Physiology"],
        "Chemistry": ["Some Basic Concepts", "Structure of Atom", "Chemical Bonding"],
        "Physics": ["Physical world", "Kinematics", "Laws of Motion"]
    },
    "12": {
        "Biology": ["Reproduction", "Genetics", "Biotechnology"],
        "Chemistry": ["Solid State", "Solutions", "Electrochemistry"],
        "Physics": ["Electrostatics", "Current Electricity", "Magnetism"]
    }
}

# ================= INTENT DETECTION =================
def detect_intent(text):
    text = text.lower()
    if "ncert" in text:
        return "ncert"
    if "mcq" in text or "questions" in text or "generate mcq" in text:
        return "mcq"
    return "theory"

# ================= AUTO DETECT SUBJECT + CLASS =================
def auto_detect_subject_class(text):
    text = text.lower()
    # Biology keywords
    biology_keywords = ["cell", "photosynthesis", "reproduction", "genetics", "enzyme", "dna", "protein", "meiosis"]
    chemistry_keywords = ["atom", "bonding", "reaction", "solution", "acid", "base", "electrochemistry", "oxidation"]
    physics_keywords = ["force", "motion", "electric", "current", "magnetism", "kinematics", "energy"]

    if any(word in text for word in biology_keywords):
        return "Biology", "11"
    elif any(word in text for word in chemistry_keywords):
        return "Chemistry", "11"
    elif any(word in text for word in physics_keywords):
        return "Physics", "11"
    else:
        # default
        return "Biology", "11"

# ================= THEORY ANSWER =================
def generate_theory_answer(question, subject):
    prompt = f"""
You are a NEET expert teacher.
Answer strictly based on NCERT syllabus.
Subject: {subject}
Question: {question}
Rules:
- NCERT-aligned
- NEET exam style
- Simple, clear explanation
- No MCQs
"""
    payload = {
        "model": "mistral-medium-latest",
        "messages": [
            {"role": "system", "content": "You are a NEET tutor."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 600
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    return response.json()["choices"][0]["message"]["content"]

# ================= MCQ GENERATOR =================
def generate_mcqs(question):
    # Detect subject and class automatically
    subject, ncert_class = auto_detect_subject_class(question)
    # Pick the first chapter automatically
    chapter = NCERT_CHAPTERS[ncert_class][subject][0]

    prompt = f"""
Generate 10 NEET-level MCQs strictly from NCERT.
Subject: {subject}
Class: {ncert_class}
Chapter: {chapter}
Rules:
- NEET pattern
- NCERT only
- Provide correct answer and explanation
"""
    payload = {
        "model": "mistral-medium-latest",
        "messages": [
            {"role": "system", "content": "You are a NEET MCQ generator."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4,
        "max_tokens": 1200
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    return response.json()["choices"][0]["message"]["content"]

# ================= STREAMLIT UI =================
st.set_page_config(page_title="NEET AI Chatbot", page_icon="🧠")
st.title("🧠 NEET AI Chatbot")
st.caption("NCERT-Based Biology • Chemistry • Physics")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_input = st.chat_input("Ask NEET questions or type 'Generate MCQs'")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    intent = detect_intent(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            if intent == "ncert":
                response = f"📘 [Official NCERT Website]({NCERT_LINK})"

            elif intent == "mcq":
                response = generate_mcqs(user_input)

            else:  # theory
                subject, ncert_class = auto_detect_subject_class(user_input)
                response = generate_theory_answer(user_input, subject)

            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

st.markdown("---")
st.markdown("🎯 Designed for NEET Aspirants | NCERT Focused | AI Powered")
