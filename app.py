import streamlit as st
import fitz
import google.generativeai as genai
import json
import re

# --- 1. API SETUP ---
GOOGLE_API_KEY = "AIzaSyBfDSDxtCJbypPcLaR2kEagUQfXLQBWXcY"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="AI Exam System", layout="wide")

# --- 2. FUNCTIONS ---
def get_pdf_text(file):
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        # អានតែ ១០ ទំព័រដំបូងដើម្បីកុំឱ្យលើសកំណត់ AI
        for i in range(min(len(doc), 10)):
            text += doc[i].get_text()
        return text.strip()
    except:
        return ""

def call_gemini_ai(pdf_text, count):
    # បង្កើត Prompt ឱ្យច្បាស់លាស់បំផុត
    prompt = f"""
    Create {count} English multiple choice questions based on the text provided.
    Return ONLY a JSON list. No intro, no explanation.
    Structure: [{"id": 1, "question": "...", "options": ["A", "B", "C", "D"], "correct": "a"}]
    
    Text content:
    {pdf_text[:7000]}
    """

    try:
        response = model.generate_content(prompt)
        res_text = response.text.strip()
        
        # ប្រើ Regex ដើម្បីចាប់យកតែផ្នែកដែលនៅក្នុងសញ្ញា [ ] (JSON List)
        match = re.search(r'\[.*\]', res_text, re.DOTALL)
        if match:
            json_str = match.group()
            return json.loads(json_str)
        return None
    except:
        return None

# --- 3. UI ---
st.title("🎓 Universal AI English Test")
st.write("រង់ចាំបន្តិច ប្រព័ន្ធកំពុងដំណើរការ...")

if 'questions' not in st.session_state:
    st.session_state.questions = []

uploaded_file = st.file_uploader("បញ្ចូលសៀវភៅ PDF របស់អ្នក", type="pdf")

if uploaded_file:
    num_q = st.sidebar.slider("ចំនួនសំណួរ", 5, 20, 10)
    
    if st.button("Generate Test ✨"):
        with st.spinner("AI កំពុងវិភាគសៀវភៅ... សូមរង់ចាំ..."):
            uploaded_file.seek(0)
            text = get_pdf_text(uploaded_file)
            
            if text:
                # ព្យាយាមហៅ AI ចំនួន ៣ ដង បើលើកទី១ មិនជោគជ័យ
                data = None
                for attempt in range(3):
                    data = call_gemini_ai(text, num_q)
                    if data: break
                
                if data:
                    st.session_state.questions = data
                    st.success("បង្កើតសំណួររួចរាល់!")
                else:
                    st.error("AI ផ្ញើទិន្នន័យមិនត្រឹមត្រូវ (Bad Data)។ សូមចុចប៊ូតុង Generate ម្ដងទៀត។")
            else:
                st.error("មិនអាចអានអត្ថបទក្នុង PDF បានទេ។")

# --- 4. TEST FORM ---
if st.session_state.questions:
    with st.form("quiz_form"):
        user_answers = {}
        for q in st.session_state.questions:
            st.write(f"**Q{q['id']}: {q['question']}**")
            opts = [f"(a) {q['options'][0]}", f"(b) {q['options'][1]}", f"(c) {q['options'][2]}", f"(d) {q['options'][3]}"]
            ans = st.radio("រើសចម្លើយ:", opts, key=f"ans_{q['id']}", index=None, label_visibility="collapsed")
            user_answers[q['id']] = ans[1] if ans else None
            st.write("---")
        
        if st.form_submit_button("ពិនិត្យលទ្ធផល"):
            score = 0
            for q in st.session_state.questions:
                correct = q['correct'].lower()
                if user_answers[q['id']] == correct:
                    st.success(f"Q{q['id']}: ត្រឹមត្រូវ! (ចម្លើយ: {correct})")
                    score += 1
                else:
                    st.error(f"Q{q['id']}: ខុសហើយ! (ចម្លើយត្រឹមត្រូវគឺ: {correct})")
            st.subheader(f"ពិន្ទុរបស់អ្នក: {score}/{len(st.session_state.questions)}")
