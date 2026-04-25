import streamlit as st
import fitz
import google.generativeai as genai
import json
import re

# ដាក់ API Key របស់អ្នក
API_KEY = "AIzaSyBfDSDxtCJbypPcLaR2kEagUQfXLQBWXcY"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("AI English Quiz Generator")

# ១. បញ្ចូលឯកសារ PDF
pdf_file = st.file_uploader("Upload PDF", type="pdf")

if pdf_file:
    if st.button("Generate Now"):
        with st.spinner("Processing..."):
            # ២. ទាញយកអត្ថបទពី PDF (យកតែ ៥ ទំព័រដើម្បីកុំឱ្យ Error)
            doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
            text_content = ""
            for i in range(min(len(doc), 5)):
                text_content += doc[i].get_text()
            
            # ៣. ហៅ AI ឱ្យបង្កើតសំណួរ
            prompt = f"Create 5 English MCQs from this text. Return ONLY a JSON list. Format: " + '[{"id":1,"question":"...","options":["a","b","c","d"],"correct":"a"}]' + f"\n\nText: {text_content[:5000]}"
            
            try:
                response = model.generate_content(prompt)
                # សម្អាតទិន្នន័យដើម្បីយកតែ JSON
                match = re.search(r'\[.*\]', response.text, re.DOTALL)
                if match:
                    st.session_state.quiz = json.loads(match.group())
                    st.success("Success! Quiz created.")
                else:
                    st.error("AI returned wrong format. Try again.")
            except Exception as e:
                st.error(f"Error: {e}")

# ៤. បង្ហាញសំណួរ
if 'quiz' in st.session_state:
    with st.form("my_form"):
        for q in st.session_state.quiz:
            st.write(f"**{q['id']}. {q['question']}**")
            user_choice = st.radio("Select answer:", q['options'], key=f"q_{q['id']}")
            st.write("---")
        
        if st.form_submit_button("Submit"):
            st.write("Done! Check your answers above.")
