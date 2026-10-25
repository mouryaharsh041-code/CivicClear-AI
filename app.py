import streamlit as st
import base64
import re
import io
import json
import os
from PIL import Image
import fitz  # PyMuPDF
from gtts import gTTS
import requests
from datetime import date

import db  # Our database module

# --- PAGE CONFIG ---
st.set_page_config(page_title="CivicClear AI | SaralNotice", page_icon="🏛️", layout="wide")

# =========================================================
# === BILINGUAL UI STRINGS ===
# =========================================================
EN = {
    "title": "CivicClear AI | SaralNotice",
    "subtitle": "Actionable Clarity for Everyone",
    "sidebar_lang": "Language / भाषा",
    "sidebar_keys": "🔑 API Keys",
    "key_openrouter": "OpenRouter API Key",
    "key_gemini": "Gemini API Key (Backup)",
    "cap_single": "Single-user dashboard. No login required.",
    "tab_analyze": "🚀 Analyze New Notice",
    "tab_active": "📂 Active / Available",
    "tab_approach": "⏰ Approaching Soon",
    "tab_expired": "❌ Expired / Crossed",
    "tab_important": "⭐ Important",
    "uploader_label": "Upload Notice (Image or PDF)...",
    "processing": "Processing file...",
    "ready": "Ready to analyze!",
    "btn_upload_new": "🔄 Upload New Notice",
    "btn_analyze": "🚀 Analyze Notice",
    "result_header": "📋 Result",
    "summary_label": "Summary / सारांश",
    "summary_header": "Summary / सारांश",
    "deadline_label": "Deadline / अंतिम तिथि",
    "deadline_header": "Deadline / अंतिम तिथि",
    "note_label": "Note / टिप्पणी",
    "note_header": "Important Note / महत्वपूर्ण टिप्पणी",
    "checklist_label": "Interactive Action Steps / कार्यवाही चरण",
    "checklist_header": "Interactive Action Steps",
    "completed_text": "**{done} of {total} tasks completed**",
    "audio_label": "🎧 Listen to Audio / ऑडियो सुनें",
    "no_notices": "No {category} notices.",
    "btn_mark_imp": "☆ Mark Important",
    "btn_mark_imp_done": "✓ Important",
    "btn_delete": "🗑️ Delete Notice",
    "save_success": "✅ Notice saved to your dashboard!",
    "already_saved": "ℹ️ This notice is already saved.",
    "api_warning": "⚠️ Please enter at least one API key in the sidebar.",
    "upload_first": "Please upload an image or PDF first.",
    "analyzing": "Analyzing document...",
    "try_openrouter": "Trying OpenRouter (Primary)...",
    "try_gemini": "Fallback: Google Gemini...",
    "done_model": "Done via {model}",
    "all_fail": "All APIs failed.",
    "api_fail": "❌ Both Primary and Backup APIs failed. Please check your keys.",
    "audio_err": "Audio generation error: {e}",
    "no_deadline": "No deadline mentioned",
    "confirm_delete_title": "⚠️ Confirm Deletion",
    "confirm_delete_msg": "Are you sure you want to delete this notice? This action cannot be undone.",
    "btn_yes": "Yes, Delete",
    "btn_cancel": "Cancel",
}

