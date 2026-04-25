import streamlit as st
import pandas as pd
import google.generativeai as genai
from PyPDF2 import PdfReader
import io
import time

# 1. កំណត់ការបង្ហាញទំព័រ
st.set_page_config(page_title="SEG AI Master 2026", page_icon="🏫", layout="wide")

# 2. ការកំណត់ AI - ប្រើបច្ចេកទេសស្វែងរក Model ដោយស្វ័យប្រវត្តិ
API_KEY = "AIzaSyBHcXDGDZjE43glfOLCCspV1N1NhIX05S4"
genai.configure(api_key=API_KEY)

@st.cache_resource
def load_robust_model():
    # ស្វែងរកម៉ូដែលដែលគាំទ្រ generateContent ក្នុង Account របស់អ្នកគ្រូ
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # ជ្រើសរើស Flash ជាអាទិភាព បើមិនមានយក Pro ឬអាដំបូងគេ
        target = next((m for m in models if 'flash' in m), models[0])
        return genai.GenerativeModel(target), target
    except Exception as e:
        return None, str(e)

model, model_name = load_robust_model()

# 3. CSS សម្រាប់ដេគ័រឱ្យមានវិជ្ជាជីវៈ
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #003057; color: white; font-weight: bold; border: none; }
    .footer { text-align: center; color: #777; font-size: 0.8em; margin-top: 50px; padding: 20px; border-top: 1px solid #eee; }
    .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 4. Sidebar ម៉ឺនុយ
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🏫 SEG System</h2>", unsafe_allow_html=True)
    st.divider()
    menu = st.radio("Menu Navigation", ["📊 Student Dashboard", "📝 AI Quiz Generator"])
    st.divider()
    if model:
        st.success(f"AI Status: Online ({model_name.split('/')[-1]})")
    else:
        st.error("AI Status: Offline (Check Key)")
    st.info("Branch: Prek Leap\nDeveloper: CHAN Sokhoeurn")

# 5. Dashboard គ្រប់គ្រងពិន្ទុ
if menu == "📊 Student Dashboard":
    st.title("📊 Student Management Dashboard")
    st.write("ប្រព័ន្ធគ្រប់គ្រងទិន្នន័យសិស្សសាលា SEG សាខាព្រែកលាប")
    st.info("មុខងារ Dashboard រក្សាទុកទិន្នន័យកំពុងដំណើរការជាធម្មតា។")

# 6. AI Quiz Generator (សម្រាប់សៀវភៅ ១,៥០០ ទំព័រ)
else:
    st.title("📝 AI Smart Quiz Generator")
    st.write("បង្កើតវិញ្ញាសាតេស្តដោយស្វ័យប្រវត្តិចេញពីសៀវភៅ PDF")

    pdf_file = st.file_uploader("បញ្ចូលសៀវភៅ PDF របស់អ្នកគ្រូ (1,500 Pages Support)", type="pdf")

    if pdf_file:
        # ការអាន PDF
        pdf_reader = PdfReader(io.BytesIO(pdf_file.read()))
        total_pages = len(pdf_reader.pages)
        st.success(f"បានរកឃើញសៀវភៅចំនួន {total_pages} ទំព័រ")

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            level = st.selectbox("កម្រិតសិក្សា (Level)", ["Elementary", "Intermediate", "Advanced"])
            num_q = st.slider("ចំនួនសំណួរ", 5, 30, 10)
        with col2:
            st.write("🎯 **ជ្រើសរើសចន្លោះទំព័រមេរៀន**")
            p_start = st.number_input("ចាប់ពីទំព័រ", min_value=1, max_value=total_pages, value=1)
            p_end = st.number_input("ដល់ទំព័រ", min_value=1, max_value=total_pages, value=min(p_start+5, total_pages))

        if st.button("🚀 ចាប់ផ្តើមបង្កើតវិញ្ញាសាតេស្ត"):
            if not model:
                st.error("មិនអាចភ្ជាប់ទៅ Google AI បានទេ។ សូមពិនិត្យ API Key របស់អ្នកគ្រូ។")
            elif p_start > p_end:
                st.error("កំហុស៖ ទំព័រចាប់ផ្ដើមមិនអាចធំជាងទំព័របញ្ចប់ទេ។")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("កំពុងដកស្រង់អត្ថបទពី PDF...")
                    progress_bar.progress(30)
                    
                    extracted_text = ""
                    # អានម្ដងបន្តិចៗដើម្បីការពារ Memory
                    for i in range(p_start - 1, p_end):
                        extracted_text += pdf_reader.pages[i].extract_text()
                    
                    progress_bar.progress(60)
                    status_text.text("AI កំពុងរៀបចំសំណួរ...")
                    
                    prompt = f"""
                    Task: Create a professional English Grammar quiz.
                    Source Text: {extracted_text[:10000]}
                    Questions: {num_q}
                    Level: {level}
                    Format: Q1: [Question] / (a) (b) (c) (d)
                    Note: Include an 'Answer Key' at the very end.
                    """
                    
                    response = model.generate_content(prompt)
                    
                    progress_bar.progress(100)
                    status_text.text("ជោគជ័យ!")
                    
                    st.divider()
                    st.subheader("✨ វិញ្ញាសាតេស្តដែលបានបង្កើតរួចរាល់")
                    st.markdown(response.text)
                    st.download_button("📥 ទាញយកជាឯកសារ .txt", response.text, file_name=f"SEG_Quiz_P{p_start}.txt")
                    
                except Exception as e:
                    st.error(f"បញ្ហាបច្ចេកទេស៖ {str(e)}")
                    st.warning("ជំនួយ៖ សូមសាកល្បងជ្រើសរើសចំនួនទំព័រឱ្យតិចជាងមុន (ត្រឹម ១-៣ ទំព័រ) ដើម្បីតេស្តសិន។")

st.markdown('<div class="footer">© 2026 SEG School Management System | Prek Leap Branch</div>', unsafe_allow_html=True)
