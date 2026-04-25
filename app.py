import streamlit as st
import pandas as pd
import google.generativeai as genai
from PyPDF2 import PdfReader
import io

# 1. Config
st.set_page_config(page_title="SEG AI Master 2026", page_icon="🏫", layout="wide")

# 2. Secure API Setup (ប្រើ Streamlit Secrets ដើម្បីសុវត្ថិភាព)
# ប្រសិនបើអ្នកគ្រូមិនទាន់បានដាក់ក្នុង Secrets កូដនឹងប្រើ Key ចាស់ជាបណ្ដោះអាសន្ន
api_key = st.secrets.get("GOOGLE_API_KEY", "AIzaSyBHcXDGDZjE43glfOLCCspV1N1NhIX05S4")
genai.configure(api_key=api_key)

@st.cache_resource
def get_model():
    try:
        # ស្វែងរក Model ដែលដើរក្នុងតំបន់របស់អ្នកគ្រូ
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        name = next((m for m in models if '1.5-flash' in m), models[0])
        return genai.GenerativeModel(name), name
    except:
        return None, "Error"

model, model_name = get_model()

# 3. CSS
st.markdown("""
<style>
    .stButton>button {width: 100%; border-radius: 10px; height: 3.5em; background-color: #003057; color: white; font-weight: bold;}
    .footer {text-align: center; color: #888; font-size: 0.8em; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px;}
</style>
""", unsafe_allow_html=True)

# 4. Sidebar
with st.sidebar:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.markdown("<h2 style='text-align: center;'>🏫 SEG System</h2>", unsafe_allow_html=True)
    st.divider()
    menu = st.radio("Menu", ["📊 Dashboard", "📝 AI Quiz Generator"])
    st.divider()
    if model:
        st.success(f"AI: Online ({model_name.split('/')[-1]})")
    else:
        st.error("AI: Offline (Key Blocked)")
    st.info("Branch: Prek Leap\nDeveloper: CHAN Sokhoeurn")

# 5. Dashboard
if menu == "📊 Dashboard":
    st.title("📊 Student Management Dashboard")
    st.info("ប្រព័ន្ធគ្រប់គ្រងពិន្ទុដំណើរការធម្មតា។")

# 6. AI Quiz Generator
else:
    st.title("📝 AI Smart Quiz Generator")
    f = st.file_uploader("Upload PDF Book", type="pdf")
    if f:
        pdf = PdfReader(io.BytesIO(f.read()))
        total = len(pdf.pages)
        st.success(f"ឯកសារមានសរុប {total} ទំព័រ")
        
        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            lvl = st.selectbox("Level", ["Elementary", "Intermediate", "Advanced"])
            num = st.number_input("Number of Questions", 1, 30, 10)
        with c2:
            st.write("🎯 **ជ្រើសរើសចន្លោះទំព័រ**")
            s_p = st.number_input("From Page", 1, total, 1)
            e_p = st.number_input("To Page", 1, total, min(s_p+5, total))

        if st.button("🚀 Generate Quiz Now"):
            if not model:
                st.error("API Key របស់អ្នកគ្រូត្រូវបាន Google បិទហើយ។ សូមបង្កើត Key ថ្មី។")
            else:
                with st.spinner("AI កំពុងអានមេរៀន..."):
                    try:
                        text = "".join([pdf.pages[i].extract_text() for i in range(s_p-1, e_p)])
                        prompt = f"Create a {lvl} English test. Questions: {num}. Format: Q1: [Question] / (a,b,c,d). Include Answer Key. Text: {text[:10000]}"
                        res = model.generate_content(prompt)
                        st.markdown(res.text)
                        st.download_button("📥 Download", res.text, file_name="Quiz.txt")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

st.markdown('<div class="footer">© 2026 SEG School Management System | Prek Leap Branch</div>', unsafe_allow_html=True)
