"""
Third Voice - Optimized Mobile Workflow
Finalized version with emotional intelligence UI
"""

import streamlit as st
import requests

# ===== Configuration =====
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = st.secrets.get("OPENROUTER_API_KEY")  # Set in Streamlit Secrets

# Emotional context settings
CONTEXTS = {
    "general": {
        "color": "#5D9BFF",  # Calm blue
        "icon": "💙",
        "prompt": "Improve this message to be clearer and kinder:"
    },
    "romantic": {
        "color": "#FF7EB9",  # Warm pink
        "icon": "❤️", 
        "prompt": "Make this romantic message more loving:"
    },
    "workplace": {
        "color": "#6EE7B7",  # Professional green
        "icon": "💼",
        "prompt": "Rephrase this professionally:"
    }
}

# ===== Mobile UI Setup =====
st.set_page_config(
    page_title="Third Voice",
    layout="centered",
    initial_sidebar_state="collapsed"
)

def apply_styles():
    st.markdown(f"""
    <style>
    /* Base mobile styles */
    @media (max-width: 768px) {{
        /* Input area */
        div.stTextArea > textarea {{
            font-size: 18px !important;
            min-height: 150px !important;
        }}
        
        /* Buttons */
        div.stButton > button {{
            width: 100%;
            padding: 14px !important;
            margin: 4px 0;
            font-size: 16px !important;
        }}
        
        /* Hide footer */
        footer {{ visibility: hidden; }}
    }}
    
    /* Context cards */
    .context-card {{
        border-radius: 12px;
        padding: 1.2rem;
        margin: 1rem 0;
        background-color: rgba(255,255,255,0.05);
        border-left: 6px solid {CONTEXTS["general"]["color"]};
        font-size: 16px;
    }}
    </style>
    """, unsafe_allow_html=True)

# ===== App Interface =====
apply_styles()

# 1. Relationship Selector
context = st.selectbox(
    "Select relationship:",
    options=list(CONTEXTS.keys()),
    format_func=lambda x: f"{CONTEXTS[x]['icon']} {x.capitalize()}"
)

# 2. Central Input
user_input = st.text_area(
    "Compose your message:",
    placeholder="Type or paste here...",
    height=150,
    key="input"
)

# 3. Action Buttons (Bottom Bar)
col1, col2 = st.columns(2)
with col1:
    analyze_btn = st.button("🔍 Analyze", help="Understand their message", use_container_width=True)
with col2:
    coach_btn = st.button("✨ Improve", help="Refine your message", type="primary", use_container_width=True)

# 4. Processing & Results
if analyze_btn or coach_btn:
    if not user_input.strip():
        st.warning("Please enter a message")
    else:
        with st.spinner("Thinking..."):
            try:
                # Prepare prompt
                action = "analyze" if analyze_btn else "coach"
                prompt = CONTEXTS[context]["prompt"] + f"\n\n{user_input}"
                
                # API Call
                response = requests.post(
                    API_URL,
                    headers={
                        "Authorization": f"Bearer {API_KEY}",
                        "HTTP-Referer": "https://third-voice.streamlit.app",
                        "X-Title": "Third Voice Mobile"
                    },
                    json={
                        "model": "mistralai/mistral-7b-instruct:free",
                        "messages": [{
                            "role": "system",
                            "content": prompt
                        }],
                        "temperature": 0.7,
                        "max_tokens": 600
                    },
                    timeout=25
                )
                
                # Show results
                result = response.json()["choices"][0]["message"]["content"]
                st.markdown(f"""
                <div class="context-card" style="border-color: {CONTEXTS[context]['color']}">
                    <strong>{'🔍 Analysis' if analyze_btn else '✨ Improved Message'}:</strong><br>
                    {result}
                </div>
                """, unsafe_allow_html=True)
                
                # Result actions
                st.download_button(
                    "📋 Copy Text",
                    data=result,
                    mime="text/plain",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.button("🔄 Try Again", use_container_width=True)

# Debug view (hidden)
if st.secrets.get("DEBUG", False):
    st.write("Last run:", datetime.datetime.now().strftime("%H:%M:%S"))
