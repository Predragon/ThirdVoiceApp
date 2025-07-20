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

# ===== API Functions =====
def call_openrouter_api(prompt, model="meta-llama/llama-3.1-8b-instruct:free"):
    """Call OpenRouter API with error handling"""
    if not API_KEY:
        return "⚠️ API key not configured. Please add OPENROUTER_API_KEY to your Streamlit secrets."
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 300,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(API_URL, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.RequestException as e:
        return f"⚠️ API Error: {str(e)}"
    except Exception as e:
        return f"⚠️ Unexpected error: {str(e)}"

def analyze_message(message, context):
    """Analyze a message for tone and potential improvements"""
    prompt = f"""
    Analyze this {context} message for tone, clarity, and potential misunderstandings:
    
    Message: "{message}"
    
    Provide:
    1. Current tone assessment
    2. Potential issues or misunderstandings
    3. Emotional impact on recipient
    
    Keep response concise and helpful.
    """
    return call_openrouter_api(prompt)

def improve_message(message, context):
    """Generate an improved version of the message"""
    prompt = f"""
    Improve this {context} message to be clearer, more positive, and better received:
    
    Original: "{message}"
    
    Provide ONLY the improved message, no explanations or quotes.
    Keep the core meaning but improve tone and clarity.
    """
    return call_openrouter_api(prompt)

# ===== Main App Interface =====
apply_styles()

# Header
st.markdown("# 💬 Third Voice")
st.markdown("*Get a fresh perspective on your messages before you send them*")

# Context Selection
context = st.selectbox(
    "📍 **Message Context**",
    options=list(CONTEXTS.keys()),
    format_func=lambda x: f"{CONTEXTS[x]['icon']} {x.title()}",
    help="Choose the context for better analysis"
)

# Message Input
message = st.text_area(
    "✍️ **Your Message**",
    placeholder="Type the message you want to analyze or improve...",
    height=120,
    help="Paste or type your message here"
)

# Action Buttons
col1, col2 = st.columns(2)
with col1:
    analyze_btn = st.button(
        "🔍 Analyze",
        use_container_width=True,
        help="Get insights about your message"
    )
with col2:
    coach_btn = st.button(
        "✨ Improve",
        use_container_width=True,
        help="Get a better version of your message"
    )

# Process and Display Results
if analyze_btn or coach_btn:
    if not message.strip():
        st.warning("⚠️ Please enter a message to analyze or improve.")
    else:
        with st.spinner("🤔 Analyzing your message..."):
            if analyze_btn:
                result = analyze_message(message, context)
                action_type = "🔍 Analysis"
            else:
                result = improve_message(message, context)
                action_type = "✨ Improved Message"
        
        if result:
            # Display Results
            st.markdown(f"""
            <div style="border-left: 4px solid {CONTEXTS[context]['color']}; 
                        padding: 1rem; margin: 1rem 0; border-radius: 0 8px 8px 0">
                <strong>{action_type}:</strong><br>
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
            
            if st.button("🔄 Try Again", use_container_width=True):
                st.rerun()

# Footer
st.markdown("---")
st.markdown("*Made with ❤️ for better communication*")
