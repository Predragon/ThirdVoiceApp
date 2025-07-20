"""
Third Voice - Fixed API Version
Combining the best of both versions with proper API handling
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
st.set_page_config(layout="centered", page_title="Third Voice")

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
    .copy-toast {{
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 10px 16px;
        background: #5D9BFF;
        color: white;
        border-radius: 20px;
        z-index: 9999;
    }}
    </style>
    """, unsafe_allow_html=True)

# ===== Guaranteed Copy Function =====
def copy_to_clipboard(text):
    """Universal copy solution with visual feedback"""
    html(f"""
    <textarea id="tempCopy" style="opacity:0; position:absolute;">{text}</textarea>
    <script>
    function showToast() {{
        const toast = document.createElement('div');
        toast.className = 'copy-toast';
        toast.innerHTML = '✓ Copied!';
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 2000);
    }}
    
    const textarea = document.getElementById('tempCopy');
    textarea.select();
    
    try {{
        // Modern API first
        if(navigator.clipboard) {{
            navigator.clipboard.writeText(`{text}`)
                .then(() => showToast())
                .catch(() => document.execCommand('copy') && showToast());
        }} 
        // Legacy method
        else if(document.execCommand('copy')) {{
            showToast();
        }}
        // Final fallback
        else {{
            alert('Press and hold the text below to copy');
        }}
    }} catch(e) {{
        console.error('Copy failed:', e);
    }}
    </script>
    """, height=0)

# ===== API Functions =====
def call_openrouter_api(prompt, context, analyze_mode=True):
    """Call OpenRouter API with proper error handling"""
    if not API_KEY:
        return "⚠️ API key not configured. Please add OPENROUTER_API_KEY to your Streamlit secrets."
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://thirdvoiceapp.streamlit.app",
        "X-Title": "Third Voice Message Analyzer"
    }
    
    data = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [
            {
                "role": "system",
                "content": "Analyze the emotions in this message:" if analyze_mode 
                          else "Improve this message for clarity and kindness:"
            },
            {
                "role": "user",
                "content": f"[{context.capitalize()}] {prompt}"
            }
        ],
        "max_tokens": 600,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(API_URL, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"].strip()
        else:
            return "⚠️ Unexpected API response format"
            
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            return "⚠️ Rate limit exceeded. Please try again in a moment."
        elif e.response.status_code == 401:
            return "⚠️ Invalid API key. Please check your OpenRouter API key."
        elif e.response.status_code == 404:
            return "⚠️ Model not found. The free model may no longer be available."
        else:
            return f"⚠️ HTTP Error {e.response.status_code}: {str(e)}"
    except requests.exceptions.RequestException as e:
        return f"⚠️ Network Error: {str(e)}"
    except Exception as e:
        return f"⚠️ Unexpected error: {str(e)}"

# ===== App Interface =====
apply_styles()

# Initialize session state for button clicks
if 'analyze_clicked' not in st.session_state:
    st.session_state.analyze_clicked = False
if 'coach_clicked' not in st.session_state:
    st.session_state.coach_clicked = False

# Header
st.markdown("# 💬 Third Voice")
st.markdown("*Get a fresh perspective on your messages before you send them*")

# Context Selection
context = st.selectbox(
    "📍 **Message Context**",
    options=list(CONTEXTS.keys()),
    format_func=lambda x: f"{CONTEXTS[x]['icon']} {x.title()}"
)

# Message Input  
message = st.text_area(
    "✍️ **Your Message**",
    placeholder="Type the message you want to analyze or improve...",
    height=150
)

# Action Buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("🔍 Analyze", use_container_width=True, key="analyze_btn"):
        st.session_state.analyze_clicked = True
        st.session_state.coach_clicked = False
with col2:
    if st.button("✨ Improve", type="primary", use_container_width=True, key="coach_btn"):
        st.session_state.coach_clicked = True
        st.session_state.analyze_clicked = False

# Results Handling
if st.session_state.analyze_clicked or st.session_state.coach_clicked:
    if not message.strip():
        st.warning("Please enter a message first!")
    else:
        with st.spinner("Processing..."):
            result = call_openrouter_api(
                message, 
                context,
                analyze_mode=st.session_state.analyze_clicked
            )
        
        # Display Results  
        st.markdown(f"""
        <div style="border-left: 4px solid {CONTEXTS[context]['color']}; 
                    padding: 1rem; margin: 1rem 0; border-radius: 0 8px 8px 0">
            <strong>{'🔍 Analysis' if st.session_state.analyze_clicked else '✨ Improved Message'}:</strong><br>
            {result}
        </div>
        """, unsafe_allow_html=True)
        
        # Copy Button
        if st.button("📋 Copy to Clipboard", key="copy_btn", use_container_width=True):
            copy_to_clipboard(result)
            time.sleep(0.3)  # Helps Android processing
            
        # Selectable text fallback
        st.markdown(f"""
        <div class="copy-box">
            {result}
            <div class="copy-instruction">
                👆 Press and hold to select text
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Try Again", key="try_again", use_container_width=True):
            st.session_state.analyze_clicked = False
            st.session_state.coach_clicked = False
            st.rerun()

# Footer
st.markdown("---")
st.markdown("*Made with ❤️ for better communication*")
