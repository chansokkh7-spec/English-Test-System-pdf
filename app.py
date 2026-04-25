import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import json
import re

# --- ១. ការកំណត់ API (កំណត់ឱ្យត្រូវតាម Version ថ្មី) ---
API_KEY = "AIzaSyBfDSDxtCJbypPcLaR2kEagUQfXLQBWXcY"
genai.configure(api_key=API_KEY)

# ប្រើឈ្មោះ model នេះដើម្បីការពារ Error 404 (សកល)
model = genai.GenerativeModel('gemini-pro')

st.set_page_config(page_title="AI Exam System", layout="wide")

# --- ២. មុខងារទាញយកអក្សរពី PDF ---
def get_pdf_text(file):
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        # យកតែ ៥ ទំព័រដំបូងដើម្បីកុំឱ្យវាគាំង (Memory Limit)
        for i in range(min(len(doc), 5)):
            text += doc[i].get_text()
        return text.strip()
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

# --- ៣. UI និងការគ្រប់គ្រងសំណួរ ---
if 'quiz' not in st.session_state:
    st.session_state.quiz = []

st.title("🎓 បង្កើតសំណួរតេស្តចេញពី PDF")

uploaded_file = st.file_uploader("Upload ឯកសារ PDF របស់អ្នក", type="pdf")

if uploaded_file:
    if st.button("Generate Quiz ✨"):
        with st.spinner("AI កំពុងបង្កើតសំណួរ... សូមរង់ចាំ..."):
            raw_text = get_pdf_text(uploaded_file)
            
            if raw_text:
                # បង្កើត Prompt ឱ្យសាមញ្ញបំផុតដើម្បីឱ្យ AI ឆ្លើយតបត្រូវ
                prompt = "Create 5 English MCQs from the text. Return ONLY a JSON list. "
                prompt += 'Format: [{"id":1, "question":"...", "options":["a","b","c","d"], "correct":"a"}] '
                prompt += "\n\nText: " + raw_text[:4000]
                
                try:
                    response = model.generate_content(prompt)
                    # សម្អាតទិន្នន័យ (យកតែ JSON ពីក្នុងចន្លោះ [ ])
                    json_data = re.search(r'\[.*\]', response.text, re.DOTALL)
                    
                    if json_data:
                        st.session_state.quiz = json.loads(json_data.group())
                        st.success("ជោគជ័យ! សំណួរត្រូវបានបង្កើតរួចរាល់។")
                    else:
                        st.error("AI ផ្ញើទិន្នន័យខុសទម្រង់។ សូមចុចប៊ូតុងម្ដងទៀត។")
                except Exception as e:
                    st.error(f"API Error: {e}")
            else:
                st.error("មិនអាចអានអត្ថបទពី PDF នេះបានទេ។")

# --- ៤. ការបង្ហាញសំណួរ (ទម្រង់តេស្តដែលអ្នកចង់បាន) ---
if st.session_state.quiz:
    st.divider()
    score = 0
    with st.form("exam_form"):
        for q in st.session_state.quiz:
            st.subheader(f"Question {q['id']}: {q['question']}")
            
            # បង្ហាញជម្រើសចម្លើយ
            user_choice = st.radio(
                "ជ្រើសរើសចម្លើយត្រឹមត្រូវ៖", 
                q['options'], 
                key=f"user_q_{q['id']}", 
                index=None
            )
            
            # ផ្ទៀងផ្ទាត់ចម្លើយ
            # correct_idx: a=0, b=1, c=2, d=3
            correct_letter = q['correct'].lower().strip()
            correct_index = ord(correct_letter) - 97
            
            if user_choice == q['options'][correct_index]:
                score += 1
            
            st.write("---")
            
        if st.form_submit_button("Submit & Check Result"):
            st.balloons()
            st.header(f"Your Score: {score} / {len(st.session_state.quiz)}")
            if score == len(st.session_state.quiz):
                st.success("អស្ចារ្យណាស់! អ្នកឆ្លើយត្រូវទាំងអស់! 🌟")
