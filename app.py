import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai

# កំណត់ Key សម្រាប់ប្រើ AI (Gemini)
# អ្នកគ្រូអាចយក Key នេះពី Google AI Studio (Free)
genai.configure(api_key="ដាក់_API_KEY_របស់អ្នកគ្រូទីនេះ")

st.title("📄 AI Automatic Test Generator")
st.write("Upload PDF របស់អ្នកគ្រូដើម្បីបង្កើតតេស្តស្វ័យប្រវត្តិ")

uploaded_pdf = st.file_uploader("ជ្រើសរើស File PDF (Grammar Test)", type="pdf")

if uploaded_pdf is not None:
    # ១. អានអក្សរពី PDF
    reader = PdfReader(uploaded_pdf)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    
    st.success("អានឯកសារចប់សព្វគ្រប់!")

    if st.button("ចាប់ផ្តើមបង្កើតតេស្ត ១០០%"):
        with st.spinner("AI កំពុងរៀបចំសំណួរ..."):
            model = genai.GenerativeModel('gemini-pro')
            
            # បញ្ជា AI ឱ្យបង្កើតតេស្ត
            prompt = f"""
            ផ្អែកលើខ្លឹមសារអត្ថបទខាងក្រោម សូមបង្កើតសំណួរតេស្ត Grammar បែប Multiple Choice (A, B, C, D) 
            ចំនួន ១០ សំណួរ ឱ្យមានទម្រង់ដូចក្នុងសៀវភៅតេស្តអន្តរជាតិ៖
            
            ខ្លឹមសារ៖ {text[:3000]}  # យកតែ ៣០០០ អក្សរដំបូងដើម្បីកុំឱ្យលើសកំណត់
            """
            
            response = model.generate_content(prompt)
            
            st.divider()
            st.subheader("📝 វិញ្ញាសាតេស្តដែលបានបង្កើត៖")
            st.write(response.text)
