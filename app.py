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

# ២. ការកំណត់ AI (ប្រើ Key ដែលអ្នកគ្រូផ្ដល់ឱ្យ)
API_KEY = "AIzaSyBHcXDGDZjE43glfOLCCspV1N1NhIX05S4"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# ៣. CSS សម្រាប់ដេគ័រឱ្យស្អាត និងជំនួយដល់ការមើលលើទូរស័ព្ទ
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        width: 100%; border-radius: 10px; height: 3em; 
        background-color: #003057; color: white; font-weight: bold; 
    }
    .footer-text { 
        text-align: center; color: #666; padding: 20px; 
        font-size: 0.8em; border-top: 1px solid #eee; margin-top: 50px; 
    }
    /* រៀបចំ Font ឱ្យស្រួលមើល */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
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

# ៥. Session State សម្រាប់រក្សាទុកទិន្នន័យ (កុំឱ្យបាត់ពេល Refresh)
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=['Student Name', 'Level', 'Average (%)', 'Result Grade'])

# --- ៦. SIDEBAR MENU (រៀបចំថ្មីការពារ Error) ---
with st.sidebar:
    # បង្ហាញ Logo បើមាន បើមិនមានបង្ហាញ Icon ជំនួស (ការពារ MediaFileStorageError)
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.markdown("<h1 style='text-align: center;'>🏫</h1>", unsafe_allow_html=True)
        st.caption("Tip: បង្ហោះរូបភាព logo.png ចូល GitHub ដើម្បីបង្ហាញ Logo សាលា")
    
    st.title("SEG System 2026")
    menu = st.radio("ជ្រើសរើសមុខងារ៖", ["📊 Dashboard ពិន្ទុសិស្ស", "📝 បង្កើតវិញ្ញាសាតេស្ត (AI)"])
    st.divider()
    st.info("Developed by: CHAN Sokhoeurn, C2/DBA")

# ==========================================
# មុខងារទី ១៖ DASHBOARD គ្រប់គ្រងពិន្ទុ
# ==========================================
if menu == "📊 Dashboard ពិន្ទុសិស្ស":
    st.markdown("<h1 style='text-align: center;'>🏫 SEG Student Management</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Branch: Prek Leap | Developer: Sokhoeurn</p>", unsafe_allow_html=True)
    
    # ផ្នែកបញ្ចូលឈ្មោះសិស្ស
    with st.expander("➕ បន្ថែមឈ្មោះសិស្សថ្មី"):
        col1, col2 = st.columns([2, 1])
        with col1:
            name_in = st.text_input("បញ្ចូលឈ្មោះសិស្ស")
        with col2:
            level_in = st.selectbox("កម្រិតសិក្សា", ["Level " + str(i) for i in range(1, 13)])
        
        if st.button("រក្សាទុកឈ្មោះសិស្ស"):
            if name_in:
                new_entry = pd.DataFrame([[name_in, level_in, 0, "F"]], columns=st.session_state.db.columns)
                st.session_state.db = pd.concat([st.session_state.db, new_entry], ignore_index=True)
                st.success(f"បានបញ្ចូលឈ្មោះ {name_in}!")
                st.rerun()

    if not st.session_state.db.empty:
        st.divider()
        # បង្ហាញ Pie Chart បែងចែកនិទ្ទេស
        st.subheader("📈 Grade Analysis")
        grade_data = st.session_state.db['Result Grade'].value_counts().reset_index()
        fig = px.pie(grade_data, values='count', names='Result Grade', hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)

        # តារាងទិន្នន័យ
        st.subheader("🔍 Student List")
        st.dataframe(st.session_state.db, use_container_width=True)
        
        # ប៊ូតុងទាញយកទិន្នន័យជា Excel/CSV
        csv = st.session_state.db.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 Download Report (CSV)", csv, "SEG_Report_2026.csv", "text/csv")
    else:
        st.info("💡 សូមបញ្ចូលឈ្មោះសិស្សនៅក្នុងប្រអប់ខាងលើ ដើម្បីចាប់ផ្តើមប្រើប្រាស់ Dashboard។")

# ==========================================
# មុខងារទី ២៖ AI QUIZ MASTER (PDF to TEST)
# ==========================================
elif menu == "📝 បង្កើតវិញ្ញាសាតេស្ត (AI)":
    st.markdown("<h1 style='text-align: center;'>📝 AI Quiz Generator</h1>", unsafe_allow_html=True)
    st.write("រៀបចំវិញ្ញាសា Grammar ចេញពី PDF ស្វ័យប្រវត្តិ ១០០% តាមបែបស្តង់ដារ")

    pdf_file = st.file_uploader("Upload ឯកសារ Grammar PDF របស់អ្នកគ្រូ", type="pdf")

    if pdf_file:
        with st.spinner("AI កំពុងអានមេរៀនក្នុង PDF..."):
            pdf_reader = PdfReader(pdf_file)
            content = ""
            for page in pdf_reader.pages:
                content += page.extract_text()
        
        st.success("អានឯកសារជោគជ័យ!")

        # កំណត់ចំនួនសំណួរ
        q_count = st.slider("ជ្រើសរើសចំនួនសំណួរដែលចង់បាន", 5, 30, 10)

        if st.button("🚀 ចាប់ផ្តើមបង្កើតតេស្ត"):
            with st.spinner("AI កំពុងរៀបចំសំណួរ..."):
                # បញ្ជា AI ឱ្យរៀបចំទម្រង់ដូចសៀវភៅរបស់អ្នកគ្រូ
                prompt = f"""
                You are a Senior English Language Teacher. Using the provided PDF text, generate a professional Grammar Test.
                Number of questions: {q_count}
                Format: 
                - Multiple Choice (A, B, C, D)
                - Structure: "Q1: [Question] / (a) (b) (c) (d)"
                - Must include "Answer Key" at the end.
                - Questions must be derived from the specific topics in the PDF.
                
                Content Reference:
                {content[:15000]}
                """
                
                res = model.generate_content(prompt)
                
                st.divider()
                st.subheader("✨ វិញ្ញាសាតេស្តដែលបានរៀបចំរួចរាល់")
                st.markdown(res.text)
                
                # ប៊ូតុង Download
                st.download_button("📥 Download Test (TXT)", res.text, file_name="SEG_AI_Test_Paper.txt")

# --- ៧. FOOTER ---
st.markdown(f"""
    <div class="footer-text">
        <p>Developed with ❤️ by <b>CHAN Sokhoeurn, C2/DBA</b></p>
        <p>© 2026 SEG School Management System | Prek Leap Branch</p>
    </div>
    """, unsafe_allow_html=True)
