import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import json

# --- 1. CONFIGURATION ---
# Your API Key is already embedded
GOOGLE_API_KEY = "AIzaSyBfDSDxtCJbypPcLaR2kEagUQfXLQBWXcY"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="AI Grammar Quiz", layout="wide")

# --- 2. FUNCTIONS ---

def extract_text(uploaded_file):
    """Extract text from PDF (Supports up to 5000 pages)"""
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    # Read first 20 pages to avoid hitting AI token limits at once
    # For a 5000-page book, we pick a sample or read in chunks
    for i in range(min(len(doc), 20)): 
        text += doc[i].get_text()
    return text

def generate_quiz(text, num_q):
    """Send text to Gemini AI to get questions"""
    prompt = f"""
    Based on the text provided, create {num_q} multiple-choice questions.
    Each question must have 4 options (a, b, c, d) and a correct answer.
    Return the result ONLY as a JSON list.
    Example: [{"id":1, "question":"...", "options":["...","...","...","..."], "correct":"a"}]
    Text: {text[:8000]}
    """
    try:
        response = model.generate_content(prompt)
        clean_json = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(clean_json)
    except Exception as e:
        return None

# --- 3. UI LAYOUT ---
st.title("🎓 AI English Test System (Universal)")
st.info("Upload any PDF book. AI will read it and create a test for you.")

if 'questions' not in st.session_state:
    st.session_state.questions = []

file = st.file_uploader("Upload PDF", type="pdf")

if file:
    num_q = st.sidebar.slider("Number of Questions", 5, 20, 10)
    if st.button("Generate Test ✨"):
        with st.spinner("AI is analyzing the book..."):
            book_text = extract_text(file)
            st.session_state.questions = generate_quiz(book_text, num_q)
            if st.session_state.questions:
                st.success("Test Generated!")
            else:
                st.error("AI Error. Please try clicking the button again.")

# --- 4. DISPLAY QUIZ ---
if st.session_state.questions:
    with st.form("quiz_form"):
        user_answers = {}
        for q in st.session_state.questions:
            st.write(f"**Q{q['id']}: {q['question']}**")
            opts = [f"(a) {q['options'][0]}", f"(b) {q['options'][1]}", f"(c) {q['options'][2]}", f"(d) {q['options'][3]}"]
            ans = st.radio(f"Select for Q{q['id']}", opts, key=f"q_{q['id']}", index=None, label_visibility="collapsed")
            user_answers[q['id']] = ans[1] if ans else None
            st.write("---")
        
        if st.form_submit_button("Submit Answers"):
            score = 0
            for q in st.session_state.questions:
                if user_answers[q['id']] == q['correct'].lower():
                    st.success(f"Q{q['id']}: Correct!")
                    score += 1
                else:
                    st.error(f"Q{q['id']}: Wrong! Correct is ({q['correct']})")
            st.subheader(f"Your Score: {score}/{len(st.session_state.questions)}")
