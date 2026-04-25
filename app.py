import streamlit as st
import fitz  # PyMuPDF
import re

# កំណត់ផ្ទៃកម្មវិធី
st.set_page_config(page_title="Grammar Test System", layout="wide")
st.title("📚 ប្រព័ន្ធតេស្តភាសាអង់គ្លេសស្វ័យប្រវត្តិ")
st.write("បញ្ចូលសៀវភៅ PDF ដើម្បីបង្កើតតេស្ត និងមើលចម្លើយភ្លាមៗ")

# ១. មុខងារទាញយកទិន្នន័យ (Extract Data)
def extract_data(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    
    # ចាប់យកចម្លើយ (Answer Key) ពីផ្នែកខាងក្រោយសៀវភៅ
    # ស្វែងរកទម្រង់ A1 ... answer: (a)
    ans_key = {}
    ans_patterns = re.findall(r"A(\d+)\s+.*?answer:\s+\(([a-d])\)", full_text, re.DOTALL)
    for num, ans in ans_patterns:
        ans_key[int(num)] = ans

    # បែងចែកសំណួរតាមកម្រិត
    # សៀវភៅរបស់អ្នកបំបែកដោយពាក្យ "Elementary level # 1", "Intermediate level # 1" ជាដើម
    quiz_data = {}
    sections = re.split(r"(Elementary|Intermediate|Advanced)\s+level\s+#\s*(\d+)", full_text)
    
    # ស្វែងរកសំណួរដែលមានទម្រង់ "Q1","Question text"... ដូចក្នុងសៀវភៅរបស់អ្នក
    q_pattern = r"\"Q(\d+)\"\s*,\"(.*?)\".*?\(a\)\s*(.*?)\n.*?\(b\)\s*(.*?)\n.*?\(c\)\s*(.*?)\n.*?\(d\)\s*(.*?)\n"
    matches = re.findall(q_pattern, full_text, re.DOTALL)
    
    formatted_quiz = []
    for m in matches:
        q_id = int(m[0])
        formatted_quiz.append({
            "id": q_id,
            "question": m[1].replace('\n', ' ').strip(),
            "options": [m[2].strip(), m[3].strip(), m[4].strip(), m[5].strip()],
            "correct": ans_key.get(q_id)
        })
    
    return formatted_quiz

# ២. បង្ហាញ UI
uploaded_file = st.file_uploader("ជ្រើសរើសឯកសារ PDF របស់អ្នក", type="pdf")

if uploaded_file:
    with st.spinner('កំពុងរៀបចំសំណួរ...'):
        all_questions = extract_data(uploaded_file)
    
    if all_questions:
        st.success(f"រកឃើញសំណួរចំនួន {len(all_questions)} ក្នុងសៀវភៅ!")
        
        # បង្កើត Form សម្រាប់ធ្វើតេស្ត (បង្ហាញម្ដង ១០ សំណួរ)
        with st.form("test_form"):
            user_answers = {}
            for q in all_questions[:10]: # អ្នកអាចដូរលេខ ១០ ចេញបើចង់បង្ហាញច្រើនជាងនេះ
                st.markdown(f"**Q{q['id']}: {q['question']}**")
                options = [f"(a) {q['options'][0]}", f"(b) {q['options'][1]}", f"(c) {q['options'][2]}", f"(d) {q['options'][3]}"]
                user_choice = st.radio("ជ្រើសរើសចម្លើយ៖", options, key=f"q_{q['id']}")
                user_answers[q['id']] = user_choice[1] # យកតែអក្សរ a, b, c ឬ d
                st.write("---")
            
            submitted = st.form_submit_button("ពិនិត្យលទ្ធផល")
            
            if submitted:
                score = 0
                for q in all_questions[:10]:
                    if user_answers[q['id']] == q['correct']:
                        st.write(f"✅ **Q{q['id']}**: ត្រឹមត្រូវ! (ចម្លើយ: {q['correct']})")
                        score += 1
                    else:
                        st.write(f"❌ **Q{q['id']}**: ខុស! ចម្លើយពិតគឺ: **({q['correct']})**")
                
                st.subheader(f"ពិន្ទុសរុបរបស់អ្នកគឺ៖ {score}/10")
                if score >= 5: st.balloons()
    else:
        st.error("មិនអាចអានសំណួរបានទេ។ សូមពិនិត្យមើលថា PDF របស់អ្នកមានទម្រង់ត្រឹមត្រូវឬទេ?")
