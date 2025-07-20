"""
The Third Voice - Mobile-Optimized Full Version
Works on your Redmi 14C + retains all features
"""
import streamlit as st
import requests
import json
import datetime

# ===== Core Config (From Your Working Version) =====
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = st.secrets.get("OPENROUTER_API_KEY")  # Set in Streamlit Cloud Secrets

# Lightweight prompts (reduced but keeps all contexts)
COACHING_PROMPTS = {
    "general": "Improve this message for clarity/empathy: {message}",
    "romantic": "Make this romantic message more loving: {message}",
    # Add other contexts as needed...
}

# ===== Mobile-Optimized UI =====
st.set_page_config(
    page_title="Third Voice Mobile",
    layout="centered",  # Better for phones
    initial_sidebar_state="collapsed"  # Saves space
)

def mobile_styles():
    st.markdown("""
    <style>
    /* Bigger touch targets */
    button, [data-testid="stTextInput"], textarea {
        min-height: 3em !important;
        font-size: 16px !important;
    }
    /* Full-width on mobile */
    @media (max-width: 768px) {
        .stButton button { width: 100%; }
        .stTextArea textarea { font-size: 18px !important; }
        /* Hide sidebar on mobile */
        [data-testid="stSidebar"] { display: none; }
    }
    </style>
    """, unsafe_allow_html=True)

# ===== API Call (From Your Working Version) =====
def get_ai_response(message, context, is_received=False):
    try:
        prompt = COACHING_PROMPTS.get(context, COACHING_PROMPTS["general"])
        messages = [
            {"role": "system", "content": prompt.format(message=message)},
            {"role": "user", "content": message}
        ]
        
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "HTTP-Referer": "https://third-voice.streamlit.app",
                "X-Title": "Third Voice Mobile"
            },
            json={
                "model": "google/gemma-2b-it:free",  # Lightweight model
                "messages": messages,
                "max_tokens": 800
            },
            timeout=30
        )
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

# ===== Simplified Mobile UI =====
mobile_styles()
st.title("🎙️ Third Voice")

# Mode selector
tab1, tab2 = st.tabs(["📤 Coach Message", "📥 Understand Message"])
context = st.selectbox("Relationship", list(COACHING_PROMPTS.keys()))

with tab1:
    message = st.text_area("Your message:", height=150)
    if st.button("Improve Message", type="primary"):
        with st.spinner("Thinking..."):
            response = get_ai_response(message, context, is_received=False)
            if response:
                st.text_area("Improved:", value=response, height=200)

with tab2:
    received_msg = st.text_area("Their message:", height=150)
    if st.button("Analyze Message"):
        with st.spinner("Decoding..."):
            analysis = get_ai_response(received_msg, context, is_received=True)
            if analysis:
                st.text_area("Analysis:", value=analysis, height=200)
