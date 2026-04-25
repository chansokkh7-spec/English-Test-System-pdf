import streamlit as st
import pandas as pd
import google.generativeai as genai
from PyPDF2 import PdfReader
import io

# 1. កំណត់ទម្រង់ទំព័រ
st.set_page_config(page_title="SEG AI Master 2026", page_icon="🏫", layout="wide")

# 2. ការកំណត់ AI - ប្រើវិធីសាស្ត្រ "ស្វែងរក Model ដោយស្វ័យប្រវត្តិ"
API_KEY = "AIzaSyBHcXDGDZjE43glfOLCCspV1N1NhIX05S4"
genai.configure(api_key=API_KEY)

# មុខងារស្វែងរកឈ្មោះ Model ដែលត្រឹមត្រូវក្នុង Account អ្នកគ្រូ
@st.cache_resource
def load_ai_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # បើមាន gemini-1.5-flash គឺយកមកប្រើ បើមិនមានយកអាដំបូងគេ
        target_model = next((m for m in models if '1.5-flash' in m), models[0])
        return genai.GenerativeModel(target_model), target_model
    except:
        return genai.GenerativeModel('gemini-pro'), "gemini-pro"

model, model_name = load_ai_model()

# 3. រៀបចំសម្រស់កម្មវិធី (CSS)
st.markdown("""
<style>
    .stButton>button {width: 100%; border-radius: 10px; height: 3em; background-color: #003057; color: white; font-weight: bold;}
    .main {background-color: #f9f9f9;}
    .footer {text-align: center; color: #888; font-size: 0.8em; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px;}
</style>
""", unsafe_allow_html=True)

# 4. Sidebar ម៉ឺនុយ
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🏫 SEG System</h2>", unsafe_allow_html=True)
    st.divider()
    menu = st.radio("Menu", ["📊 Dashboard", "📝 AI Quiz Generator"])
    st.divider()
    st.caption(f"Active Model: {model_name}")
    st.info("Branch: Prek Leap\nDeveloper: CHAN Sokhoeurn")

# 5. មុខងារ Dashboard
if menu == "📊 Dashboard":
    st.title("📊 Student Management")
    st.write("Branch: Prek Leap")
    st.info("ប្រព័ន្ធគ្រប់គ្រងពិន្ទុដំណើរការធម្មតា។")

# 6. មុខងារ AI Quiz Generator (សម្រាប់សៀវភៅ ១,៥០០ ទំព័រ)
else:
    st.title("📝 AI Smart Quiz Generator")
    st.write("បង្កើតវិញ្ញាសាតេស្តស្វ័យប្រវត្តិ ១០០% តាមកម្រិត និងតាមទំព័រ")

    file = st.file_uploader("Upload Your PDF Book", type="pdf")

    if file:
        # អាន PDF
        pdf_reader = PdfReader(io.BytesIO(file.read()))
        total_pages = len(pdf_reader.pages)
        st.success(f"ឯកសារត្រូវបានបញ្ចូល៖ សរុប {total_pages} ទំព័រ")

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            level = st.selectbox("Level", ["Elementary", "Intermediate", "Advanced"])
            num_q = st.number_input("Questions Count", min_value=1, max_value=20, value=10)
        with col2:
            st.write("🎯 **ជ្រើសរើសចន្លោះទំព័រមេរៀន**")
            start_p = st.number_input("From Page", min_value=1, max_value=total_pages, value=1)
            end_p = st.number_input("To Page", min_value=1, max_value=total_pages, value=min(start_p+5, total_pages))

        if st.button("🚀 Generate Test"):
            if start_p > end_p:
                st.error("Error: Start page must be less than end page.")
            else:
                with st.spinner(f"AI កំពុងអានមេរៀនពីទំព័រ {start_p} ដល់ {end_p}..."):
                    try:
                        # ចាប់យកអត្ថបទ
                        text = ""
                        for i in range(start_p - 1, end_p):
                            text += pdf_reader.pages[i].extract_text()
                        
                        # បញ្ជា AI
                        prompt = f"Create a grammar test. Level: {level}. Questions: {num_q}. Format: Q1: [Question] / (a) (b) (c) (d). Include Answer Key. Base it on this text: {text[:10000]}"
                        
                        response = model.generate_content(prompt)
                        
                        st.divider()
                        st.subheader("✨ វិញ្ញាសាតេស្តរបស់អ្នកគ្រូ")
                        st.markdown(response.text)
                        st.download_button("📥 Download (.txt)", response.text, file_name="SEG_AI_Test.txt")
                        
                    except Exception as e:
                        st.error(f"Technical Error: {str(e)}")

st.markdown('<div class="footer">© 2026 SEG School Management System | Prek Leap Branch</div>', unsafe_allow_html=True)
