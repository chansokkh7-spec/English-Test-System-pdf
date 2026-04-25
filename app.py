import streamlit as st
import fitz  # PyMuPDF
import re

st.set_page_config(page_title="English Test System", layout="wide")

st.title("📚 ប្រព័ន្ធបង្កើតតេស្តស្វ័យប្រវត្តិ")
st.info("សូមបញ្ចូលសៀវភៅ PDF ដើម្បីចាប់ផ្ដើម")

uploaded_file = st.file_uploader("Upload Grammar Test PDF", type="pdf")

if uploaded_file is not None:
    # ១. អានអត្ថបទពី PDF
    with st.spinner('កំពុងអានទិន្នន័យ...'):
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()

    # ២. ទាញយកចម្លើយ (Answer Key)
    # ស្វែងរកទម្រង់៖ A1 answer: (a)
    answers = {}
    ans_matches = re.findall(r"A(\d+)\s+.*?answer:\s+\(([a-d])\)", text, re.DOTALL)
    for num, char in ans_matches:
        answers[int(num)] = char

    # ៣. ទាញយកសំណួរ (Regex នេះទាញយកសំណួរដែលមានសញ្ញា " ដូចសៀវភៅអ្នក)
    # ទម្រង់៖ "Q1","Question content"... (a)... (b)... (c)... (d)...
    quiz_pattern = r"\"Q(\d+)\"\s*,\"(.*?)\".*?\(a\)\s*(.*?)\n.*?\(b\)\s*(.*?)\n.*?\(c\)\s*(.*?)\n.*?\(d\)\s*(.*?)\n"
    questions = re.findall(quiz_pattern, text, re.DOTALL)

    if questions:
        st.success(f"រកឃើញសំណួរចំនួន {len(questions)} សំណួរ!")
        
        # បង្កើត Form សម្រាប់ធ្វើតេស្ត
        with st.form("test_form"):
            user_responses = {}
            
            # បង្ហាញត្រឹម ១០ សំណួរដំបូងដើម្បីសាកល្បង (អ្នកអាចប្ដូរបាន)
            for q in questions[:10]:
                q_id = int(q[0])
                q_text = q[1].replace('\n', ' ').strip()
                opts = [q[2].strip(), q[3].strip(), q[4].strip(), q[5].strip()]
                
                st.write(f"**សំណួរទី {q_id}:** {q_text}")
                ans = st.radio(f"ជ្រើសរើសចម្លើយសម្រាប់ Q{q_id}:", 
                               [f"(a) {opts[0]}", f"(b) {opts[1]}", f"(c) {opts[2]}", f"(d) {opts[3]}"], 
                               key=f"radio_{q_id}")
                user_responses[q_id] = ans[1] # យកតែអក្សរ a, b, c ឬ d
                st.write("---")
            
            submit = st.form_submit_button("ពិនិត្យចម្លើយភ្លាមៗ")
            
            if submit:
                score = 0
                for q in questions[:10]:
                    qid = int(q[0])
                    correct_ans = answers.get(qid)
                    if user_responses[qid] == correct_ans:
                        st.success(f"Q{qid}: ត្រឹមត្រូវ! (ចម្លើយ {correct_ans})")
                        score += 1
                    else:
                        st.error(f"Q{qid}: ខុស! ចម្លើយត្រឹមត្រូវគឺ ({correct_ans})")
                
                st.metric("ពិន្ទុរបស់អ្នកគឺ", f"{score}/10")
                if score == 10: st.balloons()
    else:
        st.warning("មិនអាចរកឃើញសំណួរក្នុងទម្រង់ដែលបានកំណត់ទេ។ សូមពិនិត្យឯកសារ PDF ម្ដងទៀត។")
