import streamlit as st
import pandas as pd
import google.generativeai as genai
from PyPDF2 import PdfReader
import io

# 1. Page Configuration
st.set_page_config(page_title="SEG AI Master 2026", page_icon="🏫", layout="wide")

# 2. AI Setup - ដោះស្រាយបញ្ហា 404 Error
API_KEY = "AIzaSyBHcXDGDZjE43glfOLCCspV1N1NhIX05S4"
genai.configure(api_key=API_KEY)

# សាកល្បងប្រើឈ្មោះ Model បែប Full Path ដើម្បីការពារ Error
try:
    model = genai.GenerativeModel('models/gemini-1.5-flash')
except:
    model = genai.GenerativeModel('gemini-pro') # បម្រុងទុក (Fallback)

# 3. Custom Styling
st.markdown("""
<style>
    .stButton>button {width: 100%; border-radius: 10px; height: 3em; background-color: #003057; color: white; font-weight: bold;}
    .footer {text-align: center; color: #888; font-size: 0.8em; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px;}
</style>
""", unsafe_allow_html=True)

# 4. Sidebar
with st.sidebar:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.markdown("<h2 style='text-align: center;'>🏫 SEG SCHOOL</h2>", unsafe_allow_html=True)
    
    st.divider()
    menu = st.radio("ជ្រើសរើសមុខងារ", ["📊 Dashboard ពិន្ទុ", "📝 បង្កើតវិញ្ញាសាពី PDF"])
    st.divider()
    st.info("Branch: Prek Leap\nDeveloper: CHAN Sokhoeurn")

# 5. Dashboard
if menu == "📊 Dashboard ពិន្ទុ":
    st.title("📊 Student Management Dashboard")
    st.info("ប្រព័ន្ធដំណើរការធម្មតា។ សូមជ្រើសរើស 'បង្កើតវិញ្ញាសាពី PDF' ដើម្បីប្រើ AI។")

# 6. AI Quiz Generator (Optimized for 1,500 Pages)
else:
    st.title("📝 AI Smart Quiz Generator")
    st.write("បង្កើតវិញ្ញាសាតេស្តស្វ័យប្រវត្តិ តាមកម្រិត និងតាមទំព័រ")

    file = st.file_uploader("Upload Your PDF Book", type="pdf")

    if file:
        # Read PDF using BytesIO to handle large files
        pdf_reader = PdfReader(io.BytesIO(file.read()))
        total_pages = len(pdf_reader.pages)
        st.success(f"ឯកសារត្រូវបានបញ្ចូល៖ សរុប {total_pages} ទំព័រ")

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            level = st.selectbox("កម្រិតសំណួរ (Level)", ["Elementary", "Intermediate", "Advanced"])
            num_q = st.number_input("ចំនួនសំណួរ", min_value=1, max_value=50, value=10)
        with col2:
            st.write("🎯 **ជ្រើសរើសចន្លោះទំព័រមេរៀន**")
            start_p = st.number_input("ចាប់ពីទំព័រ", min_value=1, max_value=total_pages, value=1)
            end_p = st.number_input("ដល់ទំព័រ", min_value=1, max_value=total_pages, value=min(start_p+5, total_pages))

        if st.button("🚀 ចាប់ផ្តើមបង្កើតវិញ្ញាសា"):
            if start_p > end_p:
                st.error("កំហុស៖ ទំព័រចាប់ផ្ដើមមិនអាចធំជាងទំព័របញ្ចប់ទេ។")
            else:
                with st.spinner(f"AI កំពុងអានមេរៀនពីទំព័រ {start_p} ដល់ {end_p}..."):
                    try:
                        # Extract text from the selected page range
                        extracted_text = ""
                        for i in range(start_p - 1, end_p):
                            extracted_text += pdf_reader.pages[i].extract_text()
                        
                        # AI Prompt
                        prompt = f"""
                        Based on this English Grammar text: {extracted_text[:12000]}
                        Create a {level} level test.
                        Total questions: {num_q}
                        Format: Q1: [Question] / (a) (b) (c) (d).
                        Answer Key: Provide at the bottom.
                        """
                        
                        # បញ្ជា AI ឱ្យធ្វើការ
                        response = model.generate_content(prompt)
                        
                        st.divider()
                        st.subheader("✨ វិញ្ញាសាតេស្តដែលបានបង្កើតរួចរាល់")
                        st.markdown(response.text)
                        st.download_button("📥 Download (.txt)", response.text, file_name="SEG_AI_Test.txt")
                        
                    except Exception as e:
                        # បង្ហាញ Error ឱ្យច្បាស់ និងផ្តល់ដំណោះស្រាយ
                        st.error(f"បញ្ហាបច្ចេកទេស៖ {str(e)}")
                        st.warning("ជំនួយ៖ សូមសាកល្បងកាត់បន្ថយចំនួនទំព័រអានឱ្យតិចជាងមុន (ត្រឹម ៣-៥ ទំព័រ)។")

st.markdown('<div class="footer">© 2026 SEG School Management System | Prek Leap Branch</div>', unsafe_allow_html=True)
