
import streamlit as st
import time
import openai
import os

openai.api_key = "PASTE_YOUR_API_KEY_HERE"

TOTAL_TIME = 200 * 60

st.set_page_config(page_title="NEET AI Exam", layout="wide")

def generate_mcqs(subject, count):
    prompt = f"""
    Generate {count} NEET MCQs from NCERT {subject}
    with answers and NCERT explanations.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def exam_timer():
    if "start" not in st.session_state:
        st.session_state.start = time.time()
    left = TOTAL_TIME - int(time.time() - st.session_state.start)
    st.sidebar.write(f"⏱ Time Left: {left//60}:{left%60}")

st.title("REAL NEET EXAM MODE")
exam_timer()

if "paper" not in st.session_state:
    st.session_state.paper = {
        "Physics": generate_mcqs("Physics",45),
        "Chemistry": generate_mcqs("Chemistry",45),
        "Biology": generate_mcqs("Biology",90)
    }

subject = st.selectbox("Section",["Physics","Chemistry","Biology"])
st.markdown(st.session_state.paper[subject])
