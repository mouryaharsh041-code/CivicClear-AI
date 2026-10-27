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

import db  # Our Supabase-backed database module

# --- PAGE CONFIG & THEME LOCK ---
st.set_page_config(
    page_title="CivicClear AI | SaralNotice",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

try:
    st.config_set('theme.base', 'light')
except Exception:
    pass

# --- AUTHENTICATION SESSION STATE ---
if "user" not in st.session_state: st.session_state["user"] = None
if "access_token" not in st.session_state: st.session_state["access_token"] = None
if "refresh_token" not in st.session_state: st.session_state["refresh_token"] = None

supabase_client = db.get_base_supabase()

# --- LOGIN / SIGNUP SCREEN GATE ---
if st.session_state["user"] is None:
    st.title("🔐 CivicClear AI - Multi-User Login")
    st.write("Please sign in or create an account to manage your secure notice dashboard.")
    
    auth_tab1, auth_tab2 = st.tabs(["Sign In", "Create Account"])
    
    with auth_tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Sign In", type="primary"):
            try:
                res = supabase_client.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state["user"] = res.user
                st.session_state["access_token"] = res.session.access_token
                st.session_state["refresh_token"] = res.session.refresh_token
                st.success("Successfully logged in!")
                st.rerun()
            except Exception as e:
                st.error(f"Login failed: {e}")

    with auth_tab2:
        new_email = st.text_input("Email", key="signup_email")
        new_pass = st.text_input("Password", type="password", key="signup_pass")
        if st.button("Register Account", type="primary"):
            try:
                supabase_client.auth.sign_up({"email": new_email, "password": new_pass})
                st.success("Registration successful! Check your email to confirm your account, then sign in.")
            except Exception as e:
                st.error(f"Registration failed: {e}")
                
    st.stop()

# =========================================================
# === BILINGUAL UI STRINGS ===
# =========================================================
EN = {
    "title": "CivicClear AI | SaralNotice",
    "sidebar_lang": "Language",
    "sidebar_keys": "🔑 API Keys",
    "key_openrouter": "OpenRouter API Key",
    "key_gemini": "Gemini API Key (Backup)",
    "cap_single": "Multi-user cloud dashboard active.",
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
    "save_success": "✅ Notice saved to your cloud dashboard!",
    "already_saved": "ℹ️ This notice is already saved.",
    "api_warning": "⚠️ Please enter at least one API key in the sidebar.",
    "upload_first": "Please upload an image or PDF first.",
    "analyzing": "Analyzing document...",
    "audio_err": "Audio generation error: {e}",
    "no_deadline": "No deadline mentioned",
    "confirm_delete_msg": "Are you sure you want to delete this notice?",
    "btn_yes": "Yes, Delete",
    "btn_cancel": "Cancel",
    "helper_title": "Get 100% Free API Keys:",
    "helper_openrouter": "OpenRouter (Primary)",
    "helper_gemini": "Google Gemini (Backup)",
    "helper_note": "*Both tiers are completely free.*",
}

HI = {
    "title": "🏛️ सिविक क्लियर एआई | सरल नोटिस",
    "sidebar_lang": "भाषा",
    "sidebar_keys": "🔑 एपीआई कुंजियाँ",
    "key_openrouter": "ओपनराउटर एपीआई कुंजी",
    "key_gemini": "जेमिनी एपीआई कुंजी (बैकअप)",
    "cap_single": "मल्टी-यूज़र क्लाउड डैशबोर्ड सक्रिय।",
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
    "save_success": "✅ नोटिस आपके क्लाउड डैशबोर्ड पर सहेजा गया!",
    "already_saved": "ℹ️ यह नोटिस पहले से सहेजा गया है।",
    "api_warning": "⚠️ कृपया साइडबार में कम से कम एक एपीआई कुंजी दर्ज करें।",
    "upload_first": "कृपया पहले एक चित्र या पीडीएफ अपलोड करें।",
    "analyzing": "दस्तावेज़ का विश्लेषण हो रहा है...",
    "audio_err": "ऑडियो जनरेशन त्रुटि: {e}",
    "no_deadline": "कोई अंतिम तिथि नहीं",
    "confirm_delete_msg": "क्या आप वाकई इस नोटिस को हटाना चाहते हैं?",
    "btn_yes": "हाँ, हटाएँ",
    "btn_cancel": "रद्द करें",
    "helper_title": "100% निःशुल्क एपीआई कुंजियाँ प्राप्त करें:",
    "helper_openrouter": "ओपनराउटर (प्राथमिक)",
    "helper_gemini": "गूगल जेमिनी (बैकअप)",
    "helper_note": "*दोनों स्तर पूरी तरह निःशुल्क हैं।*",
}

# =========================================================
# === LANGUAGE SYNC ===
# =========================================================
if "lang_sb" in st.session_state:
    st.session_state.current_lang = st.session_state["lang_sb"]
current_lang = st.session_state.get("current_lang", "English")
L = HI if current_lang == "Hindi" else EN

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

def get_best_openrouter_model(api_key, supports_image=False):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
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
                    if supports_image and not supports_img: continue
                    candidates.append(mid)
            priorities = ["google/gemini-2.0-flash-lite-001:free", "google/gemini-flash-1.5:free", "meta-llama/llama-3.2-11b-vision-instruct:free"]
            for p in priorities:
                if p in candidates: return p
            if candidates: return candidates[0]
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
    best_model = get_best_openrouter_model(api_key, supports_image=supports_image)
    models_to_try = [best_model, "google/gemini-2.0-flash-lite-001:free", "google/gemini-flash-1.5:free"]
    
    for model in models_to_try:
        if not model: continue
        try:
            payload = {"model": model, "max_tokens": max_tokens, "messages": messages}
            r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload), timeout=15)
            if r.status_code == 200:
                res_data = r.json()
                if 'choices' in res_data and len(res_data['choices']) > 0:
                    content = res_data['choices'][0]['message']['content']
                    if content and len(content.strip()) > 5:
                        return content, model
        except Exception:
            continue
    return None, None

