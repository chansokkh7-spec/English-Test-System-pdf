import streamlit as st
import fitz
import google.generativeai as genai
import json
import re

# --- 1. API SETUP ---
# Using your provided API Key
GOOGLE_API_KEY = "AIzaSyBfDSDxtCJbypPcLaR2kEagUQfXLQBWXcY"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="AI Quiz System", layout="wide")

# --- 2. CLEANING FUNCTION ---
def clean_illegal_chars(text):
    """Removes non-breaking spaces and other hidden formatting characters."""
    return text.replace('\u00a0', ' ').replace('\u202f', ' ').strip()

# --- 3. LOGIC FUNCTIONS ---
def get_pdf_content(file):
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        full_text = ""
        # Read first 15 pages to stay within AI limits
        for i in range(min(len(doc), 15)):
            full_text += doc[i].get_text()
        return clean_illegal_chars(full_text)
    except Exception as e:
        st.error(f"PDF Error: {e}")
        return ""

def call_ai_api(context_text, q_count):
    prompt = f"""
    Create {q_count} English grammar MCQs from the text below. 
    Return ONLY a JSON list. No intro text.
    Format: [{"id":1, "question":"...", "options":["a","b","c","d"], "correct":"a"}]
    Text: {context_text[:8000]}
    """
    try:
        response = model.generate_content(prompt)
        res_text = response.text
        # Extract JSON using Regex in case AI adds extra words
        match = re.search(r'\[.*\]', res_text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return None
    except Exception as e:
        st.error(f"AI Error: {e}")
        return None

# --- 4. STREAMLIT UI ---
st.title("🎓 Universal AI English Test")

if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = []

uploaded_pdf = st.file_uploader("Upload PDF File", type="pdf")

if uploaded_pdf:
    num_questions = st.sidebar.slider("Questions", 5, 20, 10)
    
    if st.button("Generate Test ✨"):
        with st.spinner("AI is reading your book..."):
            uploaded_pdf.seek(0)
            extracted_text = get_pdf_content(uploaded_pdf)
            
            if extracted_text:
                questions = call_ai_api(extracted_text, num_questions)
                if questions:
                    st.session_state.quiz_data = questions
                    st.success("Test Generated!")
                else:
                    st.warning("AI failed to create JSON. Please try again.")
            else:
                st.error("Could not read text from PDF.")

# --- 5. TEST DISPLAY ---
if st.session_state.quiz_data:
    with st.form("test_form"):
        user_selections = {}
        for q in st.session_state.quiz_data:
            st.write(f"**Q{q['id']}: {q['question']}**")
            # Build radio options
            choices = [f"(a) {q['options'][0]}", f"(b) {q['options'][1]}", f"(c) {q['options'][2]}", f"(d) {q['options'][3]}"]
            user_pick = st.radio("Select:", choices, key=f"ans_{q['id']}", index=None, label_visibility="collapsed")
            user_selections[q['id']] = user_pick[1] if user_pick else None
            st.write("---")
        
        if st.form_submit_button("Submit & See Score"):
            score = 0
            for q in st.session_state.quiz_data:
                correct_letter = q['correct'].lower()
                if user_selections[q['id']] == correct_letter:
                    st.success(f"Q{q['id']}: Correct! (Answer: {correct_letter})")
                    score += 1
                else:
                    st.error(f"Q{q['id']}: Incorrect! (Correct was: {correct_letter})")
            
            st.subheader(f"Final Score: {score}/{len(st.session_state.quiz_data)}")
