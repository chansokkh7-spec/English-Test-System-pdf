import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import json
import re

# --- 1. CONFIGURATION ---
# API Key របស់អ្នក
API_KEY = "AIzaSyBfDSDxtCJbypPcLaR2kEagUQfXLQBWXcY"
genai.configure(api_key=API_KEY)

# ប្រើឈ្មោះ Full Path ដើម្បីបង្ខំឱ្យ Server ស្គាល់ Model ជានិច្ច
# វិធីនេះនឹងបំបាត់ Error 404 models/gemini-1.5-flash is not found
MODEL_NAME = 'models/gemini-1.5-flash' 

try:
    model = genai.GenerativeModel(MODEL_NAME)
except:
    # បើនៅតែរកមិនឃើញ ប្រើ Model ជំនាន់មូលដ្ឋាន
    model = genai.GenerativeModel('models/gemini-pro')

st.set_page_config(page_title="AI Exam Extractor", layout="wide")

# --- 2. FUNCTIONS ---
def get_pdf_text(file):
    try:
        file.seek(0)
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        # អាន ១៥ ទំព័រដំបូង
        for i in range(min(len(doc), 15)):
            text += doc[i].get_text()
        return text.strip()
    except Exception as e:
        return ""

# --- 3. UI ---
st.title("📖 ប្រព័ន្ធទាញយកតេស្តចេញពីសៀវភៅ PDF")
st.info("AI នឹងស្កេនរកសំណួរដែលមានស្រាប់ក្នុងសៀវភៅ រួចរៀបចំជាតេស្តឱ្យអ្នក។")

uploaded_file = st.file_uploader("Upload សៀវភៅ PDF របស់អ្នក", type="pdf")

if uploaded_file:
    if st.button("ស្វែងរក និងបង្កើតតេស្ត ✨"):
        with st.spinner("AI កំពុងស្វែងរកសំណួរក្នុងសៀវភៅ..."):
            raw_text = get_pdf_text(uploaded_file)
            
            if raw_text:
                # បញ្ជាឱ្យ AI រកសំណួរដែលមានស្រាប់
                prompt = "Find all multiple choice questions existing in this text. "
                prompt += "Extract them and return ONLY a JSON list. "
                prompt += 'Format: [{"id":1, "question":"...", "options":["a","b","c","d"], "correct":"a"}] '
                prompt += "\n\nText:\n" + raw_text[:8000]
                
                try:
                    response = model.generate_content(prompt)
                    # ឆ្កឹះយកតែ JSON
                    json_data = re.search(r'\[.*\]', response.text, re.DOTALL)
                    
                    if json_data:
                        st.session_state.quiz = json.loads(json_data.group())
                        st.success(f"រកឃើញសំណួរចំនួន {len(st.session_state.quiz)} ក្នុងសៀវភៅ!")
                    else:
                        st.error("AI រកសំណួរក្នុងទំព័រទាំងនេះមិនឃើញទេ។ សូមសាកល្បង PDF ផ្សេង។")
                except Exception as e:
                    st.error(f"API Error: {str(e)}")
            else:
                st.error("មិនអាចអានអត្ថបទបានទេ។")

# --- 4. DISPLAY ---
if 'quiz' in st.session_state and st.session_state.quiz:
    st.divider()
    score = 0
    with st.form("exam_form"):
        for q in st.session_state.quiz:
            st.subheader(f"សំណួរទី {q['id']}: {q['question']}")
            choice = st.radio("ជ្រើសរើសចម្លើយ៖", q['options'], key=f"q_{q['id']}", index=None)
            
            # Logic ដាក់ពិន្ទុ
            try:
                correct_letter = q['correct'].lower().strip()
                correct_index = ord(correct_letter) - 97
                if choice == q['options'][correct_index]:
                    score += 1
            except: pass
            st.write("---")
            
        if st.form_submit_button("Submit Result"):
            st.header(f"ពិន្ទុសរុប: {score} / {len(st.session_state.quiz)}")
            if score == len(st.session_state.quiz):
                st.balloons()
