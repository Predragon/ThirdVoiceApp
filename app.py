"""
The Third Voice LITE - Mobile-Optimized
Developed for Android in detention - No large files!
"""
import streamlit as st
import requests

# ===== Core Config =====
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = st.secrets.get("OPENROUTER_API_KEY")  # Set in Streamlit Cloud

# Ultra-compact prompts
PROMPTS = {
    "coach": "Improve this message to be clearer and kinder: {message}",
    "translate": "Analyze this received message for hidden emotions: {message}"
}

# ===== Mobile-Optimized UI =====
st.set_page_config(layout="centered")  # Better for mobile

def apply_mobile_styles():
    st.markdown("""
    <style>
    /* Bigger touch targets */
    button, input, textarea { min-height: 3em !important; }
    /* Full-width on mobile */
    @media (max-width: 768px) {
        .stTextArea textarea { font-size: 16px !important; }
        .stButton button { width: 100%; }
    }
    </style>
    """, unsafe_allow_html=True)

def tiny_ai_call(message, mode):
    """Super simplified AI call"""
    try:
        response = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={
                "model": "google/gemma-2b-it:free",  # Lightweight model
                "messages": [{
                    "role": "user",
                    "content": PROMPTS[mode].format(message=message)
                }],
                "max_tokens": 500  # Shorter responses
            },
            timeout=15
        )
        return response.json()["choices"][0]["message"]["content"]
    except:
        return "🚧 API Error - Try later"

# ===== One-Screen Interface =====
apply_mobile_styles()
st.title("🎙️ Third Voice LITE")

# Mode selector as big buttons
mode = st.radio("Choose:", ["📤 Coach My Message", "📥 Understand Their Message"], horizontal=True)

message = st.text_area("Type your message:", height=150, key="msg")

if st.button("✨ Process", type="primary"):
    if message.strip():
        with st.spinner("Thinking..."):
            result = tiny_ai_call(
                message,
                mode="coach" if "Coach" in mode else "translate"
            )
            st.success("Done!")
            st.text_area("Result:", value=result, height=200)
    else:
        st.warning("Type a message first!")