def build_ocr_prompt():
    return "Extract ALL text from this document exactly as it is written. Preserve paragraph breaks."

def build_structured_extraction_prompt(raw_text):
    return f"""From the following raw text of a government notice, extract the following fields:
1. SUMMARY: A 2-3 sentence summary.
2. DEADLINE: Main deadline in YYYY-MM-DD format if possible.
3. CHECKLIST: Every single action step as a numbered list.
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

NOTE:
[penalty/warning]"""

def build_translation_prompt(en_structured_text):
    return f"""Translate the structured notice details from English into formal Hindi. Keep headers SUMMARY:, DEADLINE:, CHECKLIST:, NOTE: exactly in English. Translate content underneath into fluent formal Hindi. Maintain numbered lists.

English Text:
{en_structured_text}"""

def clean_text_for_tts(text, lang):
    return re.sub(r'[\#\*\_\~\`\|\<\>]', ' ', text).strip()

def get_available_gemini_models(api_key):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            models = resp.json().get('models', [])
            supported = [m.get('name','').replace('models/','') for m in models if 'generateContent' in m.get('supportedGenerationMethods',[])]
            return [m for m in ["gemini-2.0-flash", "gemini-1.5-flash"] if m in supported] or ["gemini-2.0-flash"]
    except Exception:
        pass
    return ["gemini-2.0-flash"]

