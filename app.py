import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
from PyPDF2 import PdfReader

# 1. Config
st.set_page_config(page_title="SEG AI System", page_icon="🏫", layout="wide")

# 2. AI Setup
API_KEY = "AIzaSyBHcXDGDZjE43glfOLCCspV1N1NhIX05S4"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. CSS
st.markdown("""
<style>
    .stButton>button {width: 100%; border-radius: 8px; background-color: #003057; color: white;}
    .footer {text-align: center; color: #666; font-size: 0.8em; margin-top: 50px;}
</style>
""", unsafe_allow_html=True)

# 4. State
if 'db' not in st.session_state:
    st.session_state.db = pd.DataFrame(columns=['Student Name', 'Level', 'Average (%)', 'Grade'])

# 5. Sidebar
with st.sidebar:
    try:
        st.image("logo.png", use_container_width=True)
    except:
        st.write("🏫 **SEG School**")
    menu = st.radio("Menu", ["📊 Dashboard", "📝 AI Quiz Generator"])
    st.divider()
    st.info("Developed by: CHAN Sokhoeurn")

# 6. Dashboard
if menu == "📊 Dashboard":
    st.title("🏫 SEG Student Management")
    with st.expander("➕ Add Student"):
        col1, col2 = st.columns(2)
        name = col1.text_input("Name")
        lvl = col2.selectbox("Level", [f"Level {i}" for i in range(1, 13)])
        if st.button("Save"):
            if name:
                new_data = pd.DataFrame([[name, lvl, 0, "F"]], columns=st.session_state.db.columns)
                st.session_state.db = pd.concat([st.session_state.db, new_data], ignore_index=True)
                st.rerun()

    if not st.session_state.db.empty:
        st.dataframe(st.session_state.db, use_container_width=True)
        counts = st.session_state.db['Grade'].value_counts().reset_index()
        fig = px.pie(counts, values='count', names='Grade', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

# 7. AI Quiz
else:
    st.title("📝 AI Quiz Generator")
    f = st.file_uploader("Upload PDF", type="pdf")
    if f:
        reader = PdfReader(f)
        text = "".join([p.extract_text() for p in reader.pages])
        if st.button("🚀 Generate 10 Questions"):
            with st.spinner("AI Working..."):
                prompt = f"Create 10 grammar MCQs (Q1: .. / a,b,c,d) with Answer Key based on: {text[:10000]}"
                res = model.generate_content(prompt)
                st.markdown(res.text)

st.markdown('<div class="footer">© 2026 SEG School Management System</div>', unsafe_allow_html=True)
