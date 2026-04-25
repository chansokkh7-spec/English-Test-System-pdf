import streamlit as st
import fitz  # PyMuPDF
import re

st.set_page_config(page_title="English Grammar Test System", layout="wide")

def clean_and_extract(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    
    # 1. Extract Answer Key
    ans_key = {}
    ans_patterns = re.findall(r"A(\d+).*?answer:\s*\(([a-d])\)", full_text, re.DOTALL | re.IGNORECASE)
    for num, char in ans_patterns:
        ans_key[int(num)] = char.lower()

    # 2. Split by "Level #"
    sections = re.split(r"((?:Elementary|Intermediate|Advanced)\s+level\s+#\s*\d+)", full_text)
    
    all_tests = {}
    current_level = "General Test"
    
    for section in sections:
        if re.match(r"(?:Elementary|Intermediate|Advanced)\s+level\s+#\s*\d+", section):
            current_level = section.strip()
            continue
        
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

# --- Session State Management ---
if 'test_index' not in st.session_state:
    st.session_state.test_index = 0

# --- UI Layout ---
st.title("🎓 Automated English Grammar Test")
st.write("Upload your PDF book to generate interactive tests automatically.")

file = st.file_uploader("Step 1: Upload PDF File", type="pdf")

if file:
    all_quiz_data = clean_and_extract(file)
    
    if all_quiz_data:
        test_names = list(all_quiz_data.keys())
        
        # Sidebar for Navigation
        st.sidebar.header("📋 Test List")
        selected_test_name = st.sidebar.selectbox("Select a Test:", test_names, index=st.session_state.test_index)
        
        # Display Current Test
        current_questions = all_quiz_data[selected_test_name]
        st.header(f"📝 {selected_test_name}")

        # Test Form
        with st.form(key=f"form_{selected_test_name}"):
            user_answers = {}
            for q in current_questions:
                st.write(f"**Q{q['id']}: {q['question']}**")
                opts = [f"(a) {q['options'][0]}", f"(b) {q['options'][1]}", f"(c) {q['options'][2]}", f"(d) {q['options'][3]}"]
                
                # Student selects answer here
                choice = st.radio(f"Select answer for Q{q['id']}:", opts, key=f"q_{q['id']}_{selected_test_name}", index=None)
                user_answers[q['id']] = choice[1] if choice else None
                st.write("---")
            
            # Submit Button
            submitted = st.form_submit_button("Check Results")
            
            if submitted:
                score = 0
                st.subheader("Results:")
                for q in current_questions:
                    correct = q['correct']
                    user_ans = user_answers[q['id']]
                    
                    if user_ans == correct:
                        st.success(f"✅ Q{q['id']}: Correct! (Answer: {correct})")
                        score += 1
                    else:
                        st.error(f"❌ Q{q['id']}: Incorrect! (Correct Answer was: {correct})")
                
                st.divider()
                st.subheader(f"Total Score: {score} / {len(current_questions)}")
                if score == len(current_questions):
                    st.balloons()

        # --- Navigation Buttons ---
        st.write("---")
        c1, c2, c3 = st.columns([1, 2, 1])
        
        with c2:
            if st.session_state.test_index < len(test_names) - 1:
                if st.button("➡️ Next Test", use_container_width=True):
                    st.session_state.test_index += 1
                    st.rerun()
            
            if st.session_state.test_index > 0:
                if st.button("⬅️ Previous Test", use_container_width=True):
                    st.session_state.test_index -= 1
                    st.rerun()
    else:
        st.error("No test questions found in this PDF. Please check the format.")
