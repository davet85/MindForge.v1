# main.py – MindForge v1.0.0 (RCA Core Engine)

import streamlit as st
import os, json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

# === INIT ===
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ OpenAI API key missing. Check .env setup.")
    st.stop()
client = OpenAI(api_key=api_key)
PROFILE_PATH = Path("database/user_profile.json")
AVATARS = {
    "Ember": "Emotional", "Pulse": "Physical", "Vera": "Intellectual",
    "Haven": "Social", "Solace": "Spiritual", "Forge": "Occupational",
    "Ledger": "Financial", "Terra": "Environmental"
}
DEFAULT_PROMPT = (
    "You are MindForge — an AI avatar guiding recursive alignment across eight wellness domains. "
    "Use coaching loops, emotional feedback, and symbolic recursion to help the user align thought, action, and identity."
)

# === CONFIG ===
st.set_page_config("MindForge – Reflect to Evolve", layout="wide")
st.title("🧠 MindForge")
st.session_state.setdefault("onboarding_complete", False)
st.session_state.setdefault("level", 1)
st.session_state.setdefault("rca_score", 0)

# === IO ===
def save_profile(profile): 
    PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with PROFILE_PATH.open("w", encoding="utf-8") as f: json.dump(profile, f, indent=2)

def load_profile(): 
    if PROFILE_PATH.exists(): 
        with PROFILE_PATH.open("r", encoding="utf-8") as f: return json.load(f)
    return None

# === ONBOARDING ===
if not PROFILE_PATH.exists() or not st.session_state["onboarding_complete"]:
    st.subheader("🌟 Begin Your Alignment")
    name = st.text_input("📝 Name")
    age = st.number_input("🎂 Age", 10, 100)
    bio = st.text_area("📖 One sentence about you")

    st.markdown("#### ❓ What are your current challenges?")
    domains = {
        "Emotional": st.radio("Stress and emotional overload?", ["Yes", "No"]),
        "Physical": st.radio("Health, sleep, or energy issues?", ["Yes", "No"]),
        "Intellectual": st.radio("Mental stagnation or lack of purpose?", ["Yes", "No"]),
        "Social": st.radio("Relational conflict or disconnection?", ["Yes", "No"]),
        "Spiritual": st.radio("Confusion about meaning or belief?", ["Yes", "No"]),
        "Occupational": st.radio("Career dissatisfaction or burnout?", ["Yes", "No"]),
        "Financial": st.radio("Anxiety or disorganization with money?", ["Yes", "No"]),
        "Environmental": st.radio("Clutter or disconnection from space?", ["Yes", "No"]),
    }
    dominant = next((d for d, ans in domains.items() if ans == "Yes"), "Emotional")
    avatar = next((k for k, v in AVATARS.items() if v == dominant), "Ember")

    if st.button("🚀 Enter MindForge"):
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
            "history": []
        }
        save_profile(profile)
        st.session_state.update({
            "onboarding_complete": True,
            "level": 1,
            "avatar": avatar,
            "rca_score": 0
        })
        st.success(f"🎯 Assigned Champion: {avatar} ({dominant})")
        st.rerun()
    st.stop()

# === LOAD PROFILE ===
profile = load_profile()
if not profile:
    st.error("⚠️ Profile could not be loaded.")
    st.stop()

# === UI SNAPSHOT ===
st.markdown("## 🧬 Identity Snapshot")
st.markdown(f"**Name:** {profile['name']}  \n"
            f"**Avatar:** {profile['avatar']} ({AVATARS.get(profile['avatar'], 'N/A')})  \n"
            f"**Level:** {profile['level']}  \n"
            f"**RCA Score:** {profile['rca_score']}  \n"
            f"**Focus:** {profile['dimension']}  \n"
            f"**Bio:** {profile['bio']}")

# === REFLECTION INTERFACE ===
st.markdown("## 🔁 Begin Your Reflection")
user_input = st.text_area("💬 What’s on your mind today?", height=150)

if st.button("Reflect with MindForge"):
    if not user_input.strip():
        st.warning("Please write something to reflect on.")
        st.stop()

    with st.spinner("🧠 Processing..."):
        try:
            messages = [
                {"role": "system", "content": profile["generated_prompt"]},
                *profile.get("history", []),
                {"role": "user", "content": user_input}
            ]
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
                st.success(f"🎉 Level Up! Welcome to Level {profile['level']}")

            save_profile(profile)
            st.markdown("### 🧠 Avatar Feedback")
            st.markdown(reply)

        except OpenAIError as e:
            st.error(f"❌ OpenAI error: {e}")
        except Exception as e:
            st.error(f"⚠️ Unexpected error: {e}")