HI = {
    "title": "🏛️ सिविक क्लियर एआई | सरल नोटिस",
    "subtitle": "सभी के लिए कार्रवाई योग्य स्पष्टता",
    "sidebar_lang": "भाषा / Language",
    "sidebar_keys": "🔑 अन्वेषण कुंजियाँ",
    "key_openrouter": "ओपनराउटर एपीआई कुंजी",
    "key_gemini": "जेमिनी एपीआई कुंजी (बैकअप)",
    "cap_single": "एकल-उपयोगकर्ता डैशबोर्ड। लॉगिन की आवश्यकता नहीं।",
    "tab_analyze": "🚀 नया नोटिस विश्लेषण करें",
    "tab_active": "📁 सक्रिय / उपलब्ध",
    "tab_approach": "⏰ जल्द आने वाला",
    "tab_expired": "❌ समाप्त / समय सीमा पार",
    "tab_important": "⭐ महत्वपूर्ण",
    "uploader_label": "नोटिस अपलोड करें (चित्र या पीडीएफ)...",
    "processing": "फ़ाइल संसाधित हो रही है...",
    "ready": "विश्लेषण के लिए तैयार है!",
    "btn_upload_new": "🔄 नया नोटिस अपलोड करें",
    "btn_analyze": "🚀 नोटिस का विश्लेषण करें",
    "result_header": "📋 परिणाम",
    "summary_label": "सारांश / Summary",
    "summary_header": "सारांश / Summary",
    "deadline_label": "अंतिम तिथि / Deadline",
    "deadline_header": "अंतिम तिथि / Deadline",
    "note_label": "टिप्पणी / Note",
    "note_header": "महत्वपूर्ण टिप्पणी / Important Note",
    "checklist_label": "कार्यवाही चरण / Interactive Action Steps",
    "checklist_header": "कार्यवाही चरण / Action Steps",
    "completed_text": "**{total} में से {done} कार्य पूर्ण हुए**",
    "audio_label": "🎧 ऑडियो सुनें / Listen to Audio",
    "no_notices": "कोई {category} नोटिस नहीं।",
    "btn_mark_imp": "☆ महत्वपूर्ण चिह्नित करें",
    "btn_mark_imp_done": "✓ महत्वपूर्ण",
    "btn_delete": "🗑️ नोटिस हटाएँ",
    "save_success": "✅ नोटिस आपके डैशबोर्ड पर सहेजा गया!",
    "already_saved": "ℹ️ यह नोटिस पहले से सहेजा गया है।",
    "api_warning": "⚠️ कृपया साइडबार में कम से कम एक एपीआई कुंजी दर्ज करें।",
    "upload_first": "कृपया पहले एक चित्र या पीडीएफ अपलोड करें।",
    "analyzing": "दस्तावेज़ का विश्लेषण हो रहा है...",
    "try_openrouter": "ओपनराउटर का प्रयास कर रहा है (प्राथमिक)...",
    "try_gemini": "फॉलबैक: जेमिनी (बैकअप)...",
    "done_model": "मॉडल के माध्यम से पूरा हुआ: {model}",
    "all_fail": "सभी एपीआई विफल रहे।",
    "api_fail": "❌ प्राथमिक और बैकअप दोनों एपीआई विफल रहे। कृपया अपनी कुंजियाँ जांचें।",
    "audio_err": "ऑडियो जनरेशन त्रुटि: {e}",
    "no_deadline": "कोई अंतिम तिथि नहीं",
    "confirm_delete_title": "⚠️ पुष्टिकरण",
    "confirm_delete_msg": "क्या आप वाकई इस नोटिस को हटाना चाहते हैं? यह कार्रवाई वापस नहीं ली जा सकती।",
    "btn_yes": "हाँ, हटाएँ",
    "btn_cancel": "रद्द करें",
}

# =========================================================
# === LANGUAGE SYNC ===
# =========================================================
if "lang_sb" in st.session_state:
    st.session_state.current_lang = st.session_state["lang_sb"]
current_lang = st.session_state.get("current_lang", "English")
L = HI if current_lang == "Hindi" else EN

# --- CUSTOM SIDEBAR LOGO HTML ---
LOGO_HTML = """
<div style="display: flex; align-items: center; gap: 14px; margin-bottom: 2.5rem; margin-top: 1rem;">
    <div style="background-color: #FF6B6B; width: 56px; height: 56px; border-radius: 14px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(255, 107, 107, 0.25);">
        <svg width="34" height="34" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 11L12 5L20 11" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M4 11H20" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round"/>
            <path d="M7 11V16" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>
            <path d="M12 11V16" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>
            <path d="M17 11V16" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>
            <path d="M5 16H19V18H5V16Z" stroke="#FFFFFF" stroke-width="2" stroke-linejoin="round"/>
            <path d="M11 16V13H13V16" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    </div>
    <div style="display: flex; flex-direction: column; line-height: 1.2;">
        <span style="font-family: 'Inter', sans-serif; font-size: 1.35rem; font-weight: 700; color: #1F2937; letter-spacing: -0.5px;">CivicClear AI</span>
        <span style="font-family: 'Inter', sans-serif; font-size: 0.65rem; font-weight: 600; color: #6B7280; text-transform: uppercase; letter-spacing: 2px;">SARALNOTICE</span>
    </div>
</div>
"""