# --- CORE ANALYSIS PIPELINE ---
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

    with st.status(L["analyzing"], expanded=True) as status:
        status.update(label="Extracting raw text from document...")
        if openrouter_key:
            content_payload = [{"type": "text", "text": build_ocr_prompt()}]
            if st.session_state.pdf_text:
                content_payload[0]["text"] = f"Extract all text from this PDF:\n\n{st.session_state.pdf_text}"
            else:
                content_payload.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}})
            raw_text, _ = call_openrouter_with_retry(openrouter_key, [{"role":"user","content": content_payload}], max_tokens=4096, supports_image=True)

        if not raw_text and gemini_key:
            for m in get_available_gemini_models(gemini_key):
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={gemini_key}"
                content_parts = [{"text": build_ocr_prompt()}]
                if st.session_state.pdf_text:
                    content_parts.insert(0, {"text": f"Extract all text from this PDF:\n\n{st.session_state.pdf_text}"})
                else:
                    content_parts.append({"inline_data": {"mime_type": "image/jpeg", "data": img_b64}})
                try:
                    r = requests.post(url, json={"contents":[{"parts": content_parts}]}, timeout=15)
                    if r.status_code == 200:
                        raw_text = r.json()['candidates'][0]['content']['parts'][0]['text']
                        break
                except Exception:
                    pass

        if not raw_text:
            status.update(label="Failed to extract text.", state="error")
            st.error("❌ OCR Extraction Failed: Check API keys and network connection.")
            return

    en_structured = None
    with st.status("Extracting structured fields...", expanded=True) as status:
        if openrouter_key:
            en_structured, _ = call_openrouter_with_retry(openrouter_key, [{"role":"user","content": build_structured_extraction_prompt(raw_text)}], max_tokens=2048, supports_image=False)
        if not en_structured and gemini_key:
            for m in get_available_gemini_models(gemini_key):
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={gemini_key}"
                try:
                    r = requests.post(url, json={"contents":[{"parts":[{"text": build_structured_extraction_prompt(raw_text)}]}]}, timeout=15)
                    if r.status_code == 200:
                        en_structured = r.json()['candidates'][0]['content']['parts'][0]['text']
                        break
                except Exception:
                    pass
        if not en_structured:
            status.update(label="Structuring failed.", state="error")
            return

    final_result = en_structured
    if en_structured and current_lang == "Hindi":
        with st.status("Translating to Hindi...", expanded=True) as trans_status:
            if openrouter_key:
                final_result, _ = call_openrouter_with_retry(openrouter_key, [{"role":"user","content": build_translation_prompt(en_structured)}], max_tokens=2048, supports_image=False)

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
                if clean: items.append(clean)
            elif line and not re.match(r'^(CHECKLIST|कार्यवाही चरण|NOTE|महत्वपूर्ण टिप्पणी|टिप्पणी|SUMMARY|सारांश|DEADLINE|अंतिम तिथि)', line, re.IGNORECASE):
                items.append(line)

        st.session_state.checklist_items = items
        parsed = db.parse_deadline_date(deadline_text)
        db.save_notice(
            title=f"Notice ({date.today().isoformat()})",
            summary=summary,
            deadline_date_str=parsed.isoformat() if parsed else None,
            raw_result=en_structured
        )
        st.success(L["save_success"])

        try:
            checklist_text = ". ".join(items)
            tts_text = f"{summary}. कार्यवाही चरण: {checklist_text}. टिप्पणी: {note}" if current_lang == "Hindi" else f"{summary}. Checklist: {checklist_text}. Note: {note}"
            tts = gTTS(text=clean_text_for_tts(tts_text, current_lang)[:5000], lang='hi' if current_lang == "Hindi" else 'en', slow=False)
            tts.save("notice_audio.mp3")
            with open("notice_audio.mp3", 'rb') as f: st.session_state.audio_bytes = f.read()
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
    badge_map = {"available":"badge-active","expired":"badge-expired","approaching":"badge-approaching","important":"badge-important"}
    
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
                deadline_display = translate_date_to_hindi(n['deadline_date']) if current_lang == "Hindi" else (n['deadline_date'] or L["no_deadline"])
                st.markdown(f"**📅 Deadline:** `{deadline_display}`")
            with c2:
                st.markdown(f'<span class="badge {badge_map.get(category_key,"")}">{cat_display}</span>', unsafe_allow_html=True)
                is_imp = n['is_important'] == 1
                if st.button(L["btn_mark_imp_done"] if is_imp else L["btn_mark_imp"], key=f"imp_{n['notice_id']}_{category_key}"):
                    db.toggle_important(n['notice_id'], n['is_important'])
                    st.rerun()
            
            if st.button(L["btn_delete"], key=f"del_{n['notice_id']}_{category_key}", use_container_width=True, type="secondary"):
                db.delete_notice(n['notice_id'])
                st.success("Notice deleted!")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# --- SIDEBAR AUTH & CONTROLS ---
with st.sidebar:
    st.markdown(LOGO_HTML, unsafe_allow_html=True)
    st.markdown(f"**Logged in as:** `{st.session_state['user'].email}`")
    if st.button("🚪 Sign Out"):
        supabase_client.auth.sign_out()
        st.session_state["user"] = None
        st.session_state["access_token"] = None
        st.session_state["refresh_token"] = None
        st.rerun()
        
    st.markdown("---")
    st.selectbox(L["sidebar_lang"], ["English", "Hindi"], key="lang_sb", index=0 if current_lang == "English" else 1)
    
    st.markdown(f"### {L['sidebar_keys']}")
    st.text_input(L["key_openrouter"], type="password", key="or_key")
    st.text_input(L["key_gemini"], type="password", key="gm_key")
    st.markdown("---")
    st.caption(L["cap_single"])

# --- MAIN TABS ---
tab_analyze, tab_active, tab_approach, tab_expired, tab_imp = st.tabs([
    L["tab_analyze"], L["tab_active"], L["tab_approach"], L["tab_expired"], L["tab_important"]
])

