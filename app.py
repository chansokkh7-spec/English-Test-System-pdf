import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from PyPDF2 import PdfReader

# 1. Page Configuration
st.set_page_config(
    page_title="SEG Management & AI Quiz Master",
    page_icon="🏫",
    layout="wide"
)

# 2. AI Setup (Using your API Key)
API_KEY = "AIzaSyBHcXDGDZjE43glfOLCCspV1N1NhIX05S4"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. Custom CSS
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
    </style>
    """, unsafe_allow_html=True)

# 4. Grading Logic
def calculate_grade(score):
    if score >= 97: return "A+"
    elif score >= 90: return "A"
    elif score >= 80: return "B"
    elif score >= 70: return "C"
    elif score >= 60: return "D"
    else: return "F"

# 5. Session State initialization
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=['Student Name', 'Level', 'Average (%)', 'Result Grade'])

# 6. Sidebar Navigation
with st.sidebar:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.markdown("<h1 style='text-align: center;'>🏫</h1>", unsafe_allow_html=True)
    
    st.title("SEG System 2026")
    menu = st.radio("Menu", ["📊 Dashboard", "📝 AI Quiz Generator"])
    st.divider()
    st.info("Developed by: CHAN Sokhoeurn, C2/DBA")

# 7. Dashboard Logic
if menu == "📊 Dashboard":
    st.title("🏫 SEG Student Management")
    with st.expander("➕ Add New Student"):
        col1, col2 = st.columns([2, 1])
        with col1:
            name_in = st.text_input("Name")
        with col2:
            level_in = st.selectbox("Level", [f"Level {i}" for i in range(1, 13)])
        
        if st.button("Save Student"):
            if name_in:
                new_row = pd.DataFrame([[name_in, level_in, 0, "F"]], columns=st.session_state.db.columns)
                st.session_state.db = pd.concat([st.session_state.db, new_row], ignore_index=True)
                st.rerun()

    if not st.session_state.db.empty:
        st.subheader("Leaderboard")
        st.dataframe(st.session_state.db, use_container_width=True)
        # Pie Chart
        grade_data = st.session_state.db['Result Grade'].value_counts().reset_index()
        fig = px.pie(grade_data, values='count', names='Result Grade', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

# 8. AI Quiz Logic
elif menu == "📝 AI Quiz Generator":
    st.title("📝 AI Quiz Generator")
    pdf_file = st.file_uploader("Upload PDF File", type="pdf")

    if pdf_file:
        with st.spinner("Reading PDF..."):
            pdf_reader = PdfReader(pdf_file)
            content = ""
            for page in pdf_reader.pages:
                content += page.extract_text()
        
        if st.button("🚀 Generate Test"):
            with st.spinner("AI is creating questions..."):
                prompt = f"Create a grammar test with 10 questions from this text. Include options (a,b,c,d) and answers at the end: {content[:10000]}"
                res = model.generate_content(prompt)
                st.markdown(res.text)

# 9. Footer
st.markdown('<div class="footer-text">© 2026 SEG School Management System</div>', unsafe_allow_html=True)