# --- PREMIUM CSS (WARM MINIMALIST THEME + UPLOADER FIX + INPUT VISIBILITY FIX) ---
st.markdown("""
    <style>
    /* 1. FORCE LIGHT MODE GLOBALLY TO PREVENT DARK THEME CONFLICTS */
    html, body, [data-testid="stApp"] {
        background-color: #FCFBF9 !important;
        color: #1F2937 !important;
        font-family: 'Inter', sans-serif;
    }

    /* Force all text, headers, and labels to dark charcoal */
    h1, h2, h3, h4, h5, h6, span, p, label, div {
        color: #1F2937 !important;
    }

    /* 2. SIDEBAR STYLING */
    .stSidebar {
        background-color: #F4EFE6 !important;
        color: #1F2937 !important;
        border-right: 1px solid #E5E7EB !important;
    }
    .stSidebar .stMarkdown, .stSidebar .stMarkdown p, .stSidebar label {
        color: #1F2937 !important;
    }
    .stSidebar .stSelectbox > div > div, .stSidebar .stTextInput > div > div {
        background-color: #FFFFFF !important;
        color: #1F2937 !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 8px !important;
    }

    /* 3. FILE UPLOADER HIGH CONTRAST FIX (The core fix for the black box) */
    /* Outer container of the uploader */
    div[data-testid="stFileUploader"] {
        background-color: #FFFFFF !important;
        border: 2px dashed #FF6B6B !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02) !important;
    }
    
    /* Inner dropzone area - force clean white background */
    div[data-testid="stFileUploaderDropzone"] {
        background-color: #FFFFFF !important;
        border: none !important;
        padding: 1rem !important;
        border-radius: 12px !important;
    }
    
    /* Force ALL text, labels, and metadata inside the dropzone to be dark charcoal */
    div[data-testid="stFileUploaderDropzone"] p,
    div[data-testid="stFileUploaderDropzone"] span,
    div[data-testid="stFileUploaderDropzone"] div,
    div[data-testid="stFileUploaderDropzone"] label {
        color: #1F2937 !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }
    
    /* The "Upload" Button inside the dropzone - force Coral background & white text */
    div[data-testid="stFileUploaderDropzone"] button,
    div[data-testid="stFileUploader"] button {
        background-color: #FF6B6B !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 4px rgba(255, 107, 107, 0.3) !important;
    }
    div[data-testid="stFileUploaderDropzone"] button:hover,
    div[data-testid="stFileUploader"] button:hover {
        background-color: #E55A52 !important;
        color: #FFFFFF !important;
    }

    /* 4. TABS STYLING */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #E5E7EB;
        padding-bottom: 2px;
        background-color: transparent !important;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #FFFFFF !important;
        color: #4B5563 !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 10px 18px !important;
        min-width: 130px !important;
        white-space: nowrap !important;
        border: 1px solid #E5E7EB !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(255, 107, 107, 0.1) !important;
        color: #FF6B6B !important;
        border-color: rgba(255, 107, 107, 0.3) !important;
    }

    /* 5. CARDS & METRICS */
    .card {
        background-color: #FFFFFF !important;
        border-radius: 16px !important;
        padding: 24px !important;
        margin-bottom: 20px !important;
        border: 1px solid #E5E7EB !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02) !important;
    }
    .badge {
        padding: 6px 14px !important;
        border-radius: 999px !important;
        font-size: 0.7rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        display: inline-block !important;
        margin-bottom: 12px !important;
    }
    .badge-active { background: rgba(16, 185, 129, 0.1) !important; color: #10B981 !important; }
    .badge-expired { background: rgba(239, 68, 68, 0.1) !important; color: #EF4444 !important; }
    .badge-approaching { background: rgba(245, 158, 11, 0.1) !important; color: #F59E0B !important; }
    .badge-important { background: rgba(139, 92, 246, 0.1) !important; color: #8B5CF6 !important; }
    
    /* Standard buttons */
    .stButton>button {
        background: #FF6B6B !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 1.25rem !important;
        font-weight: 600 !important;
    }
    .stButton>button:hover {
        background: #E55A52 !important;
    }

    /* 6. SIDEBAR COLLAPSE BUTTON (Glowing Coral Circle Reopen Button) */
    header[data-testid="stHeader"] {
        background-color: #FCFBF9 !important;
        visibility: visible !important;
        height: auto !important;
        min-height: 0 !important;
        padding: 0 !important;
        border-bottom: 1px solid #E5E7EB !important;
    }
    header[data-testid="stHeader"] > * {
        visibility: hidden !important;
    }
    header[data-testid="stHeader"] button[data-testid="stSidebarCollapseButton"],
    header[data-testid="stHeader"] button[data-testid="stSidebarCollapseButton"] * {
        visibility: visible !important;
        display: flex !important;
        background-color: #FF6B6B !important;
        color: white !important;
        border: none !important;
        border-radius: 50% !important;
        width: 64px !important;
        height: 64px !important;
        box-shadow: 0 0 18px rgba(255, 107, 107, 0.7) !important;
        position: absolute !important;
        left: 10px !important;
        top: 80px !important;
        z-index: 99999 !important;
        transition: all 0.3s ease !important;
    }
    header[data-testid="stHeader"] button[data-testid="stSidebarCollapseButton"] svg {
        stroke: #FFFFFF !important;
        fill: #FFFFFF !important;
        width: 32px !important;
        height: 32px !important;
    }

    /* 7. FORCE DROPDOWN ARROWS & EYE ICONS TO BE DARK CHARCOAL */
    .stSidebar svg {
        stroke: #1F2937 !important;
        fill: #1F2937 !important;
        color: #1F2937 !important;
    }
    .stSidebar .stTextInput button svg,
    .stSidebar input[type="password"] ~ button svg {
        stroke: #1F2937 !important;
        fill: #1F2937 !important;
        color: #1F2937 !important;
        width: 20px !important;
        height: 20px !important;
    }

    /* 8. FIX FOR INVISIBLE WHITE TEXT IN INPUTS (Language dropdown & API inputs) */
    .stSidebar .stSelectbox > div > div,
    .stSidebar .stSelectbox [data-baseweb="select"] span,
    .stSidebar .stSelectbox [role="listbox"] span,
    .stSidebar input,
    .stSidebar select,
    .stSidebar textarea {
        color: #1F2937 !important;
        opacity: 1 !important;
    }

    .stSidebar input::placeholder,
    .stSidebar .stTextInput input::placeholder {
        color: #6B7280 !important;
        opacity: 1 !important;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'pil_image' not in st.session_state: st.session_state.pil_image = None
if 'img_base64' not in st.session_state: st.session_state.img_base64 = None
if 'raw_result' not in st.session_state: st.session_state.raw_result = None
if 'checklist_items' not in st.session_state: st.session_state.checklist_items = []
if 'audio_bytes' not in st.session_state: st.session_state.audio_bytes = None
if 'show_uploader' not in st.session_state: st.session_state.show_uploader = True
if 'audio_generated_for_lang' not in st.session_state: st.session_state.audio_generated_for_lang = None
if 'audio_version' not in st.session_state: st.session_state.audio_version = 0
if 'confirm_delete_id' not in st.session_state: st.session_state.confirm_delete_id = None

# --- HINDI DATE TRANSLATOR ---
def translate_date_to_hindi(date_str):
    if not date_str:
        return L["no_deadline"]
    try:
        d = date.fromisoformat(date_str)
        months_hi = [
            'जनवरी', 'फ़रवरी', 'मार्च', 'अप्रैल', 'मई', 'जून',
            'जुलाई', 'अगस्त', 'सितंबर', 'अक्टूबर', 'नवंबर', 'दिसंबर'
        ]
        return f"{d.day} {months_hi[d.month - 1]} {d.year}"
    except:
        return date_str

# --- PROMPTS & HELPERS ---
def build_prompt(selected_lang):
    if selected_lang == "Hindi":
        return """आप एक विशेषज्ग भाषा अनुवादक और कानूनी विश्लेषक हैं। इस नोटिस का विश्लेषण करें और इसका पूरा विवरण केवल और केवल शुद्ध, स्वाभाविक हिंदी में दें।

सूचना: अगर कोई डेडलाइन नोटिस में स्पष्ट रूप से नहीं दी गई है, तो DEADLINE के लिए "Not specified" लिखें। अन्यथा तिथि को अंग्रेजी में लिखें जैसे "25 October 2026"।

FORMAT:
SUMMARY:
[सारांश]

DEADLINE:
[तिथि अंग्रेजी में जैसे: 25 October 2026]

CHECKLIST:
[चरण 1]
[चरण 2]

NOTE:
[चेतावनी/शुल्क]"""
    else:
        return """Analyze this official notice and extract details. Return STRICTLY in this format:

SUMMARY:
[2-3 sentence summary]

DEADLINE:
[Main deadline date, e.g., 25 October 2026]

CHECKLIST:
[Action steps, each on new line]

NOTE:
[Penalty, fee, or warning]"""

def clean_text_for_tts(text, lang):
    text = re.sub(r'[\#\*\_\~\`\|\<\>]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def get_active_free_vision_models():
    try:
        resp = requests.get("https://openrouter.ai/api/v1/models", timeout=10)
        if resp.status_code == 200:
            data = resp.json().get('data', [])
            free_vision = []
            for m in data:
                mid = m.get('id','')
                pricing = m.get('pricing',{})
                arch = m.get('architecture',{})
                modalities = arch.get('modalities',[])
                is_free = float(pricing.get('prompt','1'))==0.0 and float(pricing.get('completion','1'))==0.0
                supports = 'image' in modalities or 'vision' in mid.lower() or 'vl' in mid.lower() or 'gemini' in mid.lower()
                if is_free and supports:
                    free_vision.append(mid)
            priorities = ["google/gemini-2.0-flash-lite-001:free","google/gemini-2.0-flash-exp:free","google/gemini-flash-1.5:free","qwen/qwen-2.5-vl-72b-instruct:free","meta-llama/llama-3.2-11b-vision-instruct:free","nvidia/nemotron-3.5-super-vl:free"]
            sorted_models = [p for p in priorities if p in free_vision]
            for m in free_vision:
                if m not in sorted_models: sorted_models.append(m)
            return sorted_models
    except: pass
    return ["google/gemini-2.0-flash-lite-001:free","nvidia/nemotron-3.5-super-vl:free"]

def get_available_gemini_models(api_key):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            models = resp.json().get('models',[])
            supported = []
            for m in models:
                name = m.get('name','').replace('models/','')
                methods = m.get('supportedGenerationMethods',[])
                if 'generateContent' in methods and ('flash' in name or 'pro' in name):
                    supported.append(name)
            priorities = ["gemini-2.0-flash","gemini-1.5-flash","gemini-flash"]
            sorted_models = [p for p in priorities if p in supported]
            for m in supported:
                if m not in sorted_models: sorted_models.append(m)
            return sorted_models if sorted_models else ["gemini-2.0-flash","gemini-1.5-flash"]
    except: pass
    return ["gemini-2.0-flash","gemini-1.5-flash"]

# --- CORE ANALYSIS ---
def analyze_notice():
    if st.session_state.pil_image is None:
        st.error(L["upload_first"])
        return

    openrouter_key = st.session_state.get('or_key', None)
    gemini_key = st.session_state.get('gm_key', None)
    if not openrouter_key and not gemini_key:
        st.error(L["api_warning"])
        return

    img_b64 = st.session_state.img_base64
    raw_result = None
    used_model = None

    with st.status(L["analyzing"], expanded=True) as status:
        if openrouter_key:
            status.update(label=L["try_openrouter"])
            headers = {"Authorization": f"Bearer {openrouter_key}", "Content-Type": "application/json"}
            for model in get_active_free_vision_models():
                payload = {"model": model, "max_tokens": 2048,
                           "messages": [{"role":"user","content":[
                               {"type":"text","text":build_prompt(current_lang)},
                               {"type":"image_url","image_url":{"url":f"data:image/jpeg;base64,{img_b64}"}}
                           ]}]}
                try:
                    r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload), timeout=30)
                    if r.status_code == 200:
                        c = r.json()['choices'][0]['message']['content']
                        if c and len(c.strip()) > 10:
                            raw_result = c; used_model = f"OpenRouter ({model})"; break
                except: continue

        if not raw_result and gemini_key:
            status.update(label=L["try_gemini"])
            models = get_available_gemini_models(gemini_key)
            for m in models:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={gemini_key}"
                payload = {"contents":[{"parts":[{"text":build_prompt(current_lang)},{"inline_data":{"mime_type":"image/jpeg","data":img_b64}}]}]}
                try:
                    r = requests.post(url, json=payload, timeout=30)
                    if r.status_code == 200:
                        c = r.json()['candidates'][0]['content']['parts'][0]['text']
                        if c and len(c.strip()) > 10:
                            raw_result = c; used_model = f"Gemini ({m})"; break
                except: continue

        if raw_result:
            status.update(label=L["done_model"].format(model=used_model), state="complete")
        else:
            status.update(label=L["all_fail"], state="error")

    if raw_result:
        st.session_state.raw_result = raw_result

        sm = re.search(r'SUMMARY:\s*(.*?)(?=\nDEADLINE:|\Z)', raw_result, re.DOTALL|re.IGNORECASE)
        dl = re.search(r'DEADLINE:\s*(.*?)(?=\nCHECKLIST:|\Z)', raw_result, re.DOTALL|re.IGNORECASE)
        nt = re.search(r'NOTE:\s*(.*?)(?=\Z)', raw_result, re.DOTALL|re.IGNORECASE)
        cl = re.search(r'CHECKLIST:\s*(.*?)(?=\nNOTE:|\Z)', raw_result, re.DOTALL|re.IGNORECASE)

        summary = sm.group(1).strip() if sm else "No summary."
        deadline_text = dl.group(1).strip() if dl else "Not specified"
        note = nt.group(1).strip() if nt else "None"
        checklist_raw = cl.group(1).strip() if cl else ""

        items = []
        for line in checklist_raw.split('\n'):
            line = line.strip()
            clean = re.sub(r'^[\d\)\.\-\*]+\s*','',line).strip()
            if clean: items.append(clean)
        st.session_state.checklist_items = items

        parsed = db.parse_deadline_date(deadline_text)
        parsed_str = parsed.isoformat() if parsed else None
        saved = db.save_notice(
            title=f"Notice ({date.today().isoformat()})",
            summary=summary,
            deadline_date_str=parsed_str,
            raw_result=raw_result
        )
        if saved:
            st.success(L["save_success"])
        else:
            st.info(L["already_saved"])

        try:
            checklist_text = ". ".join(items)
            if current_lang == "Hindi":
                tts_text = f"{summary}. कार्यवाही चरण: {checklist_text}. टिप्पणी: {note}"
                tts_lang = 'hi'
            else:
                tts_text = f"{summary}. Checklist: {checklist_text}. Note: {note}"
                tts_lang = 'en'
            tts_text = clean_text_for_tts(tts_text, current_lang)
            tts = gTTS(text=tts_text[:5000], lang=tts_lang, slow=False)
            af = "notice_audio.mp3"
            tts.save(af)
            with open(af,'rb') as f: st.session_state.audio_bytes = f.read()
            st.session_state.audio_generated_for_lang = current_lang
            st.session_state.audio_version += 1
        except Exception as e:
            st.error(L["audio_err"].format(e=e))

def render_cards(notices, category_key):
    cat_labels = {
        "available": ("Active / Available", "सक्रिय / उपलब्ध"),
        "expired": ("Expired / Crossed", "समाप्त / समय सीमा पार"),
        "approaching": ("Approaching Soon", "जल्द आने वाला"),
        "important": ("Important", "महत्वपूर्ण"),
    }
    cat_display = cat_labels.get(category_key, ("", ""))[1] if current_lang == "Hindi" else cat_labels.get(category_key, ("", ""))[0]
    
    badge_map = {
        "available":"badge-active","expired":"badge-expired",
        "approaching":"badge-approaching","important":"badge-important"
    }
    
    if not notices:
        st.info(L["no_notices"].format(category=cat_display))
        return
        
    for n in notices:
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            c1, c2 = st.columns([5, 1])
            with c1:
                st.markdown(f"### {n['title'] or 'Untitled'}")
                st.write(n['summary'] or "")
                
                if current_lang == "Hindi":
                    deadline_display = translate_date_to_hindi(n['deadline_date'])
                else:
                    deadline_display = n['deadline_date'] or L["no_deadline"]
                
                st.markdown(f"**📅 {L['deadline_label'].split('/')[0].strip()}:** `{deadline_display}`")
            with c2:
                st.markdown(f'<span class="badge {badge_map.get(category_key,"")}">{cat_display}</span>', unsafe_allow_html=True)
                is_imp = n['is_important'] == 1
                label = L["btn_mark_imp_done"] if is_imp else L["btn_mark_imp"]
                if st.button(label, key=f"imp_{n['notice_id']}_{category_key}"):
                    db.toggle_important(n['notice_id'], n['is_important'])
                    st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.session_state.confirm_delete_id == n['notice_id']:
                st.warning(L["confirm_delete_msg"])
                col_yes, col_cancel = st.columns(2)
                if col_yes.button(L["btn_yes"], key=f"yes_del_{n['notice_id']}_{category_key}", type="primary"):
                    db.delete_notice(n['notice_id'])
                    st.session_state.confirm_delete_id = None
                    st.success("Notice deleted successfully!")
                    st.rerun()
                if col_cancel.button(L["btn_cancel"], key=f"cancel_del_{n['notice_id']}_{category_key}"):
                    st.session_state.confirm_delete_id = None
                    st.rerun()
            else:
                if st.button(L["btn_delete"], key=f"del_{n['notice_id']}_{category_key}", use_container_width=True, type="secondary"):
                    st.session_state.confirm_delete_id = n['notice_id']
                    st.rerun()
                    
            st.markdown('</div>', unsafe_allow_html=True)

# --- SIDEBAR (UPDATED WITH HELPER LINKS) ---
with st.sidebar:
    st.markdown(LOGO_HTML, unsafe_allow_html=True)
    st.markdown("---")
    
    lang_options = ["English", "Hindi"]
    lang_index = 0 if current_lang == "English" else 1
    st.selectbox(L["sidebar_lang"], lang_options, key="lang_sb", index=lang_index)
    
    st.markdown(f"### {L['sidebar_keys']}")
    
    # Inputs with helpful hover text
    st.text_input(
        L["key_openrouter"], 
        type="password", 
        key="or_key", 
        help="Get a free key at openrouter.ai"
    )
    st.text_input(
        L["key_gemini"], 
        type="password", 
        key="gm_key", 
        help="Get a free key at Google AI Studio"
    )
    
    # 🟢 HELPER LINKS SECTION (Crucial for the "Bring Your Own Key" strategy)
    st.markdown(
        """
        <div style="background-color: #FFFFFF; padding: 12px; border-radius: 8px; border: 1px solid #E5E7EB; margin-top: 10px;">
            <p style="font-size: 0.8rem; font-weight: 700; color: #1F2937; margin-bottom: 8px;">
                🟢 Get 100% Free API Keys:
            </p>
            <a href="https://openrouter.ai/keys" target="_blank" style="text-decoration: none; color: #FF6B6B; font-weight: 600; font-size: 0.8rem; display: block; margin-bottom: 6px;">
                ➡️ OpenRouter (Primary)
            </a>
            <a href="https://aistudio.google.com/apikey" target="_blank" style="text-decoration: none; color: #FF6B6B; font-weight: 600; font-size: 0.8rem; display: block;">
                ➡️ Google Gemini (Backup)
            </a>
            <p style="font-size: 0.7rem; color: #6B7280; margin-top: 8px; margin-bottom: 0;">
                *Both tiers are completely free. No credit card required.*
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    st.caption(L["cap_single"])

# --- MAIN TABS ---
tab_labels = [
    L["tab_analyze"],
    L["tab_active"],
    L["tab_approach"],
    L["tab_expired"],
    L["tab_important"],
]
tab_analyze, tab_active, tab_approach, tab_expired, tab_imp = st.tabs(tab_labels)

# ================= TAB 1: ANALYZE =================
with tab_analyze:
    if st.session_state.show_uploader:
        f = st.file_uploader(L["uploader_label"], type=['jpg','png','jpeg','pdf'])
        if f:
            with st.status(L["processing"], expanded=True) as stt:
                try:
                    if f.type == "application/pdf":
                        doc = fitz.open(stream=f.read(), filetype="pdf")
                        pix = doc.load_page(0).get_pixmap()
                        st.session_state.pil_image = Image.frombytes("RGB",[pix.width,pix.height],pix.samples)
                    else:
                        f.seek(0)
                        st.session_state.pil_image = Image.open(f)
                    img = st.session_state.pil_image
                    img.thumbnail((1024,1024))
                    if img.mode in ("RGBA","P"): img = img.convert("RGB")
                    buf = io.BytesIO(); img.save(buf,format="JPEG")
                    st.session_state.img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                    st.session_state.show_uploader = False
                    stt.update(label=L["ready"], state="complete")
                    st.rerun()
                except Exception as e:
                    stt.update(label=f"Error: {e}", state="error")
    else:
        col_prev, col_btn = st.columns([1,1])
        with col_prev:
            if st.session_state.pil_image:
                st.image(st.session_state.pil_image, width=300, caption="Preview")
            if st.button(L["btn_upload_new"], use_container_width=True):
                st.session_state.show_uploader = True
                st.session_state.pil_image = None
                st.session_state.img_base64 = None
                st.session_state.raw_result = None
                st.session_state.checklist_items = []
                st.session_state.audio_bytes = None
                st.rerun()
        with col_btn:
            if not st.session_state.raw_result:
                if st.button(L["btn_analyze"], use_container_width=True, type="primary"):
                    analyze_notice()
                    st.rerun()

    if st.session_state.raw_result:
        raw_result = st.session_state.raw_result
        sm = re.search(r'SUMMARY:\s*(.*?)(?=\nDEADLINE:|\Z)', raw_result, re.DOTALL|re.IGNORECASE)
        dl = re.search(r'DEADLINE:\s*(.*?)(?=\nCHECKLIST:|\Z)', raw_result, re.DOTALL|re.IGNORECASE)
        nt = re.search(r'NOTE:\s*(.*?)(?=\Z)', raw_result, re.DOTALL|re.IGNORECASE)

        summary = sm.group(1).strip() if sm else raw_result[:200]
        deadline = dl.group(1).strip() if dl else "Not specified"
        note = nt.group(1).strip() if nt else "None"

        st.markdown(f"### {L['summary_header']}")
        st.info(summary)
        
        if current_lang == "Hindi":
            deadline_display = translate_date_to_hindi(deadline)
        else:
            deadline_display = deadline
        st.metric(label=L['deadline_header'], value=deadline_display)
        
        st.markdown("---")
        st.markdown(f"### {L['checklist_header']}")

        completed_count = 0
        for idx, task in enumerate(st.session_state.checklist_items):
            key = f"task_{idx}_{len(st.session_state.checklist_items)}"
            if st.checkbox(task, key=key):
                completed_count += 1

        total_tasks = len(st.session_state.checklist_items)
        if total_tasks > 0:
            st.markdown(L['completed_text'].format(done=completed_count, total=total_tasks))
            st.progress(completed_count / total_tasks)

        st.markdown("---")
        st.markdown(f"### {L['note_header']}")
        st.warning(note)

        if st.session_state.audio_bytes and st.session_state.audio_generated_for_lang == current_lang:
            st.markdown(f"#### {L['audio_label']}")
            ab64 = base64.b64encode(st.session_state.audio_bytes).decode()
            aid = f"audio-{current_lang}-{st.session_state.audio_version}"
            ah = f"""
            <audio id="{aid}" controls style="width: 100%;">
                <source src="data:audio/mp3;base64,{ab64}" type="audio/mp3">
            </audio>
            """
            st.components.v1.html(ah, height=80)

# ================= TAB 2: ACTIVE =================
with tab_active:
    st.markdown(f"### {L['tab_active']}")
    active_notices = db.get_active_notices()
    render_cards(active_notices, "available")

# ================= TAB 3: APPROACHING =================
with tab_approach:
    st.markdown(f"### {L['tab_approach']}")
    approaching_notices = db.get_approaching_notices(days_threshold=3)
    render_cards(approaching_notices, "approaching")

# ================= TAB 4: EXPIRED =================
with tab_expired:
    st.markdown(f"### {L['tab_expired']}")
    expired_notices = db.get_expired_notices()
    render_cards(expired_notices, "expired")

# ================= TAB 5: IMPORTANT =================
with tab_imp:
    st.markdown(f"### {L['tab_important']}")
    important_notices = db.get_important_notices()
    render_cards(important_notices, "important")