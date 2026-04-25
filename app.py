import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import json

# --- 1. CONFIGURATION ---
# Your API Key
GOOGLE_API_KEY = "AIzaSyBfDSDxtCJbypPcLaR2kEagUQfXLQBWXcY"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Universal AI Grammar Quiz", layout="wide")

# --- 2. FUNCTIONS ---

def extract_text_range(uploaded_file, start_page, end_page):
    """Extracts text from a specific range of pages to handle large PDFs."""
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    # Ensure we don't exceed actual page count
    end_page = min(end_page, len(doc))
    for i in range(start_page, end_page):
        text += doc[i].get_text()
    return text, len(doc)

def generate_quiz_ai(text, num_q):
    """Sends sampled text to AI to generate structured JSON quiz."""
    prompt = f"""
    You are an English examiner. Based on the text provided, create {num_q} multiple-choice questions.
    Requirements:
    1. Each question must have 4 options: (a), (b), (c), (d).
    2. Provide the correct answer letter.
    3. Return ONLY a valid JSON list.
    
    Format Example:
    [
      {{"id": 1, "question": "example?", "options": ["opt1", "opt2", "opt3", "opt4"], "correct": "a"}}
    ]
    
    Text: {text[:10000]}
    """
    try:
        response = model.generate_content(prompt)
        # Clean AI response to ensure it's pure JSON
        raw_text = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(raw_text)
    except Exception as e:
        st.error(f"AI Generation Error: {e}")
        return None

# --- 3. SESSION STATE ---
if 'quiz_questions' not in st.session_state:
    st.session_state.quiz_questions = []

# --- 4. USER INTERFACE ---
st.title("🎓 Universal AI English Quiz Generator")
st.info("Upload any English book (up to 5,000 pages). AI will analyze it and build a test.")

pdf_file = st.file_uploader("Upload PDF File", type="pdf")

if pdf_file:
    # Sidebar for controls
    st.sidebar.header("Test Settings")
    total_pages_count = fitz.open(stream=pdf_file.getvalue(), filetype="pdf").page_count
    
    # Allow user to choose which part of the book to test on
    page_start = st.sidebar.number_input("Start Page", min_value=1, max_value=total_pages_count, value=1)
    page_end = st.sidebar.number_input("End Page", min_value=page_start, max_value=total_pages_count, value=min(page_start+10, total_pages_count))
    num_questions = st.sidebar.slider("Number of Questions", 5, 20, 10)

    if st.button("Generate Test ✨"):
        with st.spinner(f"AI is reading pages {page_start} to {page_end}..."):
            # Reset file pointer and read text
            pdf_file.seek(0)
            context_text, _ = extract_text_range(pdf_file, page_start-1, page_end)
            
            # Generate Quiz
            result = generate_quiz_ai(context_text, num_questions)
            if result:
                st.session_state.quiz_questions = result
                st.success("Test Generated Successfully!")

# --- 5. DISPLAY TEST ---
if st.session_state.quiz_questions:
    st.write("---")
    with st.form("exam_form"):
        student_answers = {}
        for q in st.session_state.quiz_questions:
            st.write(f"**Question {q['id']}:** {q['question']}")
            
            # Options labels
            labels = [f"(a) {q['options'][0]}", f"(b) {q['options'][1]}", f"(c) {q['options'][2]}", f"(d) {q['options'][3]}"]
            user_choice = st.radio(f"Select answer for Q{q['id']}", labels, key=f"user_q_{q['id']}", index=None, label_visibility="collapsed")
            
            # Store answer letter (a, b, c, or d)
            student_answers[q['id']] = user_choice[1] if user_choice else None
            st.write("---")
            
        if st.form_submit_button("Submit & Show Results"):
            score = 0
            st.subheader("Examination Results:")
            for q in st.session_state.quiz_questions:
                correct_letter = q['correct'].lower()
                if student_answers[q['id']] == correct_letter:
                    st.success(f"✅ Q{q['id']}: Correct!")
                    score += 1
                else:
                    st.error(f"❌ Q{q['id']}: Wrong! The correct answer was ({correct_letter})")
            
            st.metric("Your Final Score", f"{(score/len(st.session_state.quiz_questions))*100:.0f}%", f"{score}/{len(st.session_state.quiz_questions)}")
