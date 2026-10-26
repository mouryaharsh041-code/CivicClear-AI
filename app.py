import streamlit as st
from PIL import Image
import io
import base64

# 1. FORCE LIGHT THEME (This is the most important line)
st.config_set('theme.base', 'light')

# 2. PAGE CONFIG
st.set_page_config(page_title="CivicClear AI", layout="wide")

# 3. AGGRESSIVE CSS TO FIX THE BLACK UPLOADER BAR
st.markdown("""
    <style>
    /* Force the file uploader dropzone to be pure white */
    div[data-testid="stFileUploaderDropzone"] {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        border: 2px dashed #FF6B6B !important;
    }
    /* Force all text inside the uploader to be dark charcoal */
    div[data-testid="stFileUploaderDropzone"] p,
    div[data-testid="stFileUploaderDropzone"] span,
    div[data-testid="stFileUploaderDropzone"] div {
        color: #1F2937 !important;
        opacity: 1 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 4. SIMPLE UI
st.title("🏛️ CivicClear AI")
st.write("Upload a notice to test the white uploader bar:")

uploaded_file = st.file_uploader("Upload Notice (Image or PDF)...", type=['jpg', 'png', 'jpeg', 'pdf'])

if uploaded_file:
    st.success("File uploaded successfully!")
    st.image(uploaded_file)
