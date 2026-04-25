import streamlit as st
import fitz  # PyMuPDF
import re

st.set_page_config(page_title="Grammar Quiz System", layout="wide")

def clean_and_extract(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    
    # ១. ទាញយកចម្លើយពិត (Answer Key)
    ans_key = {}
    ans_patterns = re.findall(r"A(\d+).*?answer:\s*\(([a-d])\)", full_text, re.DOTALL | re.IGNORECASE)
    for num, char in ans_patterns:
        ans_key[int(num)] = char.lower()

    # ២. បែងចែកសំណួរតាម "Level #" (ដើម្បីធ្វើជាតេស្តទី១ ទី២...)
    # ស្វែងរកផ្នែកដូចជា "Elementary level # 1"
    sections = re.split(r"((?:Elementary|Intermediate|Advanced)\s+level\s+#\s*\d+)", full_text)
    
    all_tests = {}
    current_level = "General Test"
    
    for section in sections:
        if re.match(r"(?:Elementary|Intermediate|Advanced)\s+level\s+#\s*\d+", section):
            current_level = section.strip()
            continue
        
        # សម្អាតអត្ថបទក្នុងផ្នែកនីមួយៗ
        clean_section = section.replace('"', '').replace(',,', ',')
        q_pattern = r"Q(\d+)\s*\n(.*?)\n\s*\(a\)\s*(.*?)\n\s*\(b\)\s*(.*?)\n\s*\(c\)\s*(.*?)\n\s*\(d\)\s*(.*?)\n"
        matches = re.findall(q_pattern, clean_section, re.DOTALL)
        
        quiz_list = []
        for m in matches:
            q_id = int(m[0])
            quiz_list.append({
                "id": q_id,
                "question": m[1].strip(),
                "options": [m[2].strip(), m[3].strip(), m[4].strip(), m[5].strip()],
                "correct": ans_key.get(q_id)
            })
        
        if quiz_list:
            all_tests[current_level] = quiz_list
            
    return all_tests

# --- គ្រប់គ្រងស្ថានភាពកម្មវិធី (Session State) ---
if 'test_index' not in st.session_state:
    st.session_state.test_index = 0

# --- ផ្ទៃកម្មវិធី UI ---
st.title("🎓 ប្រព័ន្ធតេស្តភាសាអង់គ្លេសស្វ័យប្រវត្តិ")

file = st.file_uploader("Upload PDF File", type="pdf")

if file:
    all_quiz_data = clean_and_extract(file)
    
    if all_quiz_data:
        test_names = list(all_quiz_data.keys())
        
        # បង្កើត Sidebar សម្រាប់ជ្រើសរើសតេស្ត
        st.sidebar.header("📋 បញ្ជីតេស្ត")
        selected_test_name = st.sidebar.selectbox("ជ្រើសរើសតេស្ត៖", test_names, index=st.session_state.test_index)
        
        # ប៊ូតុងបញ្ជា "បន្ទាប់" ឬ "ត្រឡប់ក្រោយ"
        col1, col2, col3 = st.sidebar.columns(3)
        if col1.button("⬅️ មុន"):
            if st.session_state.test_index > 0:
                st.session_state.test_index -= 1
                st.rerun()
        
        if col3.button("បន្ទាប់ ➡️"):
            if st.session_state.test_index < len(test_names) - 1:
                st.session_state.test_index += 1
                st.rerun()

        # បង្ហាញសំណួរនៃតេស្តដែលបានជ្រើសរើស
        current_questions = all_quiz_data[selected_test_name]
        st.header(f"📝 {selected_test_name}")
        st.info(f"រកឃើញសំណួរចំនួន {len(current_questions)} ក្នុងផ្នែកនេះ")

        with st.form(key=f"form_{selected_test_name}"):
            user_answers = {}
            for q in current_questions:
                st.write(f"**Q{q['id']}: {q['question']}**")
                opts = [f"(a) {q['options'][0]}", f"(b) {q['options'][1]}", f"(c) {q['options'][2]}", f"(d) {q['options'][3]}"]
                choice = st.radio(f"ជ្រើសរើសចម្លើយសម្រាប់ Q{q['id']}:", opts, key=f"q_{q['id']}_{selected_test_name}")
                user_answers[q['id']] = choice[1]
                st.write("---")
            
            submitted = st.form_submit_button("ពិនិត្យលទ្ធផល")
            
            if submitted:
                score = 0
                for q in current_questions:
                    correct = q['correct']
                    if user_answers[q['id']] == correct:
                        st.success(f"✅ Q{q['id']}: ត្រឹមត្រូវ! (ចម្លើយ: {correct})")
                        score += 1
                    else:
                        st.error(f"❌ Q{q['id']}: ខុស! (ចម្លើយពិត: {correct})")
                
                st.subheader(f"ពិន្ទុសរុប៖ {score} / {len(current_questions)}")
                if score == len(current_questions):
                    st.balloons()
                
                # បង្ហាញប៊ូតុងទៅតេស្តបន្ទាប់ក្រោយពេលចប់
                if st.session_state.test_index < len(test_names) - 1:
                    st.write("រួចរាល់ហើយមែនទេ? ចុចប៊ូតុង 'បន្ទាប់' នៅខាងឆ្វេងដើម្បីបន្តទៅតេស្តថ្មី។")
    else:
        st.error("មិនអាចបំបែកតេស្តបានទេ។ សូមពិនិត្យមើល PDF របស់អ្នកម្តងទៀត។")
