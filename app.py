import streamlit as st
import pandas as pd
import google.generativeai as genai
from PyPDF2 import PdfReader
import io

# 1. ការកំណត់ទំព័រ
st.set_page_config(page_title="SEG AI System 2026", page_icon="🏫", layout="wide")

# 2. ការកំណត់ AI (Update Model ទៅជា Version ថ្មីបំផុតដើម្បីបាត់ Error)
API_KEY = "AIzaSyBHcXDGDZjE43glfOLCCspV1N1NhIX05S4"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. រចនាប័ទ្ម (CSS)
st.markdown("""
<style>
    .stButton>button {width: 100%; border-radius: 10px; height: 3em; background-color: #003057; color: white; font-weight: bold;}
    .footer {text-align: center; color: #888; font-size: 0.8em; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px;}
</style>
""", unsafe_allow_html=True)

# 4. Sidebar ម៉ឺនុយ
with st.sidebar:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.markdown("<h2 style='text-align: center;'>🏫 SEG SCHOOL</h2>", unsafe_allow_html=True)
    
    st.divider()
    menu = st.radio("ជ្រើសរើសមុខងារ", ["📊 Dashboard ពិន្ទុ", "📝 បង្កើតវិញ្ញាសាពី PDF"])
    st.divider()
    st.info("Branch: Prek Leap\nDeveloper: CHAN Sokhoeurn")

# 5. មុខងារ Dashboard
if menu == "📊 Dashboard ពិន្ទុ":
    st.title("📊 Student Management Dashboard")
    st.info("មុខងារគ្រប់គ្រងពិន្ទុដំណើរការធម្មតា។ សូមជ្រើសរើស 'បង្កើតវិញ្ញាសាពី PDF' ដើម្បីប្រើ AI។")

# 6. មុខងារបង្កើតតេស្ត (សម្រាប់សៀវភៅ ១៥០០ ទំព័រ)
else:
    st.title("📝 AI Smart Quiz Generator")
    st.write("ប្រព័ន្ធបង្កើតវិញ្ញាសាឆ្លាតវៃ អាចអានសៀវភៅធំៗ និងបង្កើតតេស្តតាមទំព័រដែលអ្នកគ្រូកំណត់")

    file = st.file_uploader("Upload សៀវភៅ PDF របស់អ្នកគ្រូ", type="pdf")

    if file:
        # អាន PDF ក្នុង Memory ដើម្បីកុំឱ្យស្ទះ
        pdf_data = file.read()
        reader = PdfReader(io.BytesIO(pdf_data))
        total_pages = len(reader.pages)
        st.success(f"បានរកឃើញសៀវភៅចំនួន {total_pages} ទំព័រ")

        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            level = st.selectbox("កម្រិតសំណួរ (Level)", ["Elementary", "Intermediate", "Advanced"])
            num_q = st.number_input("ចំនួនសំណួរដែលចង់បាន", min_value=1, max_value=50, value=10)
        with c2:
            st.write("🎯 **ជ្រើសរើសចន្លោះទំព័រមេរៀន**")
            start_p = st.number_input("ចាប់ពីទំព័រ", min_value=1, max_value=total_pages, value=1)
            end_p = st.number_input("ដល់ទំព័រ", min_value=1, max_value=total_pages, value=min(start_p+5, total_pages))

        if st.button("🚀 ចាប់ផ្តើមបង្កើតវិញ្ញាសាស្វ័យប្រវត្តិ"):
            if start_p > end_p:
                st.error("កំហុស៖ ទំព័រចាប់ផ្ដើមមិនអាចធំជាងទំព័របញ្ចប់ទេ។")
            else:
                with st.spinner(f"AI កំពុងអានមេរៀនពីទំព័រ {start_p} ដល់ {end_p}..."):
                    try:
                        # ចាប់យកអត្ថបទតែក្នុងចន្លោះទំព័រដែលកំណត់ (ដើម្បីការពារ Error)
                        text_to_analyze = ""
                        for i in range(start_p - 1, end_p):
                            text_to_analyze += reader.pages[i].extract_text()
                        
                        # បញ្ជា AI ឱ្យបង្កើតតេស្ត
                        prompt = f"""
                        Task: Create an English Grammar Test.
                        Level: {level}
                        Questions: {num_q}
                        Source Content: {text_to_analyze[:15000]}
                        
                        Instructions:
                        1. Format: Q1: [Question] / (a) (b) (c) (d)
                        2. Style: Strictly follow the original English Test style.
                        3. Include 'Answer Key' at the very bottom.
                        4. Output in English only.
                        """
                        
                        response = model.generate_content(prompt)
                        
                        st.divider()
                        st.subheader("✨ វិញ្ញាសាតេស្តដែលបានបង្កើតរួចរាល់")
                        st.markdown(response.text)
                        
                        # ប៊ូតុងទាញយក
                        st.download_button("📥 ទាញយកវិញ្ញាសា (TXT)", response.text, file_name=f"SEG_Test_P{start_p}-{end_p}.txt")
                        
                    except Exception as e:
                        st.error(f"មានបញ្ហាបច្ចេកទេស៖ {str(e)}")

st.markdown('<div class="footer">© 2026 SEG School Management System | Prek Leap Branch</div>', unsafe_allow_html=True)
