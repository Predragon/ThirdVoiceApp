"""
Third Voice - New Workflow Test
Mobile-optimized emotional interface
"""

import streamlit as st
import requests

# ===== Configuration =====
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = st.secrets.get("OPENROUTER_API_KEY")

# Emotional context colors
CONTEXT_COLORS = {
    "general": "#5D9BFF",  # Calm blue
    "romantic": "#FF7EB9", # Warm pink
    "workplace": "#6EE7B7" # Professional green
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
    /* Mobile-first base */
    div.stTextArea > textarea {{
        font-size: 18px !important;
        min-height: 150px !important;
    }}
    div.stButton > button {{
        width: 100%;
        padding: 12px !important;
    }}
    
    /* Dynamic context coloring */
    .context-card {{
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        background-color: rgba(255,255,255,0.1);
        border-left: 6px solid {CONTEXT_COLORS["general"]};
    }}
    </style>
    """, unsafe_allow_html=True)

# ===== New Workflow =====
apply_styles()

# 1. Relationship Selector (Top)
context = st.selectbox(
    "Select relationship:",
    options=list(CONTEXT_COLORS.keys()),
    format_func=lambda x: {
        "general": "💙 General",
        "romantic": "❤️ Romantic",
        "workplace": "💼 Workplace"
    }[x]
)

# Dynamic color injection
st.markdown(f"""
<script>
document.documentElement.style.setProperty('--context-color', '{CONTEXT_COLORS[context]}');
</script>
""", unsafe_allow_html=True)

# 2. Central Input Area
user_input = st.text_area(
    "Your message:",
    placeholder="Type or paste here...",
    key="input",
    height=150
)

# 3. Action Toggle (Bottom Bar)
col1, col2 = st.columns(2)
with col1:
    analyze_mode = st.button("🔍 Analyze", use_container_width=True)
with col2:
    coach_mode = st.button("✨ Improve", use_container_width=True, type="primary")

# 4. Processing & Results
if analyze_mode or coach_mode:
    if not user_input.strip():
        st.warning("Please enter a message first")
    else:
        with st.spinner("Thinking..."):
            try:
                # Simple API call
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
                            "content": "Analyze the emotions in this message:" if analyze_mode 
                                      else "Improve this message for clarity and kindness:"
                        },{
                            "role": "user",
                            "content": f"[{context.capitalize()} context] {user_input}"
                        }],
                        "max_tokens": 500
                    },
                    timeout=20
                )
                
                result = response.json()["choices"][0]["message"]["content"]
                
                # Display with context card
                st.markdown(f"""
                <div class="context-card" style="border-color: {CONTEXT_COLORS[context]}">
                    <strong>🎙️ Result:</strong><br>
                    {result}
                </div>
                """, unsafe_allow_html=True)
                
                # Action buttons
                st.button("📋 Copy to Clipboard")
                st.button("🔄 Try Again")
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
