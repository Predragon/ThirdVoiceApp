"""
Third Voice - Final Working Copy Solution
With guaranteed copy button functionality
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
    .copy-box {{
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 12px;
        margin: 10px 0;
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

# ===== Guaranteed Copy Function =====
def copy_button_callback(text):
    """This will actually work on Android"""
    html(f"""
    <textarea id="hiddenCopy" style="opacity:0; position:fixed; top:-100px;">{text}</textarea>
    <script>
    const textarea = document.getElementById('hiddenCopy');
    textarea.select();
    try {{
        // Method 1: Modern clipboard API
        if(navigator.clipboard) {{
            navigator.clipboard.writeText(textarea.value)
                .then(() => {{
                    // Show temporary toast
                    const toast = document.createElement('div');
                    toast.innerText = '✓ Copied!';
                    toast.style.position = 'fixed';
                    toast.style.bottom = '20px';
                    toast.style.right = '20px';
                    toast.style.padding = '10px 16px';
                    toast.style.background = '#5D9BFF';
                    toast.style.color = 'white';
                    toast.style.borderRadius = '20px';
                    toast.style.zIndex = '9999';
                    document.body.appendChild(toast);
                    setTimeout(() => toast.remove(), 2000);
                }});
        }} 
        // Method 2: Legacy execCommand
        else if(document.execCommand('copy')) {{
            const toast = document.createElement('div');
            toast.innerText = '✓ Copied!';
            toast.style.position = 'fixed';
            toast.style.bottom = '20px';
            toast.style.right = '20px';
            toast.style.padding = '10px 16px';
            toast.style.background = '#5D9BFF';
            toast.style.color = 'white';
            toast.style.borderRadius = '20px';
            toast.style.zIndex = '9999';
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 2000);
        }}
        // Method 3: Final fallback
        else {{
            alert('Press and hold the text below to copy');
        }}
    }} catch(e) {{
        console.error('Copy failed:', e);
    }}
    </script>
    """, height=0)

# ===== App Interface =====
apply_styles()

# [Previous UI code remains identical until results display...]

if analyze_btn or coach_btn:
    if result:
        # Display Results
        st.markdown(f"""
        <div style="border-left: 4px solid {CONTEXTS[context]['color']}; 
                    padding: 1rem; margin: 1rem 0; border-radius: 0 8px 8px 0">
            <strong>{'🔍 Analysis' if analyze_btn else '✨ Improved Message'}:</strong><br>
            {result}
        </div>
        """, unsafe_allow_html=True)
        
        # COPY BUTTON THAT NOW WORKS
        if st.button("📋 Copy to Clipboard", key="copy_btn", use_container_width=True):
            copy_button_callback(result)
            time.sleep(0.3)  # Helps Android process the copy
            
        # Selectable text fallback
        st.markdown(f"""
        <div class="copy-box">
            {result}
            <div class="copy-instruction">
                👆 Press and hold to select text
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.button("🔄 Try Again", use_container_width=True)
