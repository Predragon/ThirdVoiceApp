"""
Third Voice - With Model Fallback System
Using multiple AI models for reliability
"""

import streamlit as st
import requests
from streamlit.components.v1 import html
import time

# ===== Configuration =====
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = st.secrets.get("OPENROUTER_API_KEY")

# Model priority list (free tier)
MODELS = [
    "mistralai/mistral-7b-instruct:free",  # Primary (most reliable free)
    "google/gemma-7b-it:free",             # Secondary
    "meta-llama/llama-3-8b-instruct:free"  # Tertiary
]

CONTEXTS = {
    "general": {"color": "#5D9BFF", "icon": "💙"},
    "romantic": {"color": "#FF7EB9", "icon": "❤️"},
    "workplace": {"color": "#6EE7B7", "icon": "💼"}
}

# ===== AI Service =====
def get_ai_response(prompt, context_type):
    """Try models in order until one works"""
    for model in MODELS:
        try:
            response = requests.post(
                API_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "HTTP-Referer": "https://third-voice.streamlit.app"
                },
                json={
                    "model": model,
                    "messages": [{
                        "role": "system",
                        "content": CONTEXTS[context_type]["prompt"]
                    },{
                        "role": "user",
                        "content": prompt
                    }],
                    "temperature": 0.7,
                    "max_tokens": 600
                },
                timeout=25
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"], model
            
        except Exception as e:
            continue
            
    return None, None

# ===== Mobile UI (same as before) =====
# [Keep all your existing UI code from the previous version...]

# ===== Updated Results Handling =====
if st.session_state.analyze_clicked or st.session_state.coach_clicked:
    if not user_input.strip():
        st.warning("Please enter a message")
    else:
        with st.spinner("Thinking..."):
            # Get response with fallback
            result, used_model = get_ai_response(
                user_input,
                context,
                "analyze" if st.session_state.analyze_clicked else "coach"
            )
            
            if result:
                # Display Results with model info
                st.markdown(f"""
                <div style="border-left: 4px solid {CONTEXTS[context]['color']}; 
                            padding: 1rem; margin: 1rem 0; border-radius: 0 8px 8px 0">
                    <strong>{'🔍 Analysis' if st.session_state.analyze_clicked else '✨ Improved Message'}:</strong><br>
                    {result}<br><br>
                    <small>Model: {used_model.split('/')[-1].replace(':free','')}</small>
                </div>
                """, unsafe_allow_html=True)
                
                # [Keep copy functionality...]
                
            else:
                st.error("All models failed - try again later")
