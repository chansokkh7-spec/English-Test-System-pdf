import streamlit as st
import fitz
import google.generativeai as genai
import json
import re

# --- 1. ការកំណត់ API ---
GOOGLE_API_KEY = "AIzaSyBfDSDxtCJbypPcLaR2kEagUQfXLQBWXcY"
genai.configure(api_key=GOOGLE_API_KEY)
# ប្រើតែកូដ gemini-1.5-flash ដើម្បីល្បឿន និងភាពត្រឹមត្រូវ
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="AI Exam Generator", layout="wide")

# --- 2. មុខងារជំនួយ ---
def extract_text(file):
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        # អានតែ ៥-១០ ទំព័រដំបូង ដើម្បីកុំឱ្យ AI វង្វេង (Bad Data)
        max_pages = min(len(doc), 10)
        for i in range(max_pages):
            text += doc[i].get_text()
        return text.strip()
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

def get_questions(content, count):
    # Prompt កាន់តែខ្លី កាន់តែមានប្រសិទ្ធភាព
    prompt = f"""
    Based on this text, create {count} English MCQs.
    Return ONLY a JSON list. 
    Format: [{{"id":1, "question":"...", "options":["a","b","c","d"], "correct":"a"}}]
    Text: {content[:6000]}
    """
    try:
        response = model.generate_content(prompt)
        res_text = response.text
        
        # ចាប់យកតែផ្នែក JSON ពីក្នុងចន្លោះ [ ]
        match = re.search(r'\[.*\]', res_text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return None
    except Exception as e:
        return None

# --- 3. រចនាសម្ព័ន្ធកម្មវិធី (UI) ---
st.title("🎓 Universal AI English Test")

if 'exam_questions' not in st.session_state:
    st.session_state.exam_questions = []

uploaded_file = st.file_uploader("សូមបញ្ចូលសៀវភៅ PDF របស់អ្នកនៅទីនេះ", type="pdf")

if uploaded_file:
    q_count = st.sidebar.slider("ជ្រើសរើសចំនួនសំណួរ", 5, 20, 10)
    
    if st.button("បង្កើតសំណួរ (Generate) ✨"):
        with st.spinner("AI កំពុងអានសៀវភៅ... សូមរង់ចាំ..."):
            # Reset file pointer
            uploaded_file.seek(0)
            pdf_text = extract_text(uploaded_file)
            
            if pdf_text:
                # ព្យាយាមសួរ AI ម្ដងទៀតបើបរាជ័យ
                results = get_questions(pdf_text, q_count)
                if not results:
                    results = get_questions(pdf_text, q_count) # Retry 1
                
                if results:
                    st.session_state.exam_questions = results
                    st.success("ជោគជ័យ! សំណួរត្រូវបានបង្កើត។")
                else:
                    st.error("AI មិនអាចបង្កើតសំណួរបានទេ។ សូមសាកល្បងម្ដងទៀត។")
            else:
                st.error("មិនអាចទាញយកអត្ថបទពី PDF បានទេ។")

# --- 4. ការបង្ហាញសំណួរ និងការដាក់ពិន្ទុ ---
if st.session_state.exam_questions:
    with st.form("exam_area"):
        answers = {}
        for q in st.session_state.exam_questions:
            st.write(f"**សំណួរទី {q['id']}: {q['question']}**")
            options = [f"(a) {q['options'][0]}", f"(b) {q['options'][1]}", f"(c) {q['options'][2]}", f"(d) {q['options'][3]}"]
            choice = st.radio("ជ្រើសរើសចម្លើយ៖", options, key=f"q_{q['id']}", index=None, label_visibility="collapsed")
            answers[q['id']] = choice[1] if choice else None
            st.write("---")
            
        if st.form_submit_button("ពិនិត្យលទ្ធផល (Submit)"):
            score = 0
            for q in st.session_state.exam_questions:
                correct_ans = q['correct'].lower()
                if answers[q['id']] == correct_ans:
                    st.success(f"សំណួរទី {q['id']}: ត្រឹមត្រូវ! ✅")
                    score += 1
                else:
                    st.error(f"សំណួរទី {q['id']}: ខុស! ចម្លើយត្រឹមត្រូវគឺ ({correct_ans}) ❌")
            st.subheader(f"ពិន្ទុដែលអ្នកទទួលបាន៖ {score} / {len(st.session_state.exam_questions)}")
