import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import io

# 1. Config
st.set_page_config(page_title="SEG AI System 2026", layout="wide")

# 2. Secure API Connection
# កូដនេះនឹងឆែករក Key ក្នុង Secrets បើរកមិនឃើញវានឹងប្រាប់ឱ្យអ្នកគ្រូដាក់
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    st.error("⚠️ រកមិនឃើញ API Key ទេ។ សូមដាក់វាក្នុង Streamlit Secrets ជាមុនសិន!")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. Sidebar
with st.sidebar:
    st.title("🏫 SEG System 2026")
    st.info("សាខា៖ ព្រែកលាប\nអ្នកបង្កើត៖ ចាន់ សុខឿន")

# 4. Main App (AI Quiz Generator)
st.title("📝 AI Smart Quiz Generator")
uploaded_file = st.file_uploader("បញ្ចូលសៀវភៅ PDF (រហូតដល់ ១,៥០០ ទំព័រ)", type="pdf")

if uploaded_file:
    reader = PdfReader(io.BytesIO(uploaded_file.read()))
    total_pages = len(reader.pages)
    st.success(f"បានរកឃើញចំនួន {total_pages} ទំព័រ")

    col1, col2 = st.columns(2)
    with col1:
        start_p = st.number_input("ចាប់ពីទំព័រ", 1, total_pages, 1)
    with col2:
        end_p = st.number_input("ដល់ទំព័រ", 1, total_pages, min(start_p+5, total_pages))

    if st.button("🚀 បង្កើតវិញ្ញាសាតេស្ត"):
        with st.spinner("AI កំពុងអានមេរៀន..."):
            try:
                # ទាញយកអត្ថបទ
                content = ""
                for i in range(start_p-1, end_p):
                    content += reader.pages[i].extract_text()
                
                # បញ្ជា AI
                prompt = f"Create 10 grammar MCQs from this text: {content[:10000]}. Level: Intermediate. Include Answer Key."
                response = model.generate_content(prompt)
                
                st.markdown(response.text)
                st.download_button("📥 ទាញយកវិញ្ញាសា", response.text, file_name="SEG_Test.txt")
            except Exception as e:
                st.error(f"បញ្ហា៖ {str(e)}")
