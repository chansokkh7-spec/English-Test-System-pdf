import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import json
import re

# --- ការកំណត់ API ---
API_KEY = "AIzaSyBfDSDxtCJbypPcLaR2kEagUQfXLQBWXcY"
genai.configure(api_key=API_KEY)

# ប្រើ Model នេះដើម្បីការពារ Error 404
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Grammar Quiz System", layout="wide")

# --- មុខងារទាញយកអត្ថបទ ---
def get_pdf_text(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for i in range(min(len(doc), 10)):
        text += doc[i].get_text()
    return text

# --- ចុចបង្កើតសំណួរ ---
if 'quiz' not in st.session_state:
    st.session_state.quiz = []

st.title("📝 បង្កើតកម្រងសំណួរ PDF ទៅជាតេស")

uploaded_file = st.file_uploader("Upload PDF File", type="pdf")

if uploaded_file:
    if st.button("បង្កើតតេស្តឥឡូវនេះ"):
        with st.spinner("កំពុងដំណើរការ..."):
            raw_text = get_pdf_text(uploaded_file)
            
            # Prompt បែបសាមញ្ញដើម្បីឱ្យ AI ផ្ញើទិន្នន័យមកត្រឹមត្រូវ
            prompt = "Create 10 English grammar MCQs from this text. Return ONLY a JSON list. "
            prompt += 'Format: [{"id": 1, "question": "...", "options": ["a", "b", "c", "d"], "correct": "a"}] '
            prompt += "\n\nText: " + raw_text[:5000]
            
            response = model.generate_content(prompt)
            
            # ស្វែងរក JSON ក្នុងចម្លើយ AI
            match = re.search(r'\[.*\]', response.text, re.DOTALL)
            if match:
                st.session_state.quiz = json.loads(match.group())
                st.success("រកឃើញសំណួរចំនួន " + str(len(st.session_state.quiz)) + " ក្នុងផ្នែកនេះ")

# --- បង្ហាញសំណួរ (ទម្រង់ដូចកូដចាស់របស់អ្នក) ---
if st.session_state.quiz:
    st.write("---")
    score = 0
    with st.form("quiz_form"):
        for q in st.session_state.quiz:
            st.subheader(f"Q{q['id']}: {q['question']}")
            
            # រៀបចំ Choice
            choice = st.radio(
                f"ជ្រើសរើសចម្លើយសម្រាប់ Q{q['id']}:", 
                q['options'], 
                key=f"q_{q['id']}", 
                index=None
            )
            
            # ឆែកចម្លើយ
            correct_letter = q['correct'].lower().strip()
            # បំប្លែង a->0, b->1, c->2, d->3 ដើម្បីផ្ទៀងផ្ទាត់ជាមួយ options
            correct_idx = ord(correct_letter) - 97
            
            if choice == q['options'][correct_idx]:
                score += 1
            
            st.write("---")
            
        submit = st.form_submit_button("បញ្ជូនចម្លើយ")
        
        if submit:
            st.balloons()
            st.header(f"លទ្ធផលរបស់អ្នកគឺ: {score} / {len(st.session_state.quiz)}")
