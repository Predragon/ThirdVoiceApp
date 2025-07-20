"""
The Third Voice - Full Mobile Version
With robust API error handling
"""

import streamlit as st
import requests
import json

# ===== Configuration =====
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = st.secrets.get("OPENROUTER_API_KEY")  # Set in Streamlit Secrets

# Simplified prompts for mobile editing
PROMPTS = {
    "general": "Improve this message to be clearer and kinder:",
    "romantic": "Make this romantic message more loving:",
    "coparenting": "Rephrase this co-parenting message to be child-focused:",
    "workplace": "Make this professional message clearer:",
    "family": "Improve this family message with care:",
    "friend": "Help this friendship message sound supportive:"
}

# ===== Mobile UI Setup =====
st.set_page_config(
    page_title="Third Voice",
    layout="centered",
    initial_sidebar_state="collapsed"
)

def mobile_styles():
    st.markdown("""
    <style>
    /* Mobile-optimized styles */
    @media (max-width: 768px) {
        /* Larger touch targets */
        button, [data-testid="stTextInput"], textarea {
            min-height: 3em !important;
            font-size: 16px !important;
        }
        /* Full-width elements */
        .stButton button { width: 100% !important; }
        .stTextArea textarea { font-size: 18px !important; }
        /* Better spacing */
        .stTextArea { margin-bottom: 1rem; }
    }
    /* Error messages */
    .stAlert { font-size: 16px !important; }
    </style>
    """, unsafe_allow_html=True)

# ===== Robust API Function =====
def get_ai_response(message, context):
    """Improved API call with complete error handling"""
    try:
        if not API_KEY:
            st.error("API key missing - check settings")
            return None
            
        if not message.strip():
            st.error("Please enter a message")
            return None

        # Prepare the prompt
        system_prompt = PROMPTS.get(context, PROMPTS["general"])
        
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "HTTP-Referer": "https://third-voice.streamlit.app",
                "X-Title": "Third Voice Mobile"
            },
            json={
                "model": "mistralai/mistral-7b-instruct:free",  # More reliable free model
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.7,
                "max_tokens": 800,
            },
            timeout=25
        )

        # Check for HTTP errors
        response.raise_for_status()
        
        # Parse and validate response
        data = response.json()
        
        if not isinstance(data, dict):
            st.error("API returned invalid format")
            return None
            
        if "choices" not in data or not isinstance(data["choices"], list):
            st.error("API response missing choices")
            return None
            
        if len(data["choices"]) == 0:
            st.error("No responses in choices array")
            return None
            
        if "message" not in data["choices"][0]:
            st.error("Response missing message content")
            return None
            
        return data["choices"][0]["message"]["content"]
        
    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {str(e)}")
        return None
    except json.JSONDecodeError:
        st.error("Invalid API response format")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return None

# ===== App Interface =====
mobile_styles()
st.title("🎙️ Third Voice")

# Main tabs
tab1, tab2 = st.tabs(["📤 Improve Message", "📥 Analyze Message"])
context = st.selectbox("Select Relationship", list(PROMPTS.keys()))

with tab1:
    user_msg = st.text_area("Your Message:", height=120, key="user_msg")
    if st.button("Get Improved Version", type="primary"):
        if user_msg.strip():
            with st.spinner("Optimizing your message..."):
                result = get_ai_response(user_msg, context)
                if result:
                    st.text_area("Improved Message:", 
                               value=result, 
                               height=200,
                               key="improved_msg")
        else:
            st.warning("Please enter a message first")

with tab2:
    their_msg = st.text_area("Their Message:", height=120, key="their_msg")
    if st.button("Analyze Their Message"):
        if their_msg.strip():
            with st.spinner("Understanding their message..."):
                analysis = get_ai_response(their_msg, context)
                if analysis:
                    st.text_area("Message Analysis:", 
                               value=analysis, 
                               height=200,
                               key="analysis")
        else:
            st.warning("Please enter a message first")

# Debug section (collapsed by default)
with st.expander("⚙️ Connection Status", False):
    st.write("API Key:", "✅ Configured" if API_KEY else "❌ Missing")
    st.write("Last Response:", "Waiting..." if not st.session_state.get('last_response') else "Received")
