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
        with st.spinner("AI កំពុងវិភាគ និងបង្កើតសំណួរ..."):
            try:
                # ២. ទាញយកអត្ថបទពី PDF
                doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
                text_content = ""
                for i in range(min(len(doc), 10)):  # អាន ១០ ទំព័រដំបូង
                    text_content += doc[i].get_text()
                
                if len(text_content.strip()) < 100:
                    st.error("❌ PDF នេះអានអត្ថបទមិនចេញទេ។ វាអាចជារូបភាពថត។")
                else:
                    # ៣. បង្កើត Prompt (ប្រើវិធីបូកអត្ថបទជំនួស f-string ដើម្បីការពារ Error)
                    prompt = "Extract 5 English grammar questions from the text below.\n"
                    prompt += "Return ONLY a JSON list of objects.\n"
                    prompt += 'Format: [{"id":1, "question":"...", "options":["a","b","c","d"], "correct":"a"}]\n\n'
                    prompt += "Text: " + text_content[:6000]
                    
                    response = model.generate_content(prompt)
                    
                    # ប្រើ Regex ដើម្បីឆ្កឹះយកតែ JSON
                    json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
                    
                    if json_match:
                        st.session_state.quiz = json.loads(json_match.group())
                        st.success("✅ បង្កើតសំណួរបានជោគជ័យ!")
                    else:
                        st.error("⚠️ AI បង្កើតទម្រង់ JSON មិនត្រឹមត្រូវ។ សូមសាកល្បងម្ដងទៀត។")
            except Exception as e:
                st.error(f"❌ កំហុសបច្ចេកទេស: {str(e)}")

# ៤. បង្ហាញសំណួរ និងដាក់ពិន្ទុ
if 'quiz' in st.session_state:
    with st.form("exam_form"):
        user_answers = {}
        for q in st.session_state.quiz:
            st.write(f"**Q{q['id']}: {q['question']}**")
            # បង្ហាញជម្រើសចម្លើយ a, b, c, d
            choice = st.radio("ជ្រើសរើសចម្លើយ:", q['options'], key=f"q_{q['id']}", index=None)
            user_answers[q['id']] = choice
            st.write("---")
        
        if st.form_submit_button("Submit"):
            score = 0
            for q in st.session_state.quiz:
                # ឆែកមើលចម្លើយដែលសិស្សរើស ធៀបនឹងចម្លើយត្រឹមត្រូវ (correct)
                correct_idx = ord(q['correct'].lower()) - 97 # បំប្លែង a->0, b->1, c->2, d->3
                try:
                    correct_text = q['options'][correct_idx]
                    if user_answers[q['id']] == correct_text:
                        st.success(f"Q{q['id']}: ត្រឹមត្រូវ! ✅")
                        score += 1
                    else:
                        st.error(f"Q{q['id']}: ខុស! ចម្លើយពិតគឺ: {correct_text} ❌")
                except:
                    st.error(f"Q{q['id']}: មានបញ្ហាជាមួយទម្រង់សំណួរ។")
                    
            st.subheader(f"ពិន្ទុរបស់អ្នកគឺ: {score}/{len(st.session_state.quiz)}")
