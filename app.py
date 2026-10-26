import streamlit as st
from PIL import Image
import io
import base64

# 1. PAGE CONFIG
st.set_page_config(
    page_title="CivicClear AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. AGGRESSIVE CSS TO FORCE LIGHT MODE, HIDE THEME SWITCHER, & FIX UPLOADER
st.markdown("""
    <style>
    /* Force global light theme on html, body, and main app container */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .stSidebar {
        background-color: #FCFBF9 !important;
        color: #1F2937 !important;
    }

    /* ---------------------------------------------------- */
    /* HIDE THEME SELECTOR ENTIRELY (INCLUDING DROPDOWN)     */
    /* ---------------------------------------------------- */
    [data-testid="stThemeToggle"], .stThemeToggle {
        display: none !important;
    }

    /* Target and remove the System / Light / Dark theme block inside the settings menu */
    div[role="menu"] div:has(button:contains("System")),
    div[role="menu"] div:has(button:contains("Light")),
    div[role="menu"] div:has(button:contains("Dark")),
    div[role="menu"] > div:first-child:has(button) {
        display: none !important;
    }

    /* ---------------------------------------------------- */
    /* FILE UPLOADER STYLING                                */
    /* ---------------------------------------------------- */
    div[data-testid="stFileUploader"] {
        background-color: #FFFFFF !important;
        border: 2px dashed #FF6B6B !important;
        border-radius: 12px !important;
    }

    div[data-testid="stFileUploaderDropzone"] {
        background-color: #FFFFFF !important;
        border: none !important;
        padding: 1.5rem !important;
    }

    div[data-testid="stFileUploaderDropzone"] * {
        background-color: transparent !important;
        color: #1F2937 !important;
        opacity: 1 !important;
        font-weight: 600 !important;
    }
    
    div[data-testid="stFileUploaderDropzone"] button,
    div[data-testid="stFileUploader"] button {
        background-color: #FF6B6B !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }

    /* ---------------------------------------------------- */
    /* SETTINGS MENU DROPDOWN STYLING                       */
    /* ---------------------------------------------------- */
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

# 3. APP UI & UPLOAD LOGIC
st.title("🏛️ CivicClear AI")
st.write("Upload a notice to test the white uploader bar and light-mode layout:")

uploaded_file = st.file_uploader("Upload Notice (Image or PDF)...", type=['jpg', 'png', 'jpeg', 'pdf'])

if uploaded_file:
    st.success("File uploaded successfully!")
    
    if uploaded_file.type.startswith('image'):
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Notice Preview", use_container_width=True)
        except Exception as e:
            st.error(f"Error loading image: {e}")
    else:
        st.info("PDF document uploaded. Ready for processing logic.")
