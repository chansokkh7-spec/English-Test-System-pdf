import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import io

# 1. កំណត់ទំព័រ
st.set_page_config(page_title="SEG Master 2026", layout="wide")

# 2. ការហៅ API Key ពី Secrets
# អ្នកគ្រូត្រូវដាក់ GOOGLE_API_KEY ក្នុង Streamlit Settings > Secrets
if "GOOGLE_API_KEY" in st.secrets:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
else:
    # បើមិនទាន់ដាក់ក្នុង Secrets ទេ អាចដាក់បញ្ចូលក្នុងប្រអប់នេះដើម្បីតេស្តសិន
    API_KEY = st.text_input("សូមបញ្ចូល API Key ថ្មីរបស់អ្នកគ្រូត្រង់នេះ៖", type="password")

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        st.success("✅ ភ្ជាប់ទៅកាន់ Google AI រួចរាល់!")
    except Exception as e:
        st.error(f"❌ កំហុសក្នុងការភ្ជាប់៖ {e}")
else:
    st.warning("⚠️ សូមបញ្ចូល API Key ដើម្បីដំណើរការកម្មវិធី។")
    st.stop()

# 3. មុខងារអាន PDF និងបង្កើត Quiz
st.title("📝 SEG AI Quiz Generator")
file = st.file_uploader("បញ្ចូលសៀវភៅ PDF (1,500 ទំព័រ)", type="pdf")

if file:
    reader = PdfReader(io.BytesIO(file.read()))
    total = len(reader.pages)
    st.info(f"សៀវភៅនេះមានសរុប {total} ទំព័រ")

    col1, col2 = st.columns(2)
    with col1:
        s_p = st.number_input("ចាប់ពីទំព័រ", 1, total, 1)
    with col2:
        e_p = st.number_input("ដល់ទំព័រ", 1, total, min(s_p+5, total))

    if st.button("🚀 បង្កើតវិញ្ញាសា"):
        with st.spinner("AI កំពុងវិភាគ..."):
            try:
                text = ""
                for i in range(s_p-1, e_p):
                    text += reader.pages[i].extract_text()
                
                prompt = f"Create a grammar test from this text: {text[:10000]}. Format: Q1: [Question] / (a,b,c,d). Include Answer Key."
                response = model.generate_content(prompt)
                
                st.markdown(response.text)
                st.download_button("📥 ទាញយកវិញ្ញាសា", response.text, file_name="SEG_Test.txt")
            except Exception as e:
                st.error(f"បញ្ហាបច្ចេកទេស៖ {e}")

st.markdown("---")
st.caption("Developed by: CHAN Sokhoeurn | Prek Leap Branch")
