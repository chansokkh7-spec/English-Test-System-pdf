import streamlit as st
import pandas as pd
import google.generativeai as genai
from PyPDF2 import PdfReader
import io

# 1. Page Configuration
st.set_page_config(page_title="SEG AI Master 2026", page_icon="🏫", layout="wide")

# 2. Secure AI Setup
# ប្រើ model 'gemini-1.5-flash' ដែលជា Version ថ្មីបំផុត និងខ្លាំងបំផុតសម្រាប់ PDF
API_KEY = "AIzaSyBHcXDGDZjE43glfOLCCspV1N1NhIX05S4"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. Clean CSS
st.markdown("""
<style>
    .stButton>button {width: 100%; border-radius: 10px; height: 3em; background-color: #003057; color: white; font-weight: bold;}
    .reportview-container {background: #fdfdfd}
    .footer {text-align: center; color: #999; font-size: 0.8em; margin-top: 60px; border-top: 1px solid #eee; padding-top: 20px;}
</style>
""", unsafe_allow_html=True)

# 4. Sidebar Navigation
with st.sidebar:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.markdown("<h2 style='text-align: center;'>🏫 SEG SCHOOL</h2>", unsafe_allow_html=True)
    
    st.divider()
    menu = st.radio("Menu Navigation", ["📊 Dashboard", "📝 AI Quiz Generator"])
    st.divider()
    st.info("Location: Prek Leap Branch\nDeveloper: CHAN Sokhoeurn")

# 5. Dashboard Functionality
if menu == "📊 Dashboard":
    st.title("📊 Student Management Dashboard")
    st.info("ប្រព័ន្ធកំពុងដំណើរការជាធម្មតា។ អ្នកគ្រូអាចប្រើប្រាស់មុខងារ Quiz Generator ក្នុង Menu ខាងឆ្វេង។")

# 6. AI Quiz Generator (Optimized for 1,500 Pages)
else:
    st.title("📝 AI Smart Quiz Generator")
    st.write("បង្កើតវិញ្ញាសាតេស្ត ១០០% ចេញពីសៀវភៅ PDF ធំៗ")

    uploaded_file = st.file_uploader("Upload Your Grammar Book (PDF)", type="pdf")

    if uploaded_file:
        # បង្កើត Reader ដើម្បីឆែកចំនួនទំព័រ
        pdf_reader = PdfReader(io.BytesIO(uploaded_file.read()))
        total_pgs = len(pdf_reader.pages)
        st.success(f"ឯកសារត្រូវបានបញ្ចូល៖ មានសរុប {total_pgs} ទំព័រ")

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            level = st.selectbox("កម្រិតតេស្ត (Level)", ["Elementary", "Intermediate", "Advanced"])
            num_q = st.number_input("ចំនួនសំណួរ (Questions)", min_value=1, max_value=50, value=10)
        with col2:
            st.write("🎯 **ជ្រើសរើសទំព័រដែលចង់យកមកធ្វើតេស្ត**")
            start_p = st.number_input("ចាប់ពីទំព័រ", min_value=1, max_value=total_pgs, value=1)
            end_p = st.number_input("ដល់ទំព័រ", min_value=1, max_value=total_pgs, value=min(start_p+10, total_pgs))

        if st.button("🚀 ចាប់ផ្តើមរៀបចំវិញ្ញាសា"):
            if start_p > end_p:
                st.error("កំហុស៖ ទំព័រចាប់ផ្ដើមមិនអាចធំជាងទំព័របញ្ចប់ទេ។")
            else:
                with st.spinner(f"AI កំពុងវិភាគទំព័រទី {start_p} ដល់ {end_p}..."):
                    try:
                        # ចាប់យកអត្ថបទតែក្នុងចន្លោះទំព័រដែលអ្នកគ្រូកំណត់ (ដើម្បីការពារកុំឱ្យ AI គាំង)
                        context_text = ""
                        for i in range(start_p - 1, end_p):
                            context_text += pdf_reader.pages[i].extract_text()
                        
                        # បញ្ជា AI ឱ្យធ្វើការ
                        prompt = f"""
                        Task: Create a professional English Grammar Test.
                        Source Content: {context_text[:15000]}
                        Level: {level}
                        Total Questions: {num_q}
                        
                        Rules:
                        1. Format each question as: "Q1: [Question] / (a) (b) (c) (d)".
                        2. Questions must be 100% based on the logic from the uploaded PDF.
                        3. Provide the Answer Key at the very end.
                        4. Language: English.
                        """
                        
                        response = model.generate_content(prompt)
                        
                        # បង្ហាញលទ្ធផល
                        st.divider()
                        st.subheader("✨ វិញ្ញាសាតេស្តដែលបានបង្កើត")
                        st.markdown(response.text)
                        
                        # ប៊ូតុង Download
                        st.download_button("📥 Download Test (TXT)", response.text, file_name=f"SEG_Test_P{start_p}-{end_p}.txt")
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

st.markdown('<div class="footer">© 2026 SEG School Management System | Prek Leap Branch</div>', unsafe_allow_html=True)
