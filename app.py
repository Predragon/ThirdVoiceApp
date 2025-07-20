"""
Third Voice - Complete Mobile Solution
With reliable copy functionality and selectable fallback
"""

import streamlit as st
import requests
from streamlit.components.v1 import html

# ===== Configuration =====
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = st.secrets.get("OPENROUTER_API_KEY")

CONTEXTS = {
    "general": {
        "color": "#5D9BFF",  # Calm blue
        "icon": "💙",
        "prompt": "Improve this message for clarity and kindness:"
    },
    "romantic": {
        "color": "#FF7EB9",  # Warm pink
        "icon": "❤️",
        "prompt": "Make this romantic message more loving:"
    },
    "workplace": {
        "color": "#6EE7B7",  # Professional green
        "icon": "💼",
        "prompt": "Rephrase this message professionally:"
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
    /* Mobile-optimized styles */
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
    }}
    
    /* Result card */
    .result-card {{
        border-radius: 12px;
        padding: 1.2rem;
        margin: 1rem 0;
        background-color: rgba(255,255,255,0.05);
        border-left: 6px solid {CONTEXTS["general"]["color"]};
    }}
    
    /* Copy feedback */
    .copy-success {{
        color: {CONTEXTS["general"]["color"]};
        font-size: 14px;
        text-align: center;
        margin: 8px 0;
    }}
    </style>
    """, unsafe_allow_html=True)

# ===== Clipboard Function =====
def copy_to_clipboard(text):
    """Universal copy solution with visual feedback"""
    copy_js = f"""
    <textarea id="tempCopy" style="opacity:0;">{text}</textarea>
    <script>
    let textarea = document.getElementById('tempCopy');
    textarea.select();
    try {{
        if(navigator.clipboard) {{
            navigator.clipboard.writeText(`{text}`)
                .then(() => {{
                    let success = document.createElement('div');
                    success.className = 'copy-success';
                    success.innerHTML = '✓ Copied to clipboard!';
                    textarea.parentNode.insertBefore(success, textarea.nextSibling);
                    setTimeout(() => success.remove(), 2000);
                }});
        }} else {{
            document.execCommand('copy');
            let success = document.createElement('div');
            success.className = 'copy-success';
            success.innerHTML = '✓ Copied! (Press menu → Paste)';
            textarea.parentNode.insertBefore(success, textarea.nextSibling);
            setTimeout(() => success.remove(), 2000);
        }}
    }} catch(e) {{
        let manual = document.createElement('div');
        manual.className = 'copy-success';
        manual.innerHTML = '⚠️ Press and hold text below to copy';
        textarea.parentNode.insertBefore(manual, textarea.nextSibling);
    }}
    textarea.remove();
    </script>
    """
    html(copy_js)

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
    height=150,
    key="input"
)

# 3. Action Buttons
col1, col2 = st.columns(2)
with col1:
    analyze_btn = st.button("🔍 Analyze", use_container_width=True)
with col2:
    coach_btn = st.button("✨ Improve", type="primary", use_container_width=True)

# 4. Results Display
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
                        "HTTP-Referer": "https://third-voice.streamlit.app",
                        "X-Title": "Third Voice Mobile"
                    },
                    json={
                        "model": "mistralai/mistral-7b-instruct:free",
                        "messages": [{
                            "role": "system",
                            "content": CONTEXTS[context]["prompt"]
                        },{
                            "role": "user", 
                            "content": user_input
                        }],
                        "temperature": 0.7,
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
                
                # Copy Button
                if st.button("📋 Copy to Clipboard", use_container_width=True):
                    copy_to_clipboard(result)
                
                # Selectable Fallback
                st.text_area("Select and copy:", 
                            value=result, 
                            height=200,
                            key="output_copy")
                
                st.button("🔄 Try Again", use_container_width=True)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.button("🔄 Try Again", use_container_width=True)

# Debug view (hidden)
if st.secrets.get("DEBUG", False):
    st.write("Last run:", datetime.datetime.now().strftime("%H:%M:%S"))
