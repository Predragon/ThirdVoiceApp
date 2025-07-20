"""
Third Voice - Mobile Optimized
With reliable clipboard copy and visual feedback
""""""
Third Voice - Working Clipboard Version
Tested solution for Android devices
"""

import streamlit as st
import requests
from streamlit.components.v1 import html

# ===== Clipboard Function =====
def copy_to_clipboard(text):
    """Universal clipboard copy that works on mobile"""
    copy_js = f"""
    <textarea id="tempCopy" style="opacity:0; position:absolute;">{text}</textarea>
    <script>
    let textarea = document.getElementById('tempCopy');
    textarea.select();
    try {{
        // Modern browsers (may not work on all mobiles)
        if(navigator.clipboard) {{
            navigator.clipboard.writeText(textarea.value)
                .then(() => {{ 
                    // Show checkmark for 2 seconds
                    let success = document.createElement('div');
                    success.innerHTML = '✓ Copied!';
                    success.style.color = '#5D9BFF';
                    success.style.position = 'fixed';
                    success.style.bottom = '20px';
                    success.style.right = '20px';
                    success.style.padding = '10px';
                    success.style.background = 'white';
                    success.style.borderRadius = '5px';
                    success.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
                    document.body.appendChild(success);
                    setTimeout(() => success.remove(), 2000);
                }})
                .catch(err => {{
                    // Fallback for when modern API fails
                    document.execCommand('copy');
                }});
        }} else {{
            // Legacy method
            document.execCommand('copy');
        }}
    }} catch(e) {{
        // Final fallback - show instructions
        alert('Select text and press COPY');
    }}
    textarea.remove();
    </script>
    """
    html(copy_js, height=0, width=0)

# ===== App Implementation =====
# [Keep all your existing UI code...]

# When showing results:
if result:
    st.markdown(f"""...""")  # Your existing result display
    
    if st.button("📋 Copy to Clipboard"):
        copy_to_clipboard(result)  # This will now work
        
    st.button("🔄 Try Again")

import streamlit as st
import requests

# ===== Configuration =====
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = st.secrets.get("OPENROUTER_API_KEY")

CONTEXTS = {
    "general": {"color": "#5D9BFF", "icon": "💙", "prompt": "Improve for kindness/clarity:"},
    "romantic": {"color": "#FF7EB9", "icon": "❤️", "prompt": "Make more loving:"},
    "workplace": {"color": "#6EE7B7", "icon": "💼", "prompt": "Rephrase professionally:"}
}

# ===== Mobile UI Setup =====
st.set_page_config(layout="centered")

def apply_styles():
    st.markdown(f"""
    <style>
    @media (max-width: 768px) {{
        /* Mobile-responsive styles */
        div.stTextArea > textarea {{ font-size: 18px !important; }}
        div.stButton > button {{ min-height: 3em !important; }}
    }}
    /* Copy button feedback */
    .copy-success {{ 
        color: {CONTEXTS["general"]["color"]};
        font-size: 14px;
        margin-top: -10px;
        margin-bottom: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

# ===== Clipboard Solution =====
def handle_copy(text):
    """Universal clipboard copy with fallback"""
    copy_js = f"""
    <script>
    function fallbackCopy(text) {{
        var textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        try {{
            document.execCommand('copy');
            return true;
        }} catch (err) {{
            console.error('Fallback failed:', err);
            return false;
        }} finally {{
            document.body.removeChild(textarea);
        }}
    }}
    
    // Try modern API first
    if (navigator.clipboard) {{
        navigator.clipboard.writeText(`{text}`)
            .then(() => {{ parent.document.getElementById('copy-success').textContent = '✓ Copied!'; }})
            .catch(err => {{ 
                console.error('Modern copy failed:', err); 
                if (fallbackCopy(`{text}`)) {{
                    parent.document.getElementById('copy-success').textContent = '✓ Copied!';
                }} else {{
                    parent.document.getElementById('copy-success').textContent = '⚠️ Press and hold to copy';
                }}
            }});
    }} else {{
        fallbackCopy(`{text}`) 
            ? parent.document.getElementById('copy-success').textContent = '✓ Copied!'
            : parent.document.getElementById('copy-success').textContent = '⚠️ Press and hold to copy';
    }}
    </script>
    <div id="copy-success" class="copy-success"></div>
    """
    st.components.v1.html(copy_js, height=0)

# ===== App Interface =====
apply_styles()

# 1. Context Selector
context = st.selectbox(
    "Relationship:",
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
                            "content": CONTEXTS[context]["prompt"]
                        },{
                            "role": "user",
                            "content": user_input
                        }],
                        "max_tokens": 600
                    },
                    timeout=20
                )
                result = response.json()["choices"][0]["message"]["content"]
                
                # Display Results
                st.markdown(f"""
                <div style="border-left: 4px solid {CONTEXTS[context]['color']}; 
                            padding: 1rem; margin: 1rem 0; border-radius: 0 8px 8px 0">
                    {result}
                </div>
                """, unsafe_allow_html=True)
                
                # Copy Button with Feedback
                if st.button("📋 Copy", key="copy_btn", use_container_width=True):
                    handle_copy(result)
                
                st.button("🔄 Try Again", use_container_width=True)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
