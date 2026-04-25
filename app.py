import streamlit as st
import fitz  # PyMuPDF
import re

st.set_page_config(page_title="Grammar Quiz System", layout="wide")

def clean_and_extract(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    
    # --- ១. ទាញយកចម្លើយពិត (Answer Key) ---
    # ស្វែងរកទម្រង់៖ A1 answer: (a) ឬ A1 ... answer: (b)
    ans_key = {}
    ans_patterns = re.findall(r"A(\d+).*?answer:\s*\(([a-d])\)", text, re.DOTALL | re.IGNORECASE)
    for num, char in ans_patterns:
        ans_key[int(num)] = char.lower()

    # --- ២. សម្អាតអត្ថបទដើម្បីស្រួលចាប់សំណួរ ---
    # លុបសញ្ញា " និងសញ្ញា , ដែលនាំឱ្យរញ៉េរញ៉ៃ
    clean_text = text.replace('"', '').replace(',,', ',')
    
    # --- ៣. ទាញយកសំណួរ ---
    # Regex ថ្មី៖ ចាប់ពី Q1 រហូតដល់ជម្រើស (d)
    q_pattern = r"Q(\d+)\s*\n(.*?)\n\s*\(a\)\s*(.*?)\n\s*\(b\)\s*(.*?)\n\s*\(c\)\s*(.*?)\n\s*\(d\)\s*(.*?)\n"
    matches = re.findall(q_pattern, clean_text, re.DOTALL)
    
    quiz_list = []
    for m in matches:
        q_id = int(m[0])
        quiz_list.append({
            "id": q_id,
            "question": m[1].strip(),
            "options": [m[2].strip(), m[3].strip(), m[4].strip(), m[5].strip()],
            "correct": ans_key.get(q_id)
        })
    return quiz_list

# --- ផ្ទៃកម្មវិធី UI ---
st.title("🎓 ប្រព័ន្ធតេស្តភាសាអង់គ្លេសស្វ័យប្រវត្តិ")
st.markdown("### បញ្ចូលសៀវភៅ PDF ដើម្បីចាប់ផ្ដើមធ្វើតេស្ត")

file = st.file_uploader("Upload PDF File", type="pdf")

if file:
    questions = clean_and_extract(file)
    
    if questions:
        st.success(f"រកឃើញសំណួរចំនួន {len(questions)} សំណួរ!")
        
        # បង្កើតការជ្រើសរើសសំណួរ (ឧទាហរណ៍៖ សំណួរទី ១ ដល់ ១០)
        st.sidebar.header("ការកំណត់")
        num_to_show = st.sidebar.slider("ចំនួនសំណួរដែលត្រូវបង្ហាញ", 5, len(questions), 10)
        
        with st.form("quiz_form"):
            user_answers = {}
            for q in questions[:num_to_show]:
                st.write(f"**Q{q['id']}: {q['question']}**")
                # បង្កើតជម្រើស radio
                opts = [f"(a) {q['options'][0]}", f"(b) {q['options'][1]}", f"(c) {q['options'][2]}", f"(d) {q['options'][3]}"]
                choice = st.radio(f"ជ្រើសរើសចម្លើយសម្រាប់ Q{q['id']}:", opts, key=f"q_{q['id']}")
                user_answers[q['id']] = choice[1] # ចាប់យកតែតួអក្សរ a, b, c, d
                st.write("---")
            
            submitted = st.form_submit_button("ពិនិត្យលទ្ធផលភ្លាមៗ")
            
            if submitted:
                score = 0
                for q in questions[:num_to_show]:
                    correct = q['correct']
                    user_ans = user_answers[q['id']]
                    
                    if user_ans == correct:
                        st.write(f"✅ **Q{q['id']}**: ត្រឹមត្រូវ! (ចម្លើយ: {correct})")
                        score += 1
                    else:
                        st.write(f"❌ **Q{q['id']}**: ខុស! (ចម្លើយពិតគឺ: {correct if correct else 'មិនមានក្នុង Key'})")
                
                st.subheader(f"ពិន្ទុសរុប៖ {score} / {num_to_show}")
                if score == num_to_show:
                    st.balloons()
    else:
        st.error("ប្រព័ន្ធមិនអាចទាញយកសំណួរបានទេ។ សូមពិនិត្យមើលថាតើឯកសារ PDF របស់អ្នកត្រូវតាមទម្រង់ដែរឬទេ?")
