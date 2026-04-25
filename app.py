import streamlit as st
import fitz
import re

# កំណត់ទំព័រ Web
st.set_page_config(page_title="Grammar Test System", layout="centered")

def get_data(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = "".join([page.get_text() for page in doc])
    
    # ទាញយកចម្លើយពិត
    ans_key = {int(n): a for n, a in re.findall(r"A(\d+)\s+.*?answer:\s+\(([a-d])\)", text)}
    
    # ទាញយកសំណួរ (បំប្លែងឱ្យត្រូវនឹងទម្រង់ PDF របស់អ្នក)
    quiz_list = []
    # ស្វែងរកសំណួរដែលមានទម្រង់ "Q1","Question text"... (a) option (b) option...
    matches = re.findall(r"\"Q(\d+)\"\s*,\"(.*?)\".*?\(a\)\s*(.*?)\n.*?\(b\)\s*(.*?)\n.*?\(c\)\s*(.*?)\n.*?\(d\)\s*(.*?)\n", text, re.DOTALL)
    
    for m in matches:
        q_id = int(m[0])
        quiz_list.append({
            "id": q_id,
            "question": m[1].replace('\n', ' ').strip(),
            "options": [m[2].strip(), m[3].strip(), m[4].strip(), m[5].strip()],
            "correct": ans_key.get(q_id)
        })
    return quiz_list

st.title("📖 ប្រព័ន្ធធ្វើតេស្តពីសៀវភៅ PDF")
uploaded_file = st.file_uploader("បញ្ចូលសៀវភៅ Grammar Test (PDF)", type="pdf")

if uploaded_file:
    data = get_data(uploaded_file)
    
    if data:
        # បង្កើតតេស្ត ២០ សំណួរក្នុងមួយទំព័រ (ឬតាមចិត្តចង់)
        with st.form("quiz"):
            user_answers = {}
            for q in data[:10]: # បង្ហាញ ១០ សំណួរដំបូងជាឧទាហរណ៍
                st.markdown(f"**សំណួរទី {q['id']}: {q['question']}**")
                # បង្កើតជម្រើស ក ខ គ ឃ
                ans = st.radio("ជ្រើសរើសចម្លើយ៖", ["(a) "+q['options'][0], "(b) "+q['options'][1], "(c) "+q['options'][2], "(d) "+q['options'][3]], key=q['id'])
                user_answers[q['id']] = ans[1] # យកតែអក្សរ a, b, c ឬ d
                st.divider()
            
            if st.form_submit_button("ពិនិត្យចម្លើយ"):
                score = 0
                for q in data[:10]:
                    if user_answers[q['id']] == q['correct']:
                        st.success(f"សំណួរទី {q['id']}: ត្រឹមត្រូវ! ✅")
                        score += 1
                    else:
                        st.error(f"សំណួរទី {q['id']}: ខុស! ចម្លើយត្រឹមត្រូវគឺ ({q['correct']}) ❌")
                st.subheader(f"ពិន្ទុរបស់អ្នកគឺ៖ {score}/10")
