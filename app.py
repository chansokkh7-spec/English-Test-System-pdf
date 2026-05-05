import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# ១. កំណត់ទម្រង់ទំព័រ
st.set_page_config(page_title="AI Quiz Master", page_icon="📝")

# ២. កំណត់ API Key (សូមដូរ YOUR_API_KEY ទៅជា Key ពិតរបស់អ្នកគ្រូ)
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("📄 SEG AI Test Generator")
st.write("បំប្លែង PDF ទៅជាវិញ្ញាសាប្រឡងស្វ័យប្រវត្តិ ១០០%")

# ៣. កន្លែង Upload PDF
uploaded_file = st.file_uploader("Upload ឯកសារ Grammar PDF របស់អ្នកគ្រូ", type="pdf")

if uploaded_file is not None:
    # អានអត្ថបទពី PDF
    with st.spinner("កំពុងអានឯកសារ..."):
        pdf_reader = PdfReader(uploaded_file)
        text_content = ""
        for page in pdf_reader.pages:
            text_content += page.extract_text()
    
    st.success("អាន PDF រួចរាល់!")

    # ប៊ូតុងបង្កើតតេស្ត
    if st.button("ចាប់ផ្តើមបង្កើតវិញ្ញាសាឥឡូវនេះ"):
        with st.spinner("AI កំពុងរៀបចំសំណួរ..."):
            # ប្រើ Prompt ពិសេសដើម្បីឱ្យដូចសៀវភៅ Grammar Test
            prompt = f"""
            ផ្អែកលើខ្លឹមសារ PDF នេះ សូមបង្កើតវិញ្ញាសា Grammar Test ចំនួន ១០ សំណួរ។
            លក្ខខណ្ឌ៖
            1. ទម្រង់សំណួរ៖ "Q1: [សំណួរ] / (a) [ជម្រើស] (b) [ជម្រើស] (c) [ជម្រើស] (d) [ជម្រើស]"។
            2. កម្រិត៖ ឱ្យត្រូវតាមខ្លឹមសារមេរៀនក្នុង PDF។
            3. ចម្លើយ៖ បង្ហាញ Key Answer នៅផ្នែកខាងក្រោមបង្អស់នៃវិញ្ញាសា (ដូចក្នុងសៀវភៅ PDF)។
            
            ខ្លឹមសារឯកសារ៖
            {text_content[:10000]} 
            """
            
            response = model.generate_content(prompt)
            
            # បង្ហាញលទ្ធផល
            st.divider()
            st.subheader("📝 វិញ្ញាសាដែលបានបង្កើតរួចរាល់")
            st.markdown(response.text)
            
            # ប៊ូតុងសម្រាប់ Copy ឬ Download (Optional)
            st.download_button("📥 ទាញយកជា Text File", response.text, file_name="generated_test.txt")
