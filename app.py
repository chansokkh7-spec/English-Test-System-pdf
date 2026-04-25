import streamlit as st
import pandas as pd
import google.generativeai as genai
from PyPDF2 import PdfReader
import io

# 1. កំណត់ការបង្ហាញទំព័រ
st.set_page_config(page_title="SEG AI Master 2026", page_icon="🏫", layout="wide")

# 2. ការកំណត់ AI - ប្រើបច្ចេកទេសបត់បែន (Flexible Model Discovery)
API_KEY = "AIzaSyBHcXDGDZjE43glfOLCCspV1N1NhIX05S4"
genai.configure(api_key=API_KEY)

@st.cache_resource
def get_working_model():
    # បញ្ជីឈ្មោះម៉ូដែលដែលយើងចង់ប្រើតាមលំដាប់អាទិភាព
    model_candidates = [
        'gemini-1.5-flash', 
        'gemini-1.5-flash-latest', 
        'gemini-pro'
    ]
    
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # ស្វែងរកម៉ូដែលណាដែល Account អ្នកគ្រូមានសិទ្ធិប្រើ
    for candidate in model_candidates:
        for available in available_models:
            if candidate in available:
                return genai.GenerativeModel(available), available
                
    # បើរកមិនឃើញក្នុងបញ្ជីខាងលើ យកអាដំបូងគេដែលប្រើបាន
    return genai.GenerativeModel(available_models[0]), available_models[0]

try:
    model, model_name = get_working_model()
except Exception as e:
    st.error("មិនអាចភ្ជាប់ទៅកាន់ Google AI បានទេ។ សូមពិនិត្យ API Key របស់អ្នកគ្រូ។")
    st.stop()

# 3. រចនាប័ទ្មកម្មវិធី
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #003057; color: white; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #004a87; color: white; }
    .footer { text-align: center; color: #777; font-size: 0.8em; margin-top: 50px; padding: 20px; border-top: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

# 4. Sidebar ម៉ឺនុយ
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🏫 SEG System</h2>", unsafe_allow_html=True)
    st.divider()
    menu = st.radio("Menu Navigation", ["📊 Student Dashboard", "📝 AI Quiz Generator"])
    st.divider()
    st.success(f"System Online: {model_name.split('/')[-1]}")
    st.info("Branch: Prek Leap\nDeveloper: CHAN Sokhoeurn")

# 5. Dashboard គ្រប់គ្រងពិន្ទុ
if menu == "📊 Student Dashboard":
    st.title("📊 Student Management Dashboard")
    st.write("ប្រព័ន្ធគ្រប់គ្រងទិន្នន័យសិស្សសាលា SEG សាខាព្រែកលាប")
    st.info("មុខងាររក្សាទុកទិន្នន័យកំពុងដំណើរការ។ អ្នកគ្រូអាចប្រើ AI បង្កើតវិញ្ញាសានៅក្នុងម៉ឺនុយខាងឆ្វេង។")

# 6. AI Quiz Generator (រៀបចំសម្រាប់សៀវភៅ ១៥០០ ទំព័រ)
else:
    st.title("📝 AI Smart Quiz Generator")
    st.write("បង្កើតវិញ្ញាសាតេស្តដោយស្វ័យប្រវត្តិចេញពីសៀវភៅ PDF")

    pdf_file = st.file_uploader("បញ្ចូលសៀវភៅ PDF របស់អ្នកគ្រូ", type="pdf")

    if pdf_file:
        # ការអាន PDF
        with st.spinner("កំពុងអានឯកសារ..."):
            pdf_reader = PdfReader(io.BytesIO(pdf_file.read()))
            total_pages = len(pdf_reader.pages)
            st.success(f"បានរកឃើញសៀវភៅចំនួន {total_pages} ទំព័រ")

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            level = st.selectbox("កម្រិតសិក្សា (Level)", ["Elementary", "Intermediate", "Advanced"])
            num_q = st.slider("ចំនួនសំណួរ", 5, 20, 10)
        with col2:
            st.write("🎯 **ជ្រើសរើសចន្លោះទំព័រមេរៀន**")
            p_start = st.number_input("ចាប់ពីទំព័រ", min_value=1, max_value=total_pages, value=1)
            p_end = st.number_input("ដល់ទំព័រ", min_value=1, max_value=total_pages, value=min(p_start+5, total_pages))

        if st.button("🚀 ចាប់ផ្តើមបង្កើតវិញ្ញាសាតេស្ត"):
            if p_start > p_end:
                st.error("កំហុស៖ ទំព័រចាប់ផ្ដើមមិនអាចធំជាងទំព័របញ្ចប់ទេ។")
            else:
                with st.spinner(f"AI កំពុងវិភាគមេរៀនពីទំព័រ {p_start} ដល់ {p_end}..."):
                    try:
                        # ចាប់យកអត្ថបទ
                        extracted_text = ""
                        for i in range(p_start - 1, p_end):
                            extracted_text += pdf_reader.pages[i].extract_text()
                        
                        # បញ្ជា AI (Prompt Engineering)
                        prompt = f"""
                        Context: This is an English Grammar lesson from a book.
                        Task: Create a multiple-choice quiz.
                        Source: {extracted_text[:12000]}
                        Number of Questions: {num_q}
                        Level: {level}
                        Format: Q1: [Question] / (a) (b) (c) (d)
                        Final Section: Include an 'Answer Key' at the bottom.
                        """
                        
                        response = model.generate_content(prompt)
                        
                        st.divider()
                        st.subheader("✨ វិញ្ញាសាតេស្តដែលបានបង្កើតរួចរាល់")
                        st.markdown(response.text)
                        st.download_button("📥 ទាញយកជាឯកសារ .txt", response.text, file_name=f"SEG_Quiz_P{p_start}.txt")
                        
                    except Exception as e:
                        st.error(f"បញ្ហាបច្ចេកទេស៖ {str(e)}")
                        st.warning("ជំនួយ៖ សូមសាកល្បងជ្រើសរើសចំនួនទំព័រឱ្យតិចជាងមុន។")

st.markdown('<div class="footer">© 2026 SEG School Management System | Prek Leap Branch</div>', unsafe_allow_html=True)
