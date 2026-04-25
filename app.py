import streamlit as st
import fitz
import google.generativeai as genai
import json

# --- 1. API SETUP ---
GOOGLE_API_KEY = "AIzaSyBfDSDxtCJbypPcLaR2kEagUQfXLQBWXcY"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="AI Quiz System", layout="wide")

# --- 2. FUNCTIONS ---
def get_text(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    # Read up to 20 pages to stay safe with AI limits
    for i in range(min(len(doc), 20)):
        text += doc[i].get_text()
    return text

def create_quiz(text, count):
    prompt = f"Create {count} English MCQs from this text. Return ONLY a JSON list. Format: "
    prompt += '[{"id":1,"question":"...","options":["a","b","c","d"],"correct":"a"}]'
    prompt += f"\n\nText: {text[:8000]}"
    try:
        response = model.generate_content(prompt)
        raw = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(raw)
    except:
        return None

# --- 3. UI ---
st.title("🎓 AI English Exam Generator")

if 'quiz' not in st.session_state:
    st.session_state.quiz = []

file = st.file_uploader("Upload PDF", type="pdf")

if file:
    num = st.sidebar.slider("Questions", 5, 20, 10)
    if st.button("Generate Test ✨"):
        with st.spinner("AI is thinking..."):
            txt = get_text(file)
            questions = create_quiz(txt, num)
            if questions:
                st.session_state.quiz = questions
                st.success("Test ready!")

# --- 4. TEST FORM ---
if st.session_state.quiz:
    with st.form("test_form"):
        user_ans = {}
        for q in st.session_state.quiz:
            st.write(f"**Q{q['id']}: {q['question']}**")
            opts = [f"(a) {q['options'][0]}", f"(b) {q['options'][1]}", f"(c) {q['options'][2]}", f"(d) {q['options'][3]}"]
            ans = st.radio("Answer:", opts, key=f"q{q['id']}", index=None, label_visibility="collapsed")
            user_ans[q['id']] = ans[1] if ans else None
            st.write("---")
        
        if st.form_submit_button("Submit"):
            score = 0
            for q in st.session_state.quiz:
                correct = q['correct'].lower()
                if user_ans[q['id']] == correct:
                    st.success(f"Q{q['id']}: Correct!")
                    score += 1
                else:
                    st.error(f"Q{q['id']}: Wrong! (Correct: {correct})")
            st.subheader(f"Score: {score}/{len(st.session_state.quiz)}")
