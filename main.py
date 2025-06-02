# main.py – MindForge v1.2.0 (Avatar Assessment First Launch Prototype)

import streamlit as st
import json
import os
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv

# === INIT ===
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("❌ OpenAI API key missing. Check your .env file.")
    st.stop()
client = OpenAI(api_key=api_key)

AVATARS = {
    "Ember":      {"domain": "Emotional",     "emoji": "🔥", "summary": "You are driven by emotion and intensity. You feel deeply, react instinctively, and carry unresolved wounds that fuel your fire."},
    "Pulse":      {"domain": "Physical",      "emoji": "💪", "summary": "You are grounded in the body. Your focus is health, vitality, and discipline, but tension may manifest somatically."},
    "Vera":       {"domain": "Intellectual",  "emoji": "🧠", "summary": "You are guided by thought and logic. Analysis is your armor—but sometimes at the cost of emotional connection."},
    "Haven":      {"domain": "Social",        "emoji": "🤝", "summary": "You seek harmony and belonging. Relationships shape your identity, but people-pleasing may mask your truth."},
    "Solace":     {"domain": "Spiritual",     "emoji": "🕊️", "summary": "You are a seeker. Meaning, belief, and purpose define your path. You may wrestle with existential fear or faith loss."},
    "Forge":      {"domain": "Occupational",  "emoji": "🛠️", "summary": "You define yourself through action. Productivity and mission matter most—but burnout is close behind."},
    "Ledger":     {"domain": "Financial",     "emoji": "💰", "summary": "You are security-focused. Finances give you control—but also anxiety, scarcity, or power dynamics."},
    "Terra":      {"domain": "Environmental", "emoji": "🌿", "summary": "You are shaped by space and rhythm. Clutter, disconnection, or chaos in your environment mirrors your inner state."}
}

DEFAULT_PROMPT = (
    "You are MindForge — an advanced recursive mirror. Begin by analyzing this user's answers to a multi-domain cognitive wellness scan. "
    "Detect emotional subtext, cognitive rigidity, relational scripts, and blindspots. Then generate layered follow-up prompts to entice deeper self-reflection."
)

st.set_page_config("MindForge – Cognitive Assessment", layout="wide")
st.title("🧠 MindForge")

# === LANDING ASSESSMENT ===
st.subheader("🌐 Cognitive Alignment Scan")

questions = [
    "How often do you feel emotionally overwhelmed or dysregulated?",
    "How would you describe your current physical state (energy, sleep, movement)?",
    "Do you feel intellectually stimulated or mentally stagnant lately?",
    "How connected and authentic do you feel in your relationships?",
    "Are you currently struggling with belief, purpose, or spiritual identity?",
    "How would you describe your work or daily structure right now?",
    "Are finances a source of anxiety, control, or disorganization for you?",
    "Does your environment feel like a sanctuary or a source of stress?"
]

domains = list(AVATARS.keys())
user_scores = {}

for i, q in enumerate(questions):
    avatar = domains[i]
    st.markdown(f"**{AVATARS[avatar]['emoji']} {q}**")
    user_scores[avatar] = st.slider("", 0, 10, 5, key=f"q{i}")

if st.button("🔍 Analyze & Assign Avatar"):
    dominant_avatar = max(user_scores, key=user_scores.get)
    selected = AVATARS[dominant_avatar]

    st.markdown("---")
    st.header(f"{selected['emoji']} Assigned Avatar: {dominant_avatar}")
    st.write(f"**Domain:** {selected['domain']}")
    st.write(f"**Reflection:** {selected['summary']}")

    # Generate deeper questions from GPT
    input_summary = "\n".join([f"{AVATARS[k]['domain']}: {v}/10" for k, v in user_scores.items()])
    try:
        with st.spinner("MindForge is constructing a deeper mirror..."):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": DEFAULT_PROMPT},
                    {"role": "user", "content": input_summary}
                ],
                temperature=0.7
            )
            reply = response.choices[0].message.content
            st.markdown("### 🧠 Insight & Deep Reflection Prompts")
            st.markdown(reply)
    except OpenAIError as e:
        st.error(f"❌ OpenAI API error: {e}")
    except Exception as e:
        st.error(f"⚠️ Unexpected error: {e}")
