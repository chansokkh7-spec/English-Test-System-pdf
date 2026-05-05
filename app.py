import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from PyPDF2 import PdfReader

# ១. ការកំណត់ទម្រង់ទំព័រ
st.set_page_config(
    page_title="SEG Management & AI Quiz Master", 
    page_icon="🏫", 
    layout="wide"
)

# ២. កំណត់ API Key និង Model
# ប្រើ Key ដែលអ្នកគ្រូផ្ដល់ឱ្យ៖ AIzaSyBHcXDGDZjE43glfOLCCspV1N1NhIX05S4
genai.configure(api_key="AIzaSyBHcXDGDZjE43glfOLCCspV1N1NhIX05S4")
model = genai.GenerativeModel('gemini-1.5-flash')

# ៣. CSS សម្រាប់ដេគ័រកម្មវិធីឱ្យមានវិជ្ជាជីវៈ
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { 
        width: 100%; border-radius: 10px; height: 3em; 
        background-color: #003057; color: white; font-weight: bold; 
    }
    .footer-text { 
        text-align: center; color: #666; padding: 20px; 
        font-size: 0.9em; border-top: 1px solid #eee; margin-top: 50px; 
    }
    [data-testid="stSidebar"] { background-color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

# ៤. មុខងារគណនា Grade
def calculate_grade(score):
    if score >= 97: return "A+"
    elif score >= 90: return "A"
    elif score >= 80: return "B"
    elif score >= 70: return "C"
    elif score >= 60: return "D"
    else: return "F"

# ៥. Session State សម្រាប់រក្សាទុកទិន្នន័យសិស្ស
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=[
        'Student Name', 'Level', 'Average (%)', 'Result Grade'
    ])

# --- ៦. SIDEBAR MENU ---
with st.sidebar:
    st.image("logo.png", use_container_width=True)
    st.title("Main Menu")
    menu = st.radio("ជ្រើសរើសមុខងារ៖", ["📊 Dashboard ពិន្ទុសិស្ស", "📝 បង្កើតវិញ្ញាសាតេស្ត (AI)"])
    st.divider()
    st.info("Developed by: CHAN Sokhoeurn, C2/DBA")

# ==========================================
# មុខងារទី ១៖ DASHBOARD គ្រប់គ្រងពិន្ទុ
# ==========================================
if menu == "📊 Dashboard ពិន្ទុសិស្ស":
    st.markdown("<h1 style='text-align: center;'>🏫 SEG Student Management</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Academic Year: 2026 | Branch: Prek Leap</p>", unsafe_allow_html=True)
    
    # ផ្នែកបញ្ចូលឈ្មោះសិស្ស
    with st.expander("➕ បន្ថែមឈ្មោះសិស្សថ្មី"):
        c1, c2 = st.columns([3, 1])
        with c1:
            name_input = st.text_input("បញ្ចូលឈ្មោះសិស្ស")
        with c2:
            level_input = st.selectbox("Level", ["Level " + str(i) for i in range(1, 13)])
        
        if st.button("រក្សាទុកទិន្នន័យ"):
            if name_input:
                new_data = pd.DataFrame([[name_input, level_input, 0, "F"]], columns=st.session_state.db.columns)
                st.session_state.db = pd.concat([st.session_state.db, new_data], ignore_index=True)
                st.success(f"បានបញ្ចូលឈ្មោះ {name_input} រួចរាល់!")
                st.rerun()

    if not st.session_state.db.empty:
        st.divider()
        # បង្ហាញ Pie Chart
        st.subheader("📈 Grade Distribution")
        grade_counts = st.session_state.db['Result Grade'].value_counts().reset_index()
        fig = px.pie(grade_counts, values='count', names='Result Grade', hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig, use_container_width=True)

        # តារាងទិន្នន័យ
        st.subheader("🔍 Student Records")
        st.dataframe(st.session_state.db, use_container_width=True)
    else:
        st.info("មិនទាន់មានទិន្នន័យសិស្សទេ។ សូមបញ្ចូលឈ្មោះសិស្សជាមុនសិន។")

# ==========================================
# មុខងារទី ២៖ AI QUIZ MASTER (PDF to TEST)
# ==========================================
elif menu == "📝 បង្កើតវិញ្ញាសាតេស្ត (AI)":
    st.markdown("<h1 style='text-align: center;'>📝 AI Automatic Test Generator</h1>", unsafe_allow_html=True)
    st.write("រៀបចំវិញ្ញាសា Grammar ចេញពីសៀវភៅ PDF របស់អ្នកគ្រូដោយស្វ័យប្រវត្តិ ១០០%")

    uploaded_pdf = st.file_uploader("Upload File PDF (ឧទាហរណ៍៖ Grammar Test.pdf)", type="pdf")

    if uploaded_pdf:
        # អាន PDF
        with st.spinner("AI កំពុងអានមេរៀនក្នុង PDF..."):
            reader = PdfReader(uploaded_pdf)
            pdf_text = ""
            for page in reader.pages:
                pdf_text += page.extract_text()
        
        st.success("អានឯកសារចប់សព្វគ្រប់!")

        # កំណត់ចំនួនសំណួរ
        num_questions = st.number_input("តើអ្នកគ្រូចង់បានសំណួរចំនួនប៉ុន្មាន?", min_value=1, max_value=50, value=10)

        if st.button("🚀 ចាប់ផ្តើមបង្កើតវិញ្ញាសាឥឡូវនេះ"):
            with st.spinner("AI កំពុងរៀបចំសំណួរ និងជម្រើសចម្លើយ..."):
                # Prompt បញ្ជា AI ឱ្យធ្វើតាមសៀវភៅ ១០០%
                prompt = f"""
                You are a professional English Teacher. Based on the provided PDF content, create a Grammar Test.
                Total Questions: {num_questions}
                Format Requirements:
                1. Each question must follow this style: "Q1: [Question] / (a) [Option] (b) [Option] (c) [Option] (d) [Option]"
                2. Provide an "Answer Key" at the very bottom.
                3. Ensure the questions match the difficulty level found in the PDF.
                
                Content:
                {pdf_text[:15000]}
                """
                
                response = model.generate_content(prompt)
                
                st.divider()
                st.subheader("✨ វិញ្ញាសាតេស្តដែលបានរៀបចំរួចរាល់")
                st.markdown(response.text)
                
                # ប៊ូតុងទាញយកលទ្ធផល
                st.download_button("📥 Download Test (Text File)", response.text, file_name="AI_Generated_Test.txt")

# --- ៧. FOOTER ---
st.markdown(f"""
    <div class="footer-text">
        <p>Developed with ❤️ by <b>CHAN Sokhoeurn, C2/DBA</b></p>
        <p>© 2026 SEG School Management System | Prek Leap Branch</p>
    </div>
    """, unsafe_allow_html=True)
