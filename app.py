"""
Third Voice - Guaranteed Copy Solution
Working version for Android devices
"""

import streamlit as st
import requests
from streamlit.components.v1 import html
import time

# ===== Configuration =====
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = st.secrets.get("OPENROUTER_API_KEY")

CONTEXTS = {
    "general": {"color": "#5D9BFF", "icon": "💙"},
    "romantic": {"color": "#FF7EB9", "icon": "❤️"},
    "workplace": {"color": "#6EE7B7", "icon": "💼"}
}

# ===== Mobile UI Setup =====
st.set_page_config(layout="centered")

def apply_styles():
    st.markdown(f"""
    <style>
    /* Mobile-optimized styles */
    @media (max-width: 768px) {{
        div.stTextArea > textarea {{
            font-size: 18px !important;
            min-height: 150px !important;
        }}
        div.stButton > button {{
            width: 100%;
            padding: 14px !important;
        }}
    }}
    /* Copy section */
    .copy-area {{
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 12px;
        margin: 10px 0;
        background: #f8f9fa;
    }}
    .copy-instruction {{
        font-size: 14px;
        color: #666;
        text-align: center;
        margin-top: 8px;
    }}
    </style>
    """, unsafe_allow_html=True)

# ===== Guaranteed Copy Solution =====
def create_copy_area(text):
    """Creates a text area with manual copy instructions"""
    html(f"""
    <div class="copy-area">
        <textarea id="copyTarget" 
                  style="width:100%; height:150px; border:none; resize:none;"
                  readonly>{text}</textarea>
        <div class="copy-instruction">
            👆 Press and hold text, then select "Copy"
        </div>
    </div>
    <script>
    // Auto-select text when area is clicked
    document.getElementById('copyTarget').addEventListener('click', function() {{
        this.select();
    }});
    </script>
    """, height=200)

# ===== App Interface =====
apply_styles()

# 1. Relationship Selector
context = st.selectbox(
    "Select relationship:",
    options=list(CONTEXTS.keys()),
    format_func=lambda x: f"{CONTEXTS[x]['icon']} {x.capitalize()}"
)

# 2. Message Input
user_input = st.text_area(
    "Your message:",
    placeholder="Type or paste here...",
    height=150
)

# 3. Action Buttons
col1, col2 = st.columns(2)
with col1:
    analyze_btn = st.button("🔍 Analyze", use_container_width=True)
with col2:
    coach_btn = st.button("✨ Improve", type="primary", use_container_width=True)

# 4. Results Handling
if analyze_btn or coach_btn:
    if not user_input.strip():
        st.warning("Please enter a message")
    else:
        with st.spinner("Thinking..."):
            try:
                # API Call
                response = requests.post(
                    API_URL,
                    headers={
                        "Authorization": f"Bearer {API_KEY}",
                        "HTTP-Referer": "https://third-voice.streamlit.app"
                    },
                    json={
                        "model": "mistralai/mistral-7b-instruct:free",
                        "messages": [{
                            "role": "system",
                            "content": "Analyze the emotions in this message:" if analyze_btn 
                                      else "Improve this message for clarity and kindness:"
                        },{
                            "role": "user",
                            "content": f"[{context.capitalize()}] {user_input}"
                        }],
                        "max_tokens": 600
                    },
                    timeout=25
                )
                result = response.json()["choices"][0]["message"]["content"]
                
                # Display Results
                st.markdown(f"""
                <div style="border-left: 4px solid {CONTEXTS[context]['color']}; 
                            padding: 1rem; margin: 1rem 0; border-radius: 0 8px 8px 0">
                    <strong>{'🔍 Analysis' if analyze_btn else '✨ Improved Message'}:</strong><br>
                    {result}
                </div>
                """, unsafe_allow_html=True)
                
                # Guaranteed Copy Section
                st.markdown("### Copy Your Result")
                create_copy_area(result)
                
                st.button("🔄 Try Another", use_container_width=True)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.button("🔄 Try Again", use_container_width=True)
