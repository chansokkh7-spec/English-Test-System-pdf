import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import json
import re

# --- ១. ការកំណត់ API ---
API_KEY = "AIzaSyBfDSDxtCJbypPcLaR2kEagUQfXLQBWXcY"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="AI Exam Extractor", layout="wide")

# --- ២. មុខងារអាន PDF ---
def get_pdf_text(file):
    try:
        file.seek(0)
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        # អាន ១៥ ទំព័រដំបូង ដើម្បីស្វែងរកសំណួរ
        for i in range(min(len(doc), 15)):
            text += doc[i].get_text()
        return text.strip()
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

# --- ៣. UI រៀបចំកម្មវិធី ---
if 'quiz' not in st.session_state:
    st.session_state.quiz = []

st.title("📖 ប្រព័ន្ធបង្កើតតេស្តដោយដកស្រង់សំណួរពីសៀវភៅ")
st.info("បញ្ចូលសៀវភៅ PDF ដែលមានសំណួរស្រាប់ AI នឹងដកស្រង់សំណួរទាំងនោះមកដាក់ក្នុងទម្រង់តេស្តឱ្យអ្នក។")

uploaded_file = st.file_uploader("Upload សៀវភៅ PDF របស់អ្នក", type="pdf")

if uploaded_file:
    if st.button("ស្វែងរក និងបង្កើតតេស្ត ✨"):
        with st.spinner("AI កំពុងស្កេនរកសំណួរក្នុងសៀវភៅ..."):
            raw_text = get_pdf_text(uploaded_file)
            
            if raw_text:
                # Prompt បញ្ជាឱ្យ AI រកសំណួរដែលមានស្រាប់ក្នុងអត្ថបទ
                prompt = "Look into the text provided and find the existing multiple choice questions. "
                prompt += "Extract them exactly as they are in the book. "
                prompt += "Return ONLY a JSON list of these questions. "
                prompt += 'Format: [{"id":1, "question":"...", "options":["a","b","c","d"], "correct":"a"}] '
                prompt += "\n\nText content:\n" + raw_text[:8000]
                
                try:
                    response = model.generate_content(prompt)
                    # ប្រើ Regex ចាប់យក JSON
                    json_data = re.search(r'\[.*\]', response.text, re.DOTALL)
                    
                    if json_data:
                        st.session_state.quiz = json.loads(json_data.group())
                        st.success(f"រកឃើញសំណួរចំនួន {len(st.session_state.quiz)} ក្នុងសៀវភៅ!")
                    else:
                        st.error("AI មិនអាចស្វែងរកសំណួរក្នុងទំព័រទាំងនេះបានទេ។")
                except Exception as e:
                    st.error(f"API Error: {e}")
            else:
                st.error("មិនអាចអានអត្ថបទបានទេ។")

# --- ៤. ការបង្ហាញតេស្ត ---
if st.session_state.quiz:
    st.divider()
    score = 0
    with st.form("exam_form"):
        for q in st.session_state.quiz:
            st.subheader(f"សំណួរទី {q['id']}: {q['question']}")
            
            # បង្ហាញ Choice
            choice = st.radio(
                "ជ្រើសរើសចម្លើយ៖", 
                q['options'], 
                key=f"q_{q['id']}", 
                index=None
            )
            
            # ឆែកចម្លើយ (បំប្លែង a, b, c, d ទៅជា Text)
            try:
                correct_letter = q['correct'].lower().strip()
                correct_index = ord(correct_letter) - 97
                correct_text = q['options'][correct_index]
                
                if choice == correct_text:
                    score += 1
            except:
                pass
            st.write("---")
            
        if st.form_submit_button("Submit & Check Result"):
            st.header(f"ពិន្ទុសរុប: {score} / {len(st.session_state.quiz)}")
            if score == len(st.session_state.quiz):
                st.balloons()
                st.success("អស្ចារ្យ! អ្នកឆ្លើយត្រូវទាំងអស់។")
