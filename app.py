import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import json
import time

# --- 1. CONFIGURATION & API SETUP ---
# API Key របស់អ្នកត្រូវបានបញ្ចូលរួចរាល់
GOOGLE_API_KEY = "AIzaSyBfDSDxtCJbypPcLaR2kEagUQfXLQBWXcY" 
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Universal AI Quiz System", layout="wide")

# --- 2. FUNCTIONS ---

def extract_text_from_pdf(uploaded_file):
    """Extract text from any PDF file, even large ones."""
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    all_pages_text = []
    for page in doc:
        all_pages_text.append(page.get_text())
    return all_pages_text

def get_questions_via_ai(text_chunk, num_questions=5):
    """Use AI to understand the text and generate structured questions."""
    prompt = f"""
    Act as an English Professor. Analyze the following text and create {num_questions} 
    multiple-choice questions (MCQs). Each question must have 4 options (a, b, c, d) 
    and one correct answer.
    
    IMPORTANT: Return ONLY a valid JSON list. Do not include explanations.
    Format:
    [
      {{"id": 1, "question": "Question here", "options": ["Choice 1", "Choice 2", "Choice 3", "Choice 4"], "correct": "a"}},
      ...
    ]
    
    Text: {text_chunk}
    """
    try:
        response = model.generate_content(prompt)
        # Clean the response text to get pure JSON
        clean_json = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(clean_json)
    except Exception as e:
        st.error(f"AI Error: {e}")
        return []

# --- 3. SESSION STATE ---
if 'all_questions' not in st.session_state:
    st.session_state.all_questions = []
if 'test_generated' not in st.session_state:
    st.session_state.test_generated = False

# --- 4. USER INTERFACE ---
st.title("🎓 Universal AI English Quiz Generator")
st.info("Upload any PDF (Grammar, Stories, or Textbooks). AI will create a 100% accurate test for you.")

# Step 1: Upload File
uploaded_file = st.file_uploader("Upload your PDF book", type="pdf")

if uploaded_file:
    # Option to select range or number of questions
    num_q = st.sidebar.slider("Number of questions to generate", 5, 20, 10)
    
    if st.button("Generate Test Now ✨"):
        with st.spinner("AI is reading and analyzing your book..."):
            # Extract text
            pages = extract_text_from_pdf(uploaded_file)
            # Combine some pages to give AI enough context (e.g., first 5-10 pages)
            combined_text = "\n".join(pages[:10]) 
            
            # Get questions from AI
            questions = get_questions_via_ai(combined_text, num_questions=num_q)
            
            if questions:
                st.session_state.all_questions = questions
                st.session_state.test_generated = True
                st.success("Test Generated Successfully!")
            else:
                st.error("Failed to generate questions. Please try again.")

# Step 2: Display Test
if st.session_state.test_generated:
    st.write("---")
    st.header("📝 Interactive English Test")
    
    with st.form("quiz_form"):
        user_answers = {}
        for q in st.session_state.all_questions:
            st.write(f"**Question {q['id']}:** {q['question']}")
            
            # Display options
            opt_labels = [f"(a) {q['options'][0]}", f"(b) {q['options'][1]}", f"(c) {q['options'][2]}", f"(d) {q['options'][3]}"]
            choice = st.radio("Choose the correct answer:", opt_labels, key=f"q_{q['id']}", index=None)
            
            # Save user selection (extracting just 'a', 'b', 'c', or 'd')
            user_answers[q['id']] = choice[1] if choice else None
            st.write("---")
            
        submit_button = st.form_submit_button("Submit & Check Results")
        
        if submit_button:
            score = 0
            st.subheader("Your Results:")
            for q in st.session_state.all_questions:
                correct_ans = q['correct'].lower()
                user_ans = user_answers[q['id']]
                
                if user_ans == correct_ans:
                    st.success(f"✅ Q{q['id']}: Correct! (Answer: {correct_ans})")
                    score += 1
                else:
                    st.error(f"❌ Q{q['id']}: Incorrect! (Correct Answer: {correct_ans})")
            
            final_score = (score / len(st.session_state.all_questions)) * 100
            st.metric("Final Score", f"{final_score}%", f"{score}/{len(st.session_state.all_questions)}")
            
            if score == len(st.session_state.all_questions):
                st.balloons()
