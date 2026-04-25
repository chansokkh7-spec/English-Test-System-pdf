import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import json

# --- 1. CONFIGURATION ---
# Your API Key is hardcoded here
GOOGLE_API_KEY = "AIzaSyBfDSDxtCJbypPcLaR2kEagUQfXLQBWXcY"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="AI Exam System", layout="wide")

# --- 2. LOGIC FUNCTIONS ---

def get_pdf_text(file):
    """Reads PDF content safely."""
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    # We read first 15 pages to stay within AI limits
    limit = min(len(doc), 15)
    for i in range(limit):
        text += doc[i].get_text()
    return text, len(doc)

def ask_gemini(context, count):
    """Uses AI to generate questions."""
    prompt = f"""
    Create {count} English grammar multiple-choice questions based on this text.
    Return ONLY a JSON list. 
    Format: [{"id": 1, "question": "...", "options": ["a", "b", "c", "d"], "correct": "a"}]
    Text: {context[:9000]}
    """
    try:
        response = model.generate_content(prompt)
        # Remove any markdown backticks
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except:
        return None

# --- 3. SESSION STATE ---
if 'quiz' not in st.session_state:
    st.session_state.quiz = []

# --- 4. UI ---
st.title("🎓 Universal AI Exam Generator")
st.write("Upload any PDF book to create an instant test.")

uploaded_file = st.file_uploader("Upload PDF", type="pdf")

if uploaded_file:
    num_q = st.sidebar.slider("Number of Questions", 5, 20, 10)
    
    if st.button("Generate Quiz ✨"):
        with st.spinner("AI is reading the book..."):
            text_data, total_pg = get_pdf_text(uploaded_file)
            questions = ask_gemini(text_data, num_q)
            if questions:
                st.session_state.quiz = questions
                st.success(f"Generated {len(questions)} questions from the book!")
            else:
                st.error("AI Busy. Please click the button again.")

# --- 5. DISPLAY QUIZ ---
if st.session_state.quiz:
    st.divider()
    with st.form("exam_form"):
        user_picks = {}
        for q in st.session_state.quiz:
            st.write(f"**Q{q['id']}: {q['question']}**")
            # Build choice labels
            choices = [f"(a) {q['options'][0]}", f"(b) {q['options'][1]}", f"(f) {q['options'][2]}", f"(d) {q['options'][3]}"]
            pick = st.radio("Select answer:", choices, key=f"ans_{q['id']}", index=None, label_visibility="collapsed")
            user_picks[q['id']] = pick[1] if pick else None
            st.write("---")
        
        if st.form_submit_button("Submit and Show Score"):
            score = 0
            for q in st.session_state.quiz:
                right_ans = q['correct'].lower()
                if user_picks[q['id']] == right_ans:
                    st.success(f"Q{q['id']}: Correct!")
                    score += 1
                else:
                    st.error(f"Q{q['id']}: Incorrect. Correct answer was ({right_ans})")
            
            st.subheader(f"Total Score: {score}/{len(st.session_state.quiz)}")
            if score == len(st.session_state.quiz):
                st.balloons()