with tab_analyze:
    if st.session_state.previous_lang != current_lang:
        st.session_state.previous_lang = current_lang
        if st.session_state.pil_image or st.session_state.pdf_text:
            analyze_notice()
            st.rerun()

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
                            st.session_state.pil_image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                            st.session_state.pdf_text = None
                        except Exception:
                            from pypdf import PdfReader
                            f.seek(0)
                            reader = PdfReader(f)
                            st.session_state.pil_image = None
                            st.session_state.pdf_text = "".join([p.extract_text() or "" for p in reader.pages])
                    else:
                        f.seek(0)
                        st.session_state.pil_image = Image.open(f)
                        st.session_state.pdf_text = None

                    if st.session_state.pil_image:
                        img = st.session_state.pil_image
                        img.thumbnail((512, 512))
                        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                        buf = io.BytesIO(); img.save(buf, format="JPEG")
                        st.session_state.img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

                    st.session_state.show_uploader = False
                    st.rerun()
                except Exception as e:
                    stt.update(label=f"Error: {e}", state="error")
    else:
        col_prev, col_btn = st.columns([1, 1])
        with col_prev:
            if st.session_state.pil_image:
                st.image(st.session_state.pil_image, width=300, caption="Preview")
            if st.button(L["btn_upload_new"], use_container_width=True):
                st.session_state.update(show_uploader=True, pil_image=None, img_base64=None, raw_result=None, checklist_items=[], audio_bytes=None, pdf_text=None)
                st.rerun()
        with col_btn:
            if st.button(L["btn_analyze"] if not st.session_state.raw_result else L["btn_analyze"] + " (Re-analyze)", use_container_width=True, type="primary"):
                analyze_notice()
                st.rerun()

    if st.session_state.raw_result:
        raw_result = st.session_state.raw_result
        sm = re.search(r'(?:SUMMARY|सारांश):\s*(.*?)(?=\n(?:DEADLINE|अंतिम तिथि|CHECKLIST|कार्यवाही चरण):|\Z)', raw_result, re.DOTALL|re.IGNORECASE)
        dl = re.search(r'(?:DEADLINE|अंतिम तिथि):\s*(.*?)(?=\n(?:CHECKLIST|कार्यवाही चरण|NOTE|टिप्पणी):|\Z)', raw_result, re.DOTALL|re.IGNORECASE)
        nt = re.search(r'(?:NOTE|महत्वपूर्ण टिप्पणी|टिप्पणी):\s*(.*?)(?=\Z)', raw_result, re.DOTALL|re.IGNORECASE)

        st.markdown(f"### {L['summary_header']}")
        st.info(sm.group(1).strip() if sm else raw_result[:300])
        st.metric(label=L['deadline_header'], value=translate_date_to_hindi(dl.group(1).strip()) if current_lang == "Hindi" else (dl.group(1).strip() if dl else "Not specified"))
        
        st.markdown("---")
        st.markdown(f"### {L['checklist_header']}")
        completed_count = sum([1 for idx, task in enumerate(st.session_state.checklist_items) if st.checkbox(task, key=f"task_{idx}")])
        if st.session_state.checklist_items:
            st.markdown(L['completed_text'].format(done=completed_count, total=len(st.session_state.checklist_items)))
            st.progress(completed_count / len(st.session_state.checklist_items))

        st.markdown("---")
        st.markdown(f"### {L['note_header']}")
        st.warning(nt.group(1).strip() if nt else "No specific warnings noted.")

        if st.session_state.audio_bytes and st.session_state.audio_generated_for_lang == current_lang:
            st.markdown(f"#### {L['audio_label']}")
            ab64 = base64.b64encode(st.session_state.audio_bytes).decode()
            st.components.v1.html(f'<audio controls style="width: 100%;"><source src="data:audio/mp3;base64,{ab64}" type="audio/mp3"></audio>', height=80)

with tab_active:
    st.markdown(f"### {L['tab_active']}")
    render_cards(db.get_active_notices(), "available")

with tab_approach:
    st.markdown(f"### {L['tab_approach']}")
    render_cards(db.get_approaching_notices(), "approaching")

with tab_expired:
    st.markdown(f"### {L['tab_expired']}")
    render_cards(db.get_expired_notices(), "expired")

with tab_imp:
    st.markdown(f"### {L['tab_important']}")
    render_cards(db.get_important_notices(), "important")
