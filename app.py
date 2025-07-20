"""
The Third Voice - Mobile Optimized
Full working version for Android editing
"""

import streamlit as st
import requests
import json
import datetime

# ===== Configuration =====
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = st.secrets.get("OPENROUTER_API_KEY")  # Set in Streamlit Secrets

COACHING_PROMPTS = {
    "general": "Improve this message for clarity and kindness: {message}",
    "romantic": "Make this romantic message more loving: {message}",
    "coparenting": "Rephrase this co-parenting message to be child-focused: {message}",
    "workplace": "Make this professional message clearer: {message}",
    "family": "Improve this family message with care: {message}",
    "friend": "Help this friendship message sound supportive: {message}"
}

# ===== Mobile UI Setup =====
st.set_page_config(
    page_title="Third Voice Mobile",
    layout="centered",
    initial_sidebar_state="collapsed"
)

def mobile_styles():
    st.markdown("""
    <style>
    /* Mobile-first design */
    @media (max-width: 768px) {
        /* Bigger touch targets */
        button, [data-testid="stTextInput"], textarea {
            min-height: 3em !important;
            font-size: 16px !important;
        }
        /* Full-width elements */
        .stButton button { width: 100%; }
        .stTextArea textarea { font-size: 18px !important; }
        /* Simplified layout */
        [data-testid="stSidebar"] { display: none; }
        .stAlert { font-size: 18px !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# ===== Core Functions =====
def get_ai_response(message, context):
    """Robust API call with full error handling"""
    try:
        prompt = COACHING_PROMPTS.get(context, COACHING_PROMPTS["general"])
        
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "HTTP-Referer": "https://third-voice.streamlit.app",
                "X-Title": "Third Voice Mobile"
            },
            json={
                "model": "google/gemma-2b-it:free",
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.7,
                "max_tokens": 800
            },
            timeout=30
        )
        
        # Validate response structure
        data = response.json()
        if not data.get("choices"):
            st.error("API returned unexpected format")
            return None
            
        return data["choices"][0]["message"]["content"]
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# ===== App Interface =====
mobile_styles()
st.title("🎙️ Third Voice")

# Main tabs
tab1, tab2 = st.tabs(["📤 Send Message", "📥 Receive Message"])
context = st.selectbox("Relationship Type", list(COACHING_PROMPTS.keys()))

with tab1:
    user_message = st.text_area("Your Message:", height=150)
    if st.button("Improve Message", type="primary"):
        if user_message.strip():
            with st.spinner("Optimizing..."):
                response = get_ai_response(user_message, context)
                if response:
                    st.text_area("Improved Message:", value=response, height=200)
        else:
            st.warning("Please enter a message")

with tab2:
    their_message = st.text_area("Their Message:", height=150)
    if st.button("Analyze Message"):
        if their_message.strip():
            with st.spinner("Understanding..."):
                analysis = get_ai_response(their_message, context)
                if analysis:
                    st.text_area("Analysis:", value=analysis, height=200)
        else:
            st.warning("Please enter a message")

# Debug section (hidden by default)
with st.expander("⚙️ Debug Info", False):
    st.write("Last API Key Check:", "Valid" if API_KEY else "Missing")
    st.write("Available Models:", ["gemma-2b-it", "mistral-7b"])
