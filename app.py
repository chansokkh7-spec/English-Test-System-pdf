import streamlit as st
import fitz
import google.generativeai as genai
import json
import re

# --- 1. API SETUP ---
# Using the API Key you provided
GOOGLE_API_KEY = "AIzaSyBfDSDxtCJbypPcLaR2kEagUQfXLQBWXcY"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="AI Quiz System", layout="wide")

# --- 2. LOGIC FUNCTIONS ---
def get_pdf_text(file):
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        # Limit to 10 pages for stability
        for i in range(min(len(doc), 10)):
            text += doc[i].get_text()
        return text.strip()
    except Exception as e:
        return ""

def call_gemini_ai(pdf_text, count):
    # Using Raw String (r''') to prevent Syntax/Value Errors with backslashes
    prompt = r'''
    You are an English teacher. Create {0} multiple choice questions based on the text provided.
    You must return ONLY a JSON list. No explanation text.
    
    JSON Structure Example:
    [
      {{"id": 1, "question": "What is...?", "options": ["Choice A", "Choice B", "Choice C", "Choice D"], "correct": "a"}}
    ]
    
    Text content:
    {1}
    '''.format(count, pdf_text[:7000])

    try:
        response = model.generate_content(prompt)
        res_text = response.text
        # Use Regex to find the JSON block [ ... ]
        match = re.search(r'\[.*\]', res_text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return None
    except Exception as e:
        return None

# --- 3. UI ---
st.title("🎓 Universal AI English Test")
st.info("Upload any PDF and click Generate. Results stay hidden until you submit.")

if 'questions' not in st.session_state:
    st.session_state.questions = []

uploaded_file = st.file_uploader("Upload PDF File", type="pdf")

if uploaded_file:
    num_q = st.sidebar.slider("Number of Questions", 5, 20, 10)
    
    if st.button("Generate Test ✨"):
        with st.spinner("AI is analyzing text..."):
            uploaded_file.seek(0)
            text = get_pdf_text(uploaded_file)
            if text:
                data = call_gemini_ai(text, num_q)
                if data:
                    st.session_state.questions = data
                    st.success("Test Generated!")
                else:
                    st.error("AI returned bad data. Try again.")
            else:
                st.error("Could not read PDF text.")

# --- 4. TEST FORM ---
if st.session_state.questions:
    with st.form("quiz_form"):
        user_answers = {}
        for q in st.session_state.questions:
            st.write(f"**Q{q['id']}: {q['question']}**")
            # Build choice labels
            choices = [f"(a) {q['options'][0]}", f"(b) {q['options'][1]}", f"(c) {q['options'][2]}", f"(d) {q['options'][3]}"]
            ans = st.radio("Select:", choices, key=f"ans_{q['id']}", index=None, label_visibility="collapsed")
            user_answers[q['id']] = ans[1] if ans else None
            st.write("---")
        
        if st.form_submit_button("Check Results"):
            score = 0
            for q in st.session_state.questions:
                correct = q['correct'].lower()
                if user_answers[q['id']] == correct:
                    st.success(f"Q{q['id']}: Correct! (Answer: {correct})")
                    score += 1
                else:
                    st.error(f"Q{q['id']}: Incorrect! (Correct was: {correct})")
            st.subheader(f"Score: {score}/{len(st.session_state.questions)}")
