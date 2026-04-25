import streamlit as st
import pandas as pd
import google.generativeai as genai
from PyPDF2 import PdfReader
import io

# 1. Page Configuration
st.set_page_config(page_title="SEG AI Master 2026", page_icon="🏫", layout="wide")

# 2. AI Setup - ស្វែងរក Model ដែលអាចប្រើបានដោយស្វ័យប្រវត្តិ
API_KEY = "AIzaSyBHcXDGDZjE43glfOLCCspV1N1NhIX05S4"
genai.configure(api_key=API_KEY)

def get_available_model():
    """ស្វែងរកឈ្មោះ Model ដែលត្រឹមត្រូវក្នុង API Version នេះ"""
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'gemini-1.5-flash' in m.name:
                    return m.name
        return 'gemini-pro' # បម្រុងទុកបើរក Flash មិនឃើញ
    except:
        return 'gemini-pro'

model_name = get_available_model()
model = genai.GenerativeModel(model_name)

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
    menu = st.radio("ជ្រើសរើសមុខងារ", ["📊 Dashboard", "📝 AI Quiz Generator"])
    st.divider()
    st.info(f"Model In Use: {model_name}\nDeveloper: CHAN Sokhoeurn")

# 5. Dashboard Logic
if menu == "📊 Dashboard":
    st.title("📊 Student Management Dashboard")
    st.info("ប្រព័ន្ធដំណើរការធម្មតា។ សូមជ្រើសរើស 'AI Quiz Generator' ដើម្បីបង្កើតតេស្ត។")

# 6. AI Quiz Generator (Optimized for Large PDFs)
else:
    st.title("📝 AI Smart Quiz Generator")
    st.write("បង្កើតវិញ្ញាសាតេស្ត ១០០% តាមកម្រិត និងតាមទំព័រដែលចង់បាន")

    file = st.file_uploader("Upload PDF Book", type="pdf")

    if file:
        # Read PDF using BytesIO
        pdf_reader = PdfReader(io.BytesIO(file.read()))
        total_pages = len(pdf_reader.pages)
        st.success(f"ឯកសារត្រូវបានបញ្ចូល៖ សរុប {total_pages} ទំព័រ")

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            level = st.selectbox("កម្រិតសំណួរ (Level)", ["Elementary", "Intermediate", "Advanced"])
            num_q = st.number_input("ចំនួនសំណួរ", min_value=1, max_value=30, value=10)
        with col2:
            st.write("🎯 **ជ្រើសរើសចន្លោះទំព័រមេរៀន**")
            start_p = st.number_input("ចាប់ពីទំព័រ", min_value=1, max_value=total_pages, value=1)
            end_p = st.number_input("ដល់ទំព័រ", min_value=1, max_value=total_pages, value=min(start_p+5, total_pages))

        if st.button("🚀 ចាប់ផ្តើមបង្កើតវិញ្ញាសា"):
            if start_p > end_p:
                st.error("កំហុស៖ ទំព័រចាប់ផ្ដើមមិនអាចធំជាងទំព័របញ្ចប់ទេ។")
            else:
                with st.spinner(f"AI កំពុងអានទំព័រ {start_p} ដល់ {end_p}..."):
                    try:
                        extracted_text = ""
                        # កម្រិតត្រឹម ៥-១០ ទំព័រក្នុងដង ដើម្បីការពារ Token Limit
                        for i in range(start_p - 1, end_p):
                            extracted_text += pdf_reader.pages[i].extract_text()
                        
                        prompt = f"""
                        Create a professional English grammar test based on this text:
                        {extracted_text[:12000]}
                        
                        Details:
                        Level: {level}
                        Questions: {num_q}
                        Format: Q1: [Question] / (a) (b) (c) (d)
                        Include 'Answer Key' at the end.
                        """
                        
                        response = model.generate_content(prompt)
                        
                        st.divider()
                        st.subheader("✨ វិញ្ញាសាតេស្តដែលបានបង្កើតរួចរាល់")
                        st.markdown(response.text)
                        st.download_button("📥 Download (.txt)", response.text, file_name=f"SEG_Test_P{start_p}-{end_p}.txt")
                        
                    except Exception as e:
                        st.error(f"បញ្ហាបច្ចេកទេស៖ {str(e)}")
                        st.info("ជំនួយ៖ សូមសាកល្បងកាត់បន្ថយចំនួនទំព័រអាន (ឧទាហរណ៍ ម្ដងអានត្រឹម ៥ ទំព័រ)។")

st.markdown('<div class="footer">© 2026 SEG School Management System | Prek Leap Branch</div>', unsafe_allow_html=True)
