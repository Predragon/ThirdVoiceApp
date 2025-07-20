"""
Third Voice - Perfect Copy Solution
With both one-click copy and manual selection
"""

import streamlit as st
import requests
from streamlit.components.v1 import html

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
        /* Input areas */
        div.stTextArea > textarea {{
            font-size: 18px !important;
            min-height: 150px !important;
        }}
        
        /* Buttons */
        div.stButton > button {{
            width: 100%;
            padding: 12px !important;
            margin: 4px 0;
        }}
    }}
    
    /* Result card */
    .result-card {{
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        background: rgba(255,255,255,0.05);
        border-left: 4px solid {CONTEXTS["general"]["color"]};
    }}
    
    /* Copy section */
    .copy-section {{
        margin: 1rem 0;
    }}
    .selectable-text {{
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 12px;
        background: #f8f9fa;
        font-size: 16px;
        line-height: 1.5;
    }}
    .copy-instruction {{
        font-size: 14px;
        color: #666;
        text-align: center;
        margin-top: 8px;
    }}
    </style>
    """, unsafe_allow_html=True)

# ===== Smart Copy Solutions =====
def create_copy_section(text):
    """Creates both copy button and selectable text area"""
    # Copy button with visual feedback
    if st.button("📋 Copy Full Text", key="copy_btn", use_container_width=True):
        html(f"""
        <textarea id="tempCopy" style="opacity:0; position:absolute;">{text}</textarea>
        <script>
        document.getElementById('tempCopy').select();
        try {{
            document.execCommand('copy');
            alert('Copied to clipboard!');
        }} catch(e) {{
            alert('Press and hold the text below to copy');
        }}
        </script>
        """, height=0)
    
    # Fully selectable text area
    st.markdown(f"""
    <div class="copy-section">
        <div class="selectable-text">{text}</div>
        <div class="copy-instruction">
            👆 Press and hold to select any text
        </div>
    </div>
    """, unsafe_allow_html=True)

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
                <div class="result-card" style="border-color: {CONTEXTS[context]['color']}">
                    <strong>{'🔍 Analysis' if analyze_btn else '✨ Improved Message'}:</strong><br>
                    {result}
                </div>
                """, unsafe_allow_html=True)
                
                # Copy Solutions
                st.markdown("### Copy Options")
                create_copy_section(result)
                
                st.button("🔄 Try Another", use_container_width=True)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.button("🔄 Try Again", use_container_width=True)
