\import streamlit as st
import os
import json
from pathlib import Path
from dotenv import load_dotenv
import openai

# === INIT ===
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ OpenAI API key missing. Check your .env file.")
    st.stop()
client = openai.OpenAI(api_key=api_key)

# === CONSTANTS ===
PROFILE_PATH = Path("database/user_profile.json")
DIMENSIONS = ["Emotional", "Physical", "Intellectual", "Social", "Spiritual", "Occupational", "Financial", "Environmental"]

# === SESSION DEFAULTS ===
st.session_state.setdefault("onboarding_complete", False)
st.session_state.setdefault("level", 1)
st.session_state.setdefault("rca_score", 0)

# === UTILS ===
def save_profile(profile):
    PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with PROFILE_PATH.open("w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)

def load_profile():
    if PROFILE_PATH.exists():
        with PROFILE_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    return None

# === NORMALIZATION ===
def normalize(score):
    return int((score / 30) * 100)  # Max 3 Qs per domain scored 1–10

# === GPT Tier Assignment ===
def analyze_user(profile):
    system_msg = """
You are the Onboarding Logic Engine for Introspect Nexus.
1. Analyze questionnaire scores.
2. Parse user narrative.
3. Assign functional tier (1-4):
   - 1: Survival, 2: Stuck, 3: Building, 4: Optimizing
4. Return JSON:
{
  \"normalized_scores\": {...},
  \"composite_score\": ..., 
  \"functional_tier\": ..., 
  \"emotional_tone\": \"..., ..., ...\"
}
"""
    user_msg = {
        "name": profile['name'],
        "age": profile['age'],
        "email": profile['email'],
        "sentence": profile['sentence'],
        "narrative": profile['narrative'],
        "raw_scores": profile['raw_scores']
    }
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": json.dumps(user_msg)}
        ]
    )
    content = response.choices[0].message.content.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        st.error("❌ GPT response was not valid JSON. See output below:")
        st.code(content)
        raise

# === ONBOARDING ===
if not PROFILE_PATH.exists() or not st.session_state["onboarding_complete"]:
    st.title("🧠 MindForge Onboarding")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=10, max_value=100)
    email = st.text_input("Email")
    code = st.text_input("Enter dummy verification code")
    sentence = st.text_input("Who are you in one sentence?")
    use_tools = st.text_input("Do you use any self-development tools now? (optional)")
    time_spent = st.text_input("How much time weekly on your growth? (optional)")
    pay_interest = st.text_input("Would you pay for AI guidance? (optional)")

    st.subheader("🧪 8-Domain Wellness Survey")
    domain_qs = {
        "Emotional": ["How often do you feel emotionally overwhelmed?"],
        "Physical": ["Rate your sleep and energy levels."],
        "Intellectual": ["Do you feel mentally stimulated or engaged?"],
        "Social": ["Are your relationships satisfying and healthy?"],
        "Spiritual": ["Do you feel aligned with your beliefs or purpose?"],
        "Occupational": ["How satisfied are you with your current work or role?"],
        "Financial": ["Rate your current sense of financial control."],
        "Environmental": ["Do you feel calm and supported by your surroundings?"]
    }

    raw_scores = {}
    for domain in DIMENSIONS:
        st.markdown(f"**{domain} Wellness**")
        score = sum([st.slider(q, 1, 10, 5, key=f"{domain}_{q}") for q in domain_qs[domain]])
        raw_scores[domain.lower()] = score

    st.subheader("📝 Narrative Input")
    narrative = st.text_area("Describe your current struggles, where you are in life, and who you want to become.", height=200)

    if st.button("Submit & Analyze"):
        profile = {
            "name": name,
            "age": age,
            "email": email,
            "sentence": sentence,
            "narrative": narrative,
            "raw_scores": raw_scores,
            "use_tools": use_tools,
            "time_spent": time_spent,
            "pay_interest": pay_interest
        }
        result = analyze_user(profile)
        profile.update(result)
        save_profile(profile)
        st.session_state.update({"onboarding_complete": True})
        st.success(f"🧬 Tier Assigned: {result['functional_tier']} | Tone: {result['emotional_tone']}")
        st.rerun()
    st.stop()

# === DASHBOARD ===
profile = load_profile()
if not profile:
    st.error("Profile load error.")
    st.stop()

st.title("🧭 MindForge Dashboard")
st.markdown(f"**Name:** {profile['name']}")
st.markdown(f"**Functional Tier:** {profile['functional_tier']}")
st.markdown(f"**Composite Score:** {profile['composite_score']}")
st.markdown(f"**Tone:** {profile['emotional_tone']}")
st.markdown("---")

st.subheader("💬 Begin Daily Reflection")
reflection = st.text_area("What’s present for you today?", height=150)
if st.button("Submit Reflection"):
    st.success("Reflection submitted. Future RCA scoring will be added here.")