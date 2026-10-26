import streamlit as st
from PIL import Image
import io
import base64

# 1. PAGE CONFIG
st.set_page_config(page_title="CivicClear AI", layout="wide")

# 2. AGGRESSIVE CSS TO FORCE LIGHT MODE AND HIDE THEME SWITCHER
st.markdown("""
    <style>
    /* Force global light theme on html, body, and main app container */
    html, body, [data-testid="stApp"], [data-testid="stHeader"], .stSidebar {
        background-color: #FCFBF9 !important;
        color: #1F2937 !important;
    }

    /* Force the outer uploader container to pure white */
    div[data-testid="stFileUploader"] {
        background-color: #FFFFFF !important;
        border: 2px dashed #FF6B6B !important;
        border-radius: 12px !important;
    }

    /* Force the inner dropzone to pure white */
    div[data-testid="stFileUploaderDropzone"] {
        background-color: #FFFFFF !important;
        border: none !important;
        padding: 1.5rem !important;
    }

    /* Force ALL nested child divs inside the dropzone to be white */
    div[data-testid="stFileUploaderDropzone"] div {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
    }
    
    /* Force ALL text, labels, and metadata inside the dropzone to be dark charcoal */
    div[data-testid="stFileUploaderDropzone"] p,
    div[data-testid="stFileUploaderDropzone"] span,
    div[data-testid="stFileUploaderDropzone"] div,
    div[data-testid="stFileUploaderDropzone"] label {
        color: #1F2937 !important;
        opacity: 1 !important;
        font-weight: 600 !important;
    }
    
    /* Force the "Upload" button to have a coral background and white text */
    div[data-testid="stFileUploaderDropzone"] button,
    div[data-testid="stFileUploader"] button {
        background-color: #FF6B6B !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }

    /* 3. HIDE THEME TOGGLE & SETTINGS THEME OPTIONS COMPLETELY */
    .stThemeToggle {
        display: none !important;
    }

    /* Hide theme options / radio toggles within the main settings popover menu */
    div[role="menu"] div:has(input[type="radio"]) {
        display: none !important;
    }

    /* 4. STYLE THE REMAINING SETTINGS MENU (Rerun, Clear cache, Print, etc.) */
    div[role="menu"] {
        background-color: #FFFFFF !important;
        color: #1F2937 !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }

    div[role="menu"] span,
    div[role="menu"] div,
    div[role="menuitem"],
    div[role="menuitem"] p {
        color: #1F2937 !important;
        font-weight: 600 !important;
    }

    div[role="menuitem"]:hover {
        background-color: #F3F4F6 !important;
        color: #111827 !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. SIMPLE UI
st.title("🏛️ CivicClear AI")
st.write("Upload a notice to test the white uploader bar:")

uploaded_file = st.file_uploader("Upload Notice (Image or PDF)...", type=['jpg', 'png', 'jpeg', 'pdf'])

if uploaded_file:
    st.success("File uploaded successfully!")
    # Display image if it's an image
    if uploaded_file.type.startswith('image'):
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
