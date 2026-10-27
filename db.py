import streamlit as st
from supabase import create_client, Client
from datetime import date, datetime

@st.cache_resource
def get_base_supabase() -> Client:
    url = st.secrets["SUPABASE"]["SUPABASE_URL"]
    key = st.secrets["SUPABASE"]["SUPABASE_KEY"]
    return create_client(url, key)

_supabase = get_base_supabase()

def get_supabase_client() -> Client:
    """Injects the active session token for Row Level Security (RLS)."""
    if st.session_state.get("access_token"):
        try:
            _supabase.auth.set_session(
                st.session_state["access_token"], 
                st.session_state.get("refresh_token", "")
            )
        except Exception:
            pass
    return _supabase

def parse_deadline_date(date_str):
    if not date_str or date_str.lower() == "not specified":
        return None
    try:
        for fmt in ("%Y-%m-%d", "%d %B %Y", "%d %b %Y", "%B %d, %Y"):
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except ValueError:
                continue
        return None
    except Exception:
        return None

def save_notice(title, summary, deadline_date_str, raw_result):
    client = get_supabase_client()
    user = st.session_state.get("user")
    if not user:
        return False

    status = "active"
    if deadline_date_str:
        try:
            d_date = date.fromisoformat(deadline_date_str)
            today = date.today()
            delta = (d_date - today).days
            if delta < 0:
                status = "expired"
            elif delta <= 3:
                status = "approaching"
            else:
                status = "active"
        except Exception:
            status = "active"

    # Check for duplicate summaries for this user
    existing = client.table("notices").select("notice_id").eq("summary", summary).eq("user_id", user.id).execute()
    if existing.data:
        return False

    client.table("notices").insert({
        "title": title,
        "summary": summary,
        "deadline_date": deadline_date_str,
        "raw_result": raw_result,
        "status": status,
        "is_important": 0,
        "user_id": user.id
    }).execute()
    return True

def toggle_important(notice_id, current_status):
    client = get_supabase_client()
    new_val = 0 if current_status == 1 else 1
    client.table("notices").update({"is_important": new_val}).eq("notice_id", notice_id).execute()

def delete_notice(notice_id):
    client = get_supabase_client()
    client.table("notices").delete().eq("notice_id", notice_id).execute()

def get_active_notices():
    client = get_supabase_client()
    res = client.table("notices").select("*").eq("status", "active").order("notice_id", desc=True).execute()
    return res.data if res.data else []

def get_approaching_notices(days_threshold=3):
    client = get_supabase_client()
    res = client.table("notices").select("*").eq("status", "approaching").order("notice_id", desc=True).execute()
    return res.data if res.data else []

def get_expired_notices():
    client = get_supabase_client()
    res = client.table("notices").select("*").eq("status", "expired").order("notice_id", desc=True).execute()
    return res.data if res.data else []

def get_important_notices():
    client = get_supabase_client()
    res = client.table("notices").select("*").eq("is_important", 1).order("notice_id", desc=True).execute()
    return res.data if res.data else []
