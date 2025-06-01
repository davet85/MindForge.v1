# main.py – MindForge v1.1.4 (Fixed Logout, Enticing Prompts, Enhanced UX)

import streamlit as st
import os, json, hashlib
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

# === INIT ===
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ OpenAI API key missing. Check your .env file.")
    st.stop()
client = OpenAI(api_key=api_key)

AVATARS = {
    "Ember":      {"domain": "Emotional",     "emoji": "🔥"},
    "Pulse":      {"domain": "Physical",      "emoji": "💪"},
    "Vera":       {"domain": "Intellectual",  "emoji": "🧠"},
    "Haven":      {"domain": "Social",        "emoji": "🤝"},
    "Solace":     {"domain": "Spiritual",     "emoji": "🕊️"},
    "Forge":      {"domain": "Occupational",  "emoji": "🛠️"},
    "Ledger":     {"domain": "Financial",     "emoji": "💰"},
    "Terra":      {"domain": "Environmental", "emoji": "🌿"}
}

DEFAULT_PROMPT = (
    "You are MindForge — a symbolic AI avatar guiding deep self-reflection across emotional, physical, and existential dimensions. "
    "Encourage radical honesty, ask probing questions, and deliver recursive feedback to unlock clarity, alignment, and growth."
)

st.set_page_config("MindForge – Reflect to Evolve", layout="wide")
st.title("🧠 MindForge")

# Force re-validation of session state for deployment edge cases
if st.session_state.get("authenticated") and not st.session_state.get("profile"):
    st.session_state["authenticated"] = False
    st.session_state["username"] = None

# === UTILS ===
def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_profile_path(username):
    return Path(f"database/user_profile_{username}.json")

def save_profile(profile, username):
    path = get_profile_path(username)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)

def load_profile(username):
    path = get_profile_path(username)
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return None

def authenticate(username, password):
    profile = load_profile(username)
    if profile and profile.get("password_hash") == hash_pass(password):
        return profile
    return None

# === SESSION DEFAULTS ===
if not st.session_state.get("authenticated") or not st.session_state.get("profile"):
    st.session_state.update({
        "authenticated": False,
        "username": None,
        "profile": None,
        "create_mode": False
    })

# === LOGOUT ===
if st.session_state["authenticated"]:
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

# === CREATE PROFILE FLOW ===
if st.session_state["create_mode"]:
    st.subheader("🆕 Create Your Reflective Identity")
    new_username = st.text_input("Choose a Username")
    new_password = st.text_input("Choose a Password", type="password")
    name = st.text_input("📝 What's your name?")
    age = st.number_input("🎂 How old are you?", 10, 100)
    bio = st.text_area("📓 Write a sentence that describes who you are — or who you're becoming.")

    st.markdown("#### 🧭 What patterns or struggles feel most active in your life?")
    domains = {k: st.radio(f"{AVATARS[k]['emoji']} {AVATARS[k]['domain']} challenges?", ["Yes", "No"], key=k) for k in AVATARS}
    dominant = next((AVATARS[k]['domain'] for k in AVATARS if domains[k] == "Yes"), "Emotional")
    avatar = next((k for k, v in AVATARS.items() if v["domain"] == dominant), "Ember")

    if st.button("🚀 Create My Profile"):
        if not new_username or not new_password:
            st.warning("Please enter both a username and password.")
            st.stop()
        if get_profile_path(new_username).exists():
            st.error("🚫 Username already exists. Try a different one.")
            st.stop()

        profile = {
            "name": name,
            "age": age,
            "bio": bio,
            "dimension": dominant,
            "avatar": avatar,
            "level": 1,
            "rca_score": 0,
            "missions": [],
            "generated_prompt": DEFAULT_PROMPT,
            "history": [],
            "password_hash": hash_pass(new_password)
        }
        save_profile(profile, new_username)
        st.session_state.update({
            "authenticated": True,
            "username": new_username,
            "profile": profile,
            "create_mode": False
        })
        st.success(f"🌟 Avatar Assigned: {avatar} ({dominant})")
        st.rerun()

    if st.button("⬅️ Back to Login"):
        st.session_state["create_mode"] = False
        st.rerun()
    st.stop()

# === LOGIN FLOW ===
if not st.session_state["authenticated"]:
    st.subheader("🔐 Log In to Continue")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Log In"):
            profile = authenticate(username, password)
            if profile:
                st.session_state.update({
                    "authenticated": True,
                    "username": username,
                    "profile": profile
                })
                st.success(f"✅ Welcome back, {profile['name']}!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials.")

    with col2:
        if st.button("New Profile"):
            st.session_state["create_mode"] = True
            st.rerun()
    st.stop()

# === ACTIVE SESSION ===
profile = st.session_state["profile"]
username = st.session_state["username"]

# === SESSION RESUME ===
st.markdown("## 🔁 Resume or Reset")
if profile.get("history"):
    last_user = next((m["content"] for m in reversed(profile["history"]) if m["role"] == "user"), None)
    last_bot = next((m["content"] for m in reversed(profile["history"]) if m["role"] == "assistant"), None)
    if last_user:
        st.markdown("### 🧠 Last Reflection")
        st.markdown(f"**You said:** {last_user}")
    if last_bot:
        st.markdown(f"**MindForge replied:** {last_bot}")
    if st.radio("Continue session?", ["Yes", "Start Over"], index=0) == "Start Over":
        profile["history"] = []
        profile["rca_score"] = 0
        profile["level"] = 1
        save_profile(profile, username)
        st.rerun()

# === IDENTITY SNAPSHOT ===
avatar = profile["avatar"]
avatar_data = AVATARS.get(avatar, {"emoji": "❓", "domain": "Unknown"})
st.markdown("## 📃 Identity Snapshot")
st.markdown(f"""
**Name:** {profile['name']}  
**Avatar:** {avatar_data['emoji']} {avatar} ({avatar_data['domain']})  
**Level:** {profile['level']}  
**RCA Score:** {profile['rca_score']}  
**Focus:** {profile['dimension']}  
**Bio:** {profile['bio']}
""")

# === REFLECTION INPUT ===
st.markdown("## 🕵️‍ Dive Deeper")
user_input = st.text_area("📣 What's unfolding in your inner world right now? What truth wants to be seen?", height=150)

if st.button("Reflect with MindForge"):
    if not user_input.strip():
        st.warning("Reflection requires a starting point — share something real.")
        st.stop()
    with st.spinner("MindForge is listening and responding..."):
        try:
            messages = [{"role": "system", "content": profile["generated_prompt"]}]
            messages += profile.get("history", []) + [{"role": "user", "content": user_input}]
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.6
            )
            reply = response.choices[0].message.content
            profile["history"].append({"role": "user", "content": user_input})
            profile["history"].append({"role": "assistant", "content": reply})
            profile["rca_score"] += 10
            if profile["rca_score"] >= profile["level"] * 50:
                profile["level"] += 1
                st.balloons()
                st.success(f"🎉 Breakthrough Achieved — Welcome to Level {profile['level']}!")
            save_profile(profile, username)
            st.session_state["profile"] = profile
            st.markdown("### 🔮 Avatar Feedback")
            st.markdown(reply)
        except OpenAIError as e:
            st.error(f"❌ OpenAI API error: {e}")
        except Exception as e:
            st.error(f"⚠️ Unexpected error: {e}")
