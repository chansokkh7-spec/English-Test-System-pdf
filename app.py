import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import json
import re

# --- ១. ការកំណត់ API (ប្រើម៉ូដែលចុងក្រោយបំផុត) ---
API_KEY = "AIzaSyBfDSDxtCJbypPcLaR2kEagUQfXLQBWXcY"
genai.configure(api_key=API_KEY)

# ប្រើឈ្មោះ gemini-1.5-flash ដើម្បីការពារ Error 404
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="AI Exam System", layout="wide")

# --- ២. មុខងារទាញយកអត្ថបទពី PDF ---
def get_pdf_text(file):
    try:
        # Reset file pointer មុនពេលអាន
        file.seek(0)
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        # អានតែ ៥ ទំព័រដំបូងដើម្បីការពារការគាំង
        for i in range(min(len(doc), 5)):
            text += doc[i].get_text()
        return text.strip()
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

# --- ៣. UI និងការគ្រប់គ្រងសំណួរ ---
if 'quiz' not in st.session_state:
    st.session_state.quiz = []

st.title("🎓 បង្កើតសំណួរតេស្តចេញពី PDF (Version 2026)")

uploaded_file = st.file_uploader("Upload ឯកសារ PDF របស់អ្នក", type="pdf")

if uploaded_file:
    if st.button("Generate Quiz ✨"):
        with st.spinner("AI កំពុងវិភាគសៀវភៅ និងបង្កើតសំណួរ..."):
            raw_text = get_pdf_text(uploaded_file)
            
            if raw_text:
                # Prompt សម្រាប់ទាញយកសំណួរ
                prompt = "Create 5 English multiple choice questions from the text provided. "
                prompt += "Return ONLY a JSON list. "
                prompt += 'Format: [{"id":1, "question":"...", "options":["a","b","c","d"], "correct":"a"}] '
                prompt += "\n\nText: " + raw_text[:5000]
                
                try:
                    response = model.generate_content(prompt)
                    # សម្អាតយកតែ JSON (Regex)
                    json_data = re.search(r'\[.*\]', response.text, re.DOTALL)
                    
                    if json_data:
                        st.session_state.quiz = json.loads(json_data.group())
                        st.success("ជោគជ័យ! បង្កើតសំណួរបានរួចរាល់។")
                    else:
                        st.error("AI ផ្ញើទិន្នន័យខុសទម្រង់។ សូមចុចប៊ូតុងម្ដងទៀត។")
                except Exception as e:
                    st.error(f"API Error: {e}")
            else:
                st.error("មិនអាចអានអត្ថបទពី PDF នេះបានទេ។ សូមប្រើ PDF ដែលមានអក្សរ (មិនមែនរូបថត)។")

# --- ៤. ការបង្ហាញសំណួរ និងការដាក់ពិន្ទុ ---
if st.session_state.quiz:
    st.divider()
    with st.form("exam_form"):
        user_answers = {}
        for q in st.session_state.quiz:
            st.subheader(f"Question {q['id']}: {q['question']}")
            
            # បង្ហាញជម្រើសចម្លើយ
            choice = st.radio(
                "ជ្រើសរើសចម្លើយ៖", 
                q['options'], 
                key=f"q_key_{q['id']}", 
                index=None
            )
            user_answers[q['id']] = choice
            st.write("---")
            
        if st.form_submit_button("Submit & Check Score"):
            score = 0
            for q in st.session_state.quiz:
                # កំណត់លំដាប់ចម្លើយ a, b, c, d
                correct_letter = q['correct'].lower().strip()
                correct_index = ord(correct_letter) - 97
                correct_text = q['options'][correct_index]
                
                if user_answers[q['id']] == correct_text:
                    st.success(f"Q{q['id']}: ត្រឹមត្រូវ! ✅")
                    score += 1
                else:
                    st.error(f"Q{q['id']}: ខុស! ចម្លើយត្រឹមត្រូវគឺ: {correct_text} ❌")
            
            st.subheader(f"លទ្ធផលសរុប: {score} / {len(st.session_state.quiz)}")
            if score == len(st.session_state.quiz):
                st.balloons()
