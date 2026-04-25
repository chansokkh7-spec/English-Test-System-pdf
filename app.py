import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import json
import re

# --- ការកំណត់ API ---
API_KEY = "AIzaSyBfDSDxtCJbypPcLaR2kEagUQfXLQBWXcY"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="AI Exam Pro", layout="centered")
st.title("🎓 AI English Exam Generator")

# ១. កន្លែង Upload PDF
pdf_file = st.file_uploader("បញ្ចូលសៀវភៅ PDF របស់អ្នក", type="pdf")

if pdf_file:
    if st.button("Generate Test ✨"):
        with st.spinner("AI កំពុងអាន និងបង្កើតសំណួរ..."):
            try:
                # ២. ទាញយកអត្ថបទពី PDF
                doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
                text_content = ""
                for i in range(min(len(doc), 10)):  # អាន ១០ ទំព័រដំបូង
                    text_content += doc[i].get_text()
                
                # ពិនិត្យមើលថាអានអក្សរដាច់ដែរឬទេ
                if len(text_content.strip()) < 100:
                    st.error("❌ មិនអាចអានអត្ថបទបានទេ! PDF នេះអាចជា 'រូបភាពថត'។ សូមសាកល្បង PDF ផ្សេង។")
                else:
                    # ៣. ហៅ AI ឱ្យបង្កើតសំណួរ
                    prompt = f"""
                    Extract 5 English grammar questions from this text. 
                    Return ONLY a JSON list of objects.
                    Format: [{"id":1, "question":"...", "options":["a","b","c","d"], "correct":"a"}]
                    Text: {text_content[:6000]}
                    """
                    
                    response = model.generate_content(prompt)
                    # ប្រើ Regex ដើម្បីឆ្កឹះយកតែ JSON បើទោះជា AI និយាយច្រើនក៏ដោយ
                    json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
                    
                    if json_match:
                        st.session_state.quiz = json.loads(json_match.group())
                        st.success("✅ បង្កើតសំណួរបានជោគជ័យ!")
                    else:
                        st.error("⚠️ AI ផ្ញើទិន្នន័យមកខុសទម្រង់។ សូមចុចប៊ូតុងម្ដងទៀត។")
            except Exception as e:
                st.error(f"❌ កំហុសបច្ចេកទេស: {e}")

# ៤. បង្ហាញសំណួរ និងដាក់ពិន្ទុ
if 'quiz' in st.session_state:
    with st.form("exam_form"):
        user_answers = {}
        for q in st.session_state.quiz:
            st.write(f"**Q{q['id']}: {q['question']}**")
            choice = st.radio("ជ្រើសរើសចម្លើយ:", q['options'], key=f"q_{q['id']}", index=None)
            user_answers[q['id']] = choice
            st.write("---")
        
        if st.form_submit_button("Submit"):
            score = 0
            for q in st.session_state.quiz:
                if user_answers[q['id']] and user_answers[q['id']].startswith(f"({q['correct']})"):
                    score += 1
            st.subheader(f"ពិន្ទុរបស់អ្នកគឺ: {score}/{len(st.session_state.quiz)}")
