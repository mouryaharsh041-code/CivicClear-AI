import streamlit as st
import base64
import re
import io
import json
import os
from PIL import Image
from gtts import gTTS
import requests
from datetime import date

import db  # Our database module

# --- PAGE CONFIG & THEME LOCK ---
st.set_page_config(
    page_title="CivicClear AI | SaralNotice",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Programmatically lock the base theme to light
try:
    st.config_set('theme.base', 'light')
except Exception:
    pass

# =========================================================
# === BILINGUAL UI STRINGS (PURE SINGLE-LANGUAGE HEADINGS) ===
# =========================================================
EN = {
    "title": "CivicClear AI | SaralNotice",
    "subtitle": "Actionable Clarity for Everyone",
    "sidebar_lang": "Language",
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
    "result_header": "Result",
    "summary_header": "Summary",
    "deadline_header": "Deadline",
    "note_header": "Important Note",
    "checklist_header": "Action Steps",
    "completed_text": "**{done} of {total} tasks completed**",
    "audio_label": "🎧 Listen to Audio",
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
    "helper_title": "Get 100% Free API Keys:",
    "helper_openrouter": "OpenRouter (Primary)",
    "helper_gemini": "Google Gemini (Backup)",
    "helper_note": "*Both tiers are completely free. No credit card required.*",
}

HI = {
    "title": "🏛️ सिविक क्लियर एआई | सरल नोटिस",
    "subtitle": "सभी के लिए कार्रवाई योग्य स्पष्टता",
    "sidebar_lang": "भाषा",
    "sidebar_keys": "🔑 एपीआई कुंजियाँ",
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
    "result_header": "परिणाम",
    "summary_header": "सारांश",
    "deadline_header": "अंतिम तिथि",
    "note_header": "महत्वपूर्ण टिप्पणी",
    "checklist_header": "कार्यवाही चरण",
    "completed_text": "**{total} में से {done} कार्य पूर्ण हुए**",
    "audio_label": "🎧 ऑडियो सुनें",
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
    "helper_title": "100% निःशुल्क एपीआई कुंजियाँ प्राप्त करें:",
    "helper_openrouter": "ओपनराउटर (प्राथमिक)",
    "helper_gemini": "गूगल जेमिनी (बैकअप)",
    "helper_note": "*दोनों स्तर पूरी तरह निःशुल्क हैं। क्रेडिट कार्ड की आवश्यकता नहीं है।*",
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

# --- PREMIUM CSS ---
st.markdown("""
    <style>
    html, body, [data-testid="stApp"], [data-testid="stHeader"], .stSidebar {
        background-color: #FCFBF9 !important;
        color: #1F2937 !important;
    }
    h1, h2, h3, h4, h5, h6, span, p, label, div {
        color: #1F2937 !important;
    }
    .stSidebar {
        background-color: #F4EFE6 !important;
        color: #1F2937 !important;
        border-right: 1px solid #E5E7EB !important;
    }
    .card {
        background-color: #FFFFFF !important;
        border-radius: 16px !important;
        padding: 24px !important;
        margin-bottom: 20px !important;
        border: 1px solid #E5E7EB !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12) !important;
    }
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
    .stThemeToggle, div[data-testid="stThemeToggle"] {
        display: none !important;
    }
    div[role="menu"] > div:first-child {
        display: none !important;
    }
    div[role="menu"] > hr:first-of-type {
        display: none !important;
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
if 'pdf_text' not in st.session_state: st.session_state.pdf_text = None
if 'previous_lang' not in st.session_state: st.session_state.previous_lang = None

# --- HINDI DATE TRANSLATOR ---
def translate_date_to_hindi(date_str):
    if not date_str or date_str.lower() == "not specified":
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

# =========================================================
# === MODEL & PROMPT HELPERS ===
# =========================================================
def get_best_openrouter_model(api_key, supports_image=False):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    try:
        resp = requests.get("https://openrouter.ai/api/v1/models", headers=headers, timeout=10)
        if resp.status_code == 200:
            models = resp.json().get('data', [])
            candidates = []
            for m in models:
                mid = m.get('id', '')
                pricing = m.get('pricing', {})
                is_free = float(pricing.get('prompt', 1)) == 0.0 and float(pricing.get('completion', 1)) == 0.0
                arch = m.get('architecture', {})
                modalities = arch.get('modalities', [])
                supports_img = 'image' in modalities or 'vision' in mid.lower() or 'vl' in mid.lower() or 'gemini' in mid.lower()
                
                if is_free:
                    if supports_image and not supports_img:
                        continue
                    candidates.append(mid)
            
            priorities = [
                "google/gemini-2.0-flash-lite-001:free",
                "google/gemini-2.0-flash-exp:free",
                "google/gemini-flash-1.5:free",
                "qwen/qwen-2.5-vl-72b-instruct:free",
                "nvidia/nemotron-3.5-super-vl:free",
                "meta-llama/llama-3.2-11b-vision-instruct:free",
            ]
            for p in priorities:
                if p in candidates:
                    return p
            if candidates:
                return candidates[0]
    except Exception:
        pass
    return "google/gemini-2.0-flash-lite-001:free" if supports_image else "meta-llama/llama-3.2-11b-vision-instruct:free"

def call_openrouter_with_retry(api_key, messages, max_tokens=2048, supports_image=False):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://civicclear-ai.streamlit.app",
        "X-Title": "CivicClear AI"
    }
    
    # Get the best model dynamically
    best_model = get_best_openrouter_model(api_key, supports_image=supports_image)
    
    # Create a list of models to try: dynamic best first, then fallbacks
    fallbacks = [
        "google/gemini-2.0-flash-lite-001:free",
        "google/gemini-flash-1.5:free",
        "qwen/qwen-2.5-72b-instruct:free",
        "meta-llama/llama-3.2-11b-vision-instruct:free"
    ]
    
    models_to_try = [best_model] if best_model else []
    for m in fallbacks:
        if m not in models_to_try:
            models_to_try.append(m)
            
    for model in models_to_try:
        try:
            payload = {
                "model": model, 
                "max_tokens": max_tokens,
                "messages": messages
            }
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions", 
                headers=headers, 
                data=json.dumps(payload), 
                timeout=15  # Fast timeout to skip decommissioned models quickly
            )
            
            if r.status_code == 200:
                res_data = r.json()
                if 'choices' in res_data and len(res_data['choices']) > 0:
                    content = res_data['choices'][0]['message']['content']
                    if content and len(content.strip()) > 5:
                        return content, model
            # If status code is not 200 (e.g. 404 model decommissioned), try next model silently
        except Exception as e:
            # Connection error or timeout, try next model silently
            continue
            
    return None, None

def build_ocr_prompt():
    return """Extract ALL text from this document exactly as it is written. 
Preserve paragraph breaks. Do not summarize, translate, or omit any text."""

def build_structured_extraction_prompt(raw_text):
    return f"""From the following raw text of a government notice, extract the following fields:

1. SUMMARY: A 2-3 sentence summary of the notice.
2. DEADLINE: The main deadline date in YYYY-MM-DD format if possible, or standard format (e.g., "2026-11-15"). If multiple dates exist, extract the final deadline.
3. CHECKLIST: Extract EVERY single action step as a numbered list. Do not merge steps.
4. NOTE: Any penalty, fee, or warning.

RAW TEXT:
{raw_text}

Return STRICTLY in this format:
SUMMARY:
[summary]

DEADLINE:
[date]

CHECKLIST:
1. [step 1]
2. [step 2]
...

NOTE:
[penalty/warning]"""

def build_translation_prompt(en_structured_text):
    return f"""Translate the following structured notice details from English into formal Hindi. 
Translate BOTH the section headers and the content under them into formal Hindi matching these exact keys:
- SUMMARY: -> SUMMARY:
- DEADLINE: -> DEADLINE:
- CHECKLIST: -> CHECKLIST:
- NOTE: -> NOTE:

(Keep the header labels in English keyword format "SUMMARY:", "DEADLINE:", "CHECKLIST:", "NOTE:" so they can be parsed, but translate everything else including section descriptions completely into fluent formal Hindi).
- DO NOT MERGE OR REORDER THE CHECKLIST ITEMS. Translate each numbered item exactly as written, keeping the exact same numbering (1, 2, 3...).

English Text:
{en_structured_text}
"""

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

# =========================================================
# === CORE ANALYSIS PIPELINE (WITH SILENT RETRIES & SAFE PARSING) ===
# =========================================================
def analyze_notice():
    if st.session_state.pil_image is None and st.session_state.pdf_text is None:
        st.error(L["upload_first"])
        return

    openrouter_key = st.session_state.get('or_key', None)
    gemini_key = st.session_state.get('gm_key', None)
    if not openrouter_key and not gemini_key:
        st.error(L["api_warning"])
        return

    img_b64 = st.session_state.img_base64
    raw_text = None
    used_model = None

    # Step 1: Extract raw text
    with st.status(L["analyzing"], expanded=True) as status:
        status.update(label="Extracting raw text from document...")
        
        if openrouter_key:
            content_payload = [{"type": "text", "text": build_ocr_prompt()}]
            if st.session_state.pdf_text:
                content_payload[0]["text"] = f"Extract all text from this PDF:\n\n{st.session_state.pdf_text}"
            else:
                content_payload.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}})
            
            raw_text, used_model = call_openrouter_with_retry(
                openrouter_key, 
                [{"role":"user","content": content_payload}], 
                max_tokens=4096, 
                supports_image=True
            )

        if not raw_text and gemini_key:
            models = get_available_gemini_models(gemini_key)
            for m in models:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={gemini_key}"
                content_parts = [{"text": build_ocr_prompt()}]
                if st.session_state.pdf_text:
                    content_parts.insert(0, {"text": f"Extract all text from this PDF:\n\n{st.session_state.pdf_text}"})
                else:
                    content_parts.append({"inline_data": {"mime_type": "image/jpeg", "data": img_b64}})
                payload = {"contents":[{"parts": content_parts}]}
                try:
                    r = requests.post(url, json=payload, timeout=15)
                    if r.status_code == 200:
                        res_json = r.json()
                        if 'candidates' in res_json and len(res_json['candidates']) > 0:
                            c = res_json['candidates'][0]['content']['parts'][0]['text']
                            if c and len(c.strip()) > 10:
                                raw_text = c
                                used_model = f"Gemini ({m})"
                                break
                except Exception as e:
                    pass

        if raw_text:
            status.update(label=f"Text extraction complete via {used_model}", state="complete")
        else:
            status.update(label="Failed to extract text from document.", state="error")
            st.error("❌ **OCR Extraction Failed:** Please verify that your API keys are correct, have active quota, and that your connection is stable.")
            return

    # Step 2: Extract structured fields in English (With Safe JSON Parsing & Silent Retries)
    en_structured = None
    model_used = None
    with st.status("Extracting structured fields...", expanded=True) as status:
        if openrouter_key:
            en_structured, model_used = call_openrouter_with_retry(
                openrouter_key, 
                [{"role":"user","content": build_structured_extraction_prompt(raw_text)}], 
                max_tokens=2048, 
                supports_image=False
            )
        
        if not en_structured and gemini_key:
            models = get_available_gemini_models(gemini_key)
            for m in models:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={gemini_key}"
                payload = {"contents":[{"parts":[{"text": build_structured_extraction_prompt(raw_text)}]}]}
                try:
                    r = requests.post(url, json=payload, timeout=15)
                    if r.status_code == 200:
                        res_data = r.json()
                        if 'candidates' in res_data and len(res_data['candidates']) > 0:
                            en_structured = res_data['candidates'][0]['content']['parts'][0]['text']
                            model_used = f"Gemini ({m})"
                            break
                except Exception as e:
                    pass

        if en_structured:
            status.update(label=f"Structured extraction complete via {model_used}", state="complete")
        else:
            status.update(label="Failed to extract structured fields.", state="error")
            st.error("❌ **Structuring Failed:** The AI model could not structure the extracted text fields.")
            return

    # Step 3: Translate to Hindi if selected (With Safe JSON Parsing)
    final_result = en_structured
    if en_structured and current_lang == "Hindi":
        with st.status("Translating to Hindi...", expanded=True) as trans_status:
            translated = False
            model_used_trans = None
            
            if openrouter_key:
                final_result, model_used_trans = call_openrouter_with_retry(
                    openrouter_key, 
                    [{"role":"user","content": build_translation_prompt(en_structured)}], 
                    max_tokens=2048, 
                    supports_image=False
                )
                if final_result:
                    translated = True
            
            if not translated and gemini_key:
                try:
                    models = get_available_gemini_models(gemini_key)
                    for m in models:
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={gemini_key}"
                        payload = {"contents":[{"parts":[{"text": build_translation_prompt(en_structured)}]}]}
                        r = requests.post(url, json=payload, timeout=15)
                        if r.status_code == 200:
                            res_data = r.json()
                            if 'candidates' in res_data and len(res_data['candidates']) > 0:
                                final_result = res_data['candidates'][0]['content']['parts'][0]['text']
                                model_used_trans = f"Gemini ({m})"
                                translated = True
                                break
                except Exception as e:
                    pass

            if translated:
                trans_status.update(label=f"Translation complete via {model_used_trans}!", state="complete")
            else:
                trans_status.update(label="Translation failed. Showing English fallback.", state="error")

    # Step 4: Parse structured result & save to DB
    if final_result:
        st.session_state.raw_result = final_result

        sm = re.search(r'(?:SUMMARY|सारांश):\s*(.*?)(?=\n(?:DEADLINE|अंतिम तिथि|CHECKLIST|कार्यवाही चरण):|\Z)', final_result, re.DOTALL|re.IGNORECASE)
        dl = re.search(r'(?:DEADLINE|अंतिम तिथि):\s*(.*?)(?=\n(?:CHECKLIST|कार्यवाही चरण|NOTE|टिप्पणी):|\Z)', final_result, re.DOTALL|re.IGNORECASE)
        nt = re.search(r'(?:NOTE|महत्वपूर्ण टिप्पणी|टिप्पणी):\s*(.*?)(?=\Z)', final_result, re.DOTALL|re.IGNORECASE)
        cl = re.search(r'(?:CHECKLIST|कार्यवाही चरण):\s*(.*?)(?=\n(?:NOTE|महत्वपूर्ण टिप्पणी|टिप्पणी|SUMMARY|सारांश|DEADLINE|अंतिम तिथि):|\Z)', final_result, re.DOTALL|re.IGNORECASE)

        summary = sm.group(1).strip() if sm else "No summary available."
        deadline_text = dl.group(1).strip() if dl else "Not specified"
        note = nt.group(1).strip() if nt else "None"
        checklist_raw = cl.group(1).strip() if cl else ""

        items = []
        for line in checklist_raw.split('\n'):
            line = line.strip()
            match = re.match(r'^\s*(?:\d+[\)\.]|\*|\-)\s+(.*)', line)
            if match:
                clean = match.group(1).strip()
                if clean:
                    items.append(clean)
            elif line and not re.match(r'^(CHECKLIST|कार्यवाही चरण|NOTE|महत्वपूर्ण टिप्पणी|टिप्पणी|SUMMARY|सारांश|DEADLINE|अंतिम तिथि)', line, re.IGNORECASE):
                items.append(line)

        st.session_state.checklist_items = items

        parsed = db.parse_deadline_date(deadline_text)
        parsed_str = parsed.isoformat() if parsed else None
        db.save_notice(
            title=f"Notice ({date.today().isoformat()})",
            summary=summary,
            deadline_date_str=parsed_str,
            raw_result=en_structured
        )

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
                
                st.markdown(f"**📅 {L['deadline_header']}:** `{deadline_display}`")
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

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(LOGO_HTML, unsafe_allow_html=True)
    st.markdown("---")
    
    lang_options = ["English", "Hindi"]
    lang_index = 0 if current_lang == "English" else 1
    st.selectbox(L["sidebar_lang"], lang_options, key="lang_sb", index=lang_index)
    
    st.markdown(f"### {L['sidebar_keys']}")
    
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
    
    st.markdown(
        f"""
        <div style="background-color: #FFFFFF; padding: 12px; border-radius: 8px; border: 1px solid #E5E7EB; margin-top: 10px;">
            <p style="font-size: 0.8rem; font-weight: 700; color: #1F2937; margin-bottom: 8px;">
                🟢 {L['helper_title']}
            </p>
            <a href="https://openrouter.ai/keys" target="_blank" style="text-decoration: none; color: #FF6B6B; font-weight: 600; font-size: 0.8rem; display: block; margin-bottom: 6px;">
                ➡️ {L['helper_openrouter']}
            </a>
            <a href="https://aistudio.google.com/apikey" target="_blank" style="text-decoration: none; color: #FF6B6B; font-weight: 600; font-size: 0.8rem; display: block;">
                ➡️ {L['helper_gemini']}
            </a>
            <p style="font-size: 0.7rem; color: #6B7280; margin-top: 8px; margin-bottom: 0;">
                {L['helper_note']}
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
    if st.session_state.previous_lang != current_lang:
        if st.session_state.pil_image is not None or st.session_state.pdf_text is not None:
            st.session_state.previous_lang = current_lang
            analyze_notice()
            st.rerun()
        else:
            st.session_state.previous_lang = current_lang

    if st.session_state.show_uploader:
        f = st.file_uploader(L["uploader_label"], type=['jpg', 'png', 'jpeg', 'pdf'])
        if f:
            with st.status(L["processing"], expanded=True) as stt:
                try:
                    if f.type == "application/pdf":
                        try:
                            import fitz
                            doc = fitz.open(stream=f.read(), filetype="pdf")
                            pix = doc.load_page(0).get_pixmap()
                            st.session_state.pil_image = Image.frombytes("RGB",[pix.width,pix.height],pix.samples)
                            st.session_state.pdf_text = None
                            stt.update(label="PDF processed via PyMuPDF (Image)", state="complete")
                        except Exception:
                            from pypdf import PdfReader
                            f.seek(0)
                            reader = PdfReader(f)
                            text = ""
                            for page in reader.pages:
                                text += page.extract_text() or ""
                            
                            st.session_state.pil_image = None
                            st.session_state.pdf_text = text
                            stt.update(label="PDF processed via pypdf (Text fallback)", state="complete")
                    else:
                        f.seek(0)
                        st.session_state.pil_image = Image.open(f)
                        st.session_state.pdf_text = None
                        stt.update(label=L["ready"], state="complete")
                    
                    if st.session_state.pil_image:
                        img = st.session_state.pil_image
                        img.thumbnail((512,512))  # OPTIMIZED: Reduced resolution for faster upload
                        if img.mode in ("RGBA","P"): img = img.convert("RGB")
                        buf = io.BytesIO(); img.save(buf,format="JPEG")
                        st.session_state.img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                    
                    st.session_state.show_uploader = False
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
                st.session_state.pdf_text = None
                st.rerun()
        with col_btn:
            btn_label = L["btn_analyze"] if not st.session_state.raw_result else L["btn_analyze"] + " (Re-analyze)"
            if st.button(btn_label, use_container_width=True, type="primary"):
                analyze_notice()
                st.rerun()

    if st.session_state.raw_result:
        raw_result = st.session_state.raw_result
        
        sm = re.search(r'(?:SUMMARY|सारांश):\s*(.*?)(?=\n(?:DEADLINE|अंतिम तिथि|CHECKLIST|कार्यवाही चरण):|\Z)', raw_result, re.DOTALL|re.IGNORECASE)
        dl = re.search(r'(?:DEADLINE|अंतिम तिथि):\s*(.*?)(?=\n(?:CHECKLIST|कार्यवाही चरण|NOTE|टिप्पणी):|\Z)', raw_result, re.DOTALL|re.IGNORECASE)
        nt = re.search(r'(?:NOTE|महत्वपूर्ण टिप्पणी|टिप्पणी):\s*(.*?)(?=\Z)', raw_result, re.DOTALL|re.IGNORECASE)

        summary = sm.group(1).strip() if sm else raw_result[:300]
        deadline = dl.group(1).strip() if dl else "Not specified"
        note = nt.group(1).strip() if nt else "No specific warnings noted."

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
