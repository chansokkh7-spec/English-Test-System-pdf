import streamlit as st
import fitz
import google.generativeai as genai
import json
import re

# --- 1. API SETUP ---
# Secure your API Key
GOOGLE_API_KEY = "AIzaSyBfDSDxtCJbypPcLaR2kEagUQfXLQBWXcY"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="AI Quiz System", layout="wide")

# --- 2. FUNCTIONS ---
def get_text(file):
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        # Read a maximum of 15 pages to stay within prompt limits
        for i in range(min(len(doc), 15)):
            text += doc[i].get_text()
        return text.strip()
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

def create_quiz(text, count):
    if not text:
        st.error("The PDF appears to be empty or an image (not readable text).")
        return None

    prompt = f"""
    Create {count} English Multiple Choice Questions based on the text below.
    Return ONLY a valid JSON list of objects.
    Structure: [{{"id":1,"question":"...","options":["choice1","choice2","choice3","choice4"],"correct":"a"}}]
    
    Rules:
    - Options must be a list of 4 strings.
    - 'correct' must be a single letter: 'a', 'b', 'c', or 'd'.
    
    Text content:
    {text[:7000]}
    """
    
    try:
        response = model.generate_content(prompt)
        raw_output = response.text
        
        # --- REINFORCED JSON CLEANING ---
        # This removes markdown code blocks like ```json ... ```
        json_match = re.search(r'\[.*\]', raw_output, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            # Fallback for plain text response
            return json.loads(raw_output.strip())
    except Exception as e:
        st.error(f"AI Error: {e}")
        return None

# --- 3. UI ---
st.title("🎓 AI English Exam Generator")

if 'quiz' not in st.session_state:
    st.session_state.quiz = []

file = st.file_uploader("Upload PDF", type="pdf")

if file:
    num = st.sidebar.slider("Number of Questions", 5, 20, 10)
    if st.button("Generate Test ✨"):
        with st.spinner("AI is analyzing the document..."):
            # Reset file pointer before reading
            file.seek(0)
            txt = get_text(file)
            questions = create_quiz(txt, num)
            
            if questions:
                st.session_state.quiz = questions
                st.success("Test Generated Successfully!")
            else:
                st.warning("AI failed to format the questions. Please click 'Generate' again.")

# --- 4. TEST FORM ---
if st.session_state.quiz:
    with st.form("test_form"):
        user_ans = {}
        for q in st.session_state.quiz:
            st.write(f"**Q{q['id']}: {q['question']}**")
            # Map a,b,c,d to the option list
            opts = [f"(a) {q['options'][0]}", f"(b) {q['options'][1]}", f"(c) {q['options'][2]}", f"(d) {q['options'][3]}"]
            ans = st.radio("Select answer:", opts, key=f"q{q['id']}", index=None, label_visibility="collapsed")
            user_ans[q['id']] = ans[1] if ans else None
            st.write("---")
        
        if st.form_submit_button("Submit & Check Score"):
            score = 0
            for q in st.session_state.quiz:
                correct = q['correct'].lower()
                if user_ans[q['id']] == correct:
                    st.success(f"Q{q['id']}: Correct! (Answer: {correct})")
                    score += 1
                else:
                    st.error(f"Q{q['id']}: Wrong! (The correct answer was: {correct})")
            
            st.subheader(f"Total Score: {score}/{len(st.session_state.quiz)}")
            if score == len(st.session_state.quiz):
                st.balloons()
