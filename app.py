import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from PyPDF2 import PdfReader

# ១. ការកំណត់ទំព័រ (Settings)
st.set_page_config(
    page_title="SEG Management & AI Quiz Master", 
    page_icon="🏫", 
    layout="wide"
)

# ២. កំណត់ API Key របស់អ្នកគ្រូ
API_KEY = "AIzaSyBHcXDGDZjE43glfOLCCspV1N1NhIX05S4"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# ៣. CSS សម្រាប់ដេគ័រឱ្យស្អាត
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .footer-text { text-align: center; color: #666; padding: 20px; border-top: 1px solid #eee; margin-top: 50px; }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ៤. មុខងារជំនួយ (Helper Functions)
def calculate_grade(score):
    if score >= 97: return "A+"
    elif score >= 90: return "A"
    elif score >= 80: return "B"
    elif score >= 70: return "C"
    elif score >= 60: return "D"
    else: return "F"

# ៥. Session State សម្រាប់រក្សាទុកទិន្នន័យ
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=['Student Name', 'Level', 'Average (%)', 'Result Grade'])

# --- ៦. SIDEBAR (ម៉ឺនុយបញ្ជា) ---
st.sidebar.image("logo.png", width=120) if st.sidebar.button("Home") else None
menu = st.sidebar.radio("ជ្រើសរើសមុខងារ", ["📊 គ្រប់គ្រងពិន្ទុសិស្ស", "📝 បង្កើតតេស្តស្វ័យប្រវត្តិ (AI)"])

# ==========================================
# មុខងារទី ១៖ គ្រប់គ្រងពិន្ទុសិស្ស SEG
# ==========================================
if menu == "📊 គ្រប់គ្រងពិន្ទុសិស្ស":
    st.title("🏫 SEG Student Management")
    st.write("Branch: **Prek Leap** | Academic Year: 2026")
    
    # បញ្ចូលឈ្មោះសិស្ស
    with st.expander("➕ បន្ថែមឈ្មោះសិស្សថ្មី"):
        new_name = st.text_input("ឈ្មោះសិស្ស")
        if st.button("រក្សាទុកឈ្មោះ"):
            if new_name:
                new_row = pd.DataFrame([[new_name, "Level 1", 0, "F"]], columns=st.session_state.db.columns)
                st.session_state.db = pd.concat([st.session_state.db, new_row], ignore_index=True)
                st.rerun()

    # បង្ហាញតារាងពិន្ទុ
    if not st.session_state.db.empty:
        st.subheader("Leaderboard")
        st.dataframe(st.session_state.db, use_container_width=True)
    else:
        st.info("មិនទាន់មានទិន្នន័យសិស្សនៅឡើយទេ។")

# ==========================================
# មុខងារទី ២៖ បង្កើតតេស្តស្វ័យប្រវត្តិ (AI)
# ==========================================
elif menu == "📝 បង្កើតតេស្តស្វ័យប្រវត្តិ (AI)":
    st.title("📄 AI Quiz Master 100%")
    st.write("Upload PDF ដើម្បីឱ្យ AI រៀបចំវិញ្ញាសាដូចក្នុងសៀវភៅ")

    uploaded_pdf = st.file_uploader("ជ្រើសរើស File Grammar PDF", type="pdf")

    if uploaded_pdf:
        # អាន PDF
        with st.spinner("កំពុងអានខ្លឹមសារមេរៀន..."):
            reader = PdfReader(uploaded_pdf)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        
        st.success("អានឯកសារបានជោគជ័យ!")

        # បញ្ជា AI ឱ្យបង្កើតតេស្ត
        num_q = st.slider("ចំនួនសំណួរដែលចង់បាន", 5, 20, 10)
        
        if st.button("🚀 ចាប់ផ្តើមបង្កើតវិញ្ញាសា"):
            with st.spinner("AI កំពុងរៀបចំសំណួរ និងជម្រើសចម្លើយ..."):
                prompt = f"""
                ផ្អែកលើខ្លឹមសារ PDF នេះ សូមបង្កើតវិញ្ញាសា Grammar Test ចំនួន {num_q} សំណួរ។
                លក្ខខណ្ឌតឹងរ៉ឹង៖
                1. ទម្រង់សំណួរត្រូវតែដូចក្នុងសៀវភៅ៖ Q1: [សំណួរ] / (a) (b) (c) (d)។
                2. ត្រូវមាន "Answer Key" នៅផ្នែកខាងក្រោមបង្អស់។
                3. សំណួរត្រូវតែដកស្រង់ចេញពីខ្លឹមសារមេរៀនក្នុង PDF នេះប៉ុណ្ណោះ។
                
                ខ្លឹមសារ PDF៖
                {text[:15000]}
                """
                
                response = model.generate_content(prompt)
                
                st.divider()
                st.subheader("📝 វិញ្ញាសាតេស្តរបស់អ្នកគ្រូ")
                st.markdown(response.text)
                
                # ប៊ូតុងទាញយក
                st.download_button("📥 Download Test (.txt)", response.text, file_name="SEG_AI_Test.txt")

# --- ៧. FOOTER ---
st.markdown(f"""
    <div class="footer-text">
        <p>Developed with ❤️ by <b>CHAN Sokhoeurn, C2/DBA</b></p>
        <p>© 2026 SEG School Management | AI Integrated</p>
    </div>
    """, unsafe_allow_html=True)
