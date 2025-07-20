"""
Third Voice - Mobile-Optimized MVP with Model Selection
Fixed context buttons, streamlined help, mobile-first design, multiple AI models
"""

import streamlit as st
import requests
import json
from datetime import datetime
import base64

# ===== Configuration =====
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = st.secrets.get("OPENROUTER_API_KEY")

# AI Models Configuration
AI_MODELS = [
    {
        "id": "google/gemma-2-9b-it:free",
        "name": "Gemma 2 9B (Free)",
        "description": "Google's efficient model, good balance of speed and quality"
    },
    {
        "id": "meta-llama/llama-3.2-3b-instruct:free", 
        "name": "Llama 3.2 3B (Free)",
        "description": "Meta's compact model, fast responses"
    },
    {
        "id": "microsoft/phi-3-mini-128k-instruct:free",
        "name": "Phi-3 Mini (Free)",
        "description": "Microsoft's small but capable model with large context"
    }
]

CONTEXTS = {
    "general": {
        "color": "#5D9BFF", 
        "icon": "💙",
        "description": "Everyday conversations and general communication"
    },
    "romantic": {
        "color": "#FF7EB9", 
        "icon": "❤️",
        "description": "Personal relationships and intimate conversations"
    },
    "workplace": {
        "color": "#6EE7B7", 
        "icon": "💼",
        "description": "Professional communication and work-related messages"
    },
    "family": {
        "color": "#FFB347", 
        "icon": "👨‍👩‍👧‍👦",
        "description": "Family conversations and sensitive discussions"
    },
    "coparenting": {
        "color": "#9B59B6", 
        "icon": "👶",
        "description": "Co-parenting communication focused on child welfare"
    }
}

# ===== Mobile-First UI Setup =====
st.set_page_config(
    page_title="Third Voice - Message Helper",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

def apply_mobile_styles():
    st.markdown("""
    <style>
    /* Mobile-first responsive design */
    div.stTextArea > textarea {
        font-size: 16px !important;
        min-height: 120px !important;
        border-radius: 12px !important;
        border: 2px solid #e0e0e0 !important;
        padding: 16px !important;
    }
    
    div.stTextArea > textarea:focus {
        border-color: #5D9BFF !important;
        box-shadow: 0 0 0 3px rgba(93, 155, 255, 0.1) !important;
    }
    
    /* Enhanced button styling for better mobile feedback */
    div.stButton > button {
        border-radius: 12px !important;
        padding: 16px 24px !important;
        font-weight: 600 !important;
        min-height: 56px !important;
        font-size: 16px !important;
        margin-bottom: 12px !important;
        transition: all 0.2s ease !important;
        border: 2px solid transparent !important;
        width: 100% !important;
    }
    
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #5D9BFF 0%, #4A90E2 100%) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(93, 155, 255, 0.3) !important;
    }
    
    div.stButton > button[kind="secondary"] {
        background: white !important;
        color: #5D9BFF !important;
        border: 2px solid #5D9BFF !important;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(0,0,0,0.15) !important;
    }
    
    div.stButton > button:active {
        transform: translateY(0px) !important;
    }
    
    .result-container {
        border-radius: 16px;
        padding: 20px;
        margin: 16px 0;
        box-shadow: 0 2px 16px rgba(0,0,0,0.1);
        background: white;
    }
    
    .analysis-result {
        border-left: 4px solid #5D9BFF;
        background: linear-gradient(135deg, #f8fbff 0%, #e8f4ff 100%);
    }
    
    .improvement-result {
        border-left: 4px solid #10B981;
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    }
    
    .selectable-text {
        border: 2px dashed #d1d5db;
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
        background: #f9fafb;
        font-family: inherit;
        line-height: 1.6;
        user-select: text;
        -webkit-user-select: text;
        -moz-user-select: text;
        -ms-user-select: text;
        font-size: 16px;
    }
    
    .char-counter {
        font-size: 12px;
        color: #6b7280;
        text-align: right;
        margin-top: 4px;
    }
    
    .char-counter.warning { color: #f59e0b; }
    .char-counter.error { color: #ef4444; }
    
    .model-info {
        background: rgba(124, 58, 237, 0.1);
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        border-left: 3px solid #7c3aed;
    }
    
    @media (max-width: 768px) {
        .result-container {
            margin: 12px 0 !important;
            padding: 16px !important;
        }
        
        .selectable-text {
            font-size: 16px !important;
            padding: 20px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# ===== Session State Management =====
def init_state():
    defaults = {
        'selected_context': 'general',
        'selected_model': AI_MODELS[0]["id"],  # Default to first model
        'message_history': [],
        'current_result': None,
        'current_action': None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ===== History Management =====
def add_to_history(original, result, action, context, model):
    item = {
        'timestamp': datetime.now().isoformat(),
        'original': original,
        'result': result,
        'action': action,
        'context': context,
        'model': model
    }
    st.session_state.message_history.insert(0, item)
    if len(st.session_state.message_history) > 50:
        st.session_state.message_history = st.session_state.message_history[:50]

def download_history():
    if not st.session_state.message_history:
        return None
    
    history_data = {
        'exported_date': datetime.now().isoformat(),
        'total_items': len(st.session_state.message_history),
        'history': st.session_state.message_history
    }
    
    json_str = json.dumps(history_data, indent=2, ensure_ascii=False)
    b64 = base64.b64encode(json_str.encode()).decode()
    
    filename = f"third_voice_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    return f'<a href="data:application/json;base64,{b64}" download="{filename}" style="text-decoration:none"><button style="background:#10B981;color:white;border:none;padding:8px 16px;border-radius:8px;cursor:pointer;">📥 Download History</button></a>'

def upload_history(uploaded_file):
    try:
        history_data = json.load(uploaded_file)
        if 'history' in history_data and isinstance(history_data['history'], list):
            st.session_state.message_history = history_data['history']
            return True, f"✅ Loaded {len(history_data['history'])} items"
        else:
            return False, "❌ Invalid file format"
    except Exception as e:
        return False, f"❌ Error loading file: {str(e)}"

# ===== Enhanced API Functions =====
def get_system_prompt(action, context):
    prompts = {
        'analyze': {
            'general': "Analyze the emotional tone and underlying message. What might the sender really be feeling or needing? Help the user understand what's behind these words.",
            'romantic': "Analyze this message from a romantic partner. What emotions, needs, or concerns might be underneath their words? Help the user respond with empathy.",
            'workplace': "Analyze this professional message for hidden concerns, stress, or workplace dynamics. What might be driving this communication?",
            'family': "Analyze this family message for underlying emotions, generational patterns, or family dynamics. What deeper feelings might be expressed?",
            'coparenting': "Analyze this co-parenting message focusing on what emotions or concerns about the children might be underneath their words."
        },
        'improve': {
            'general': "Improve this response to be more understanding, clear, and healing. Transform potential conflict into connection.",
            'romantic': "Improve this message to be more loving, understanding, and emotionally connecting. Help heal instead of hurt.",
            'workplace': "Improve this response to be professional, constructive, and solution-focused while acknowledging concerns.",
            'family': "Improve this message to strengthen family bonds, show understanding, and promote healing.",
            'coparenting': "Improve this message to be child-focused, respectful, neutral, and solution-oriented. Reduce conflict, increase cooperation."
        }
    }
    return prompts[action].get(context, prompts[action]['general'])

def call_api(message, action, context, model_id):
    try:
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "HTTP-Referer": "https://third-voice.streamlit.app",
                "Content-Type": "application/json"
            },
            json={
                "model": model_id,
                "messages": [
                    {"role": "system", "content": get_system_prompt(action, context)},
                    {"role": "user", "content": f"Context: {context.capitalize()}\nMessage: {message}"}
                ],
                "max_tokens": 800,
                "temperature": 0.7
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"], None
        else:
            return None, f"API Error: {response.status_code}"
            
    except requests.exceptions.Timeout:
        return None, "Request timed out. Please try again."
    except Exception as e:
        return None, f"Error: {str(e)}"

def get_model_name(model_id):
    for model in AI_MODELS:
        if model["id"] == model_id:
            return model["name"]
    return model_id

# ===== Main App =====
def main():
    init_state()
    apply_mobile_styles()
    
    # Header
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="color: #1f2937; font-size: 2.5rem; margin-bottom: 8px;">💬 Third Voice</h1>
        <p style="color: #6b7280; font-size: 1.1rem;">Your AI communication assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Model Selection
    st.markdown("### 🤖 Choose your AI model:")
    
    for model in AI_MODELS:
        button_style = "primary" if st.session_state.selected_model == model["id"] else "secondary"
        if st.button(
            f"🧠 {model['name']}",
            key=f"model_{model['id']}",
            use_container_width=True,
            type=button_style
        ):
            st.session_state.selected_model = model["id"]
            # Clear any previous results when model changes
            st.session_state.current_result = None
            st.session_state.current_action = None
    
    # Model description
    selected_model = next((m for m in AI_MODELS if m["id"] == st.session_state.selected_model), AI_MODELS[0])
    st.markdown(f"""
    <div class="model-info">
        <small style="color: #4b5563;"><strong>🧠 {selected_model['name']}:</strong> {selected_model['description']}</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Context Selection - Mobile Optimized
    st.markdown("### 🎯 Choose your context:")
    
    for key, info in CONTEXTS.items():
        button_style = "primary" if st.session_state.selected_context == key else "secondary"
        if st.button(
            f"{info['icon']} {key.capitalize()}",
            key=f"context_{key}",
            use_container_width=True,
            type=button_style
        ):
            st.session_state.selected_context = key
            # Clear any previous results when context changes
            st.session_state.current_result = None
            st.session_state.current_action = None
    
    # Context description
    selected_info = CONTEXTS[st.session_state.selected_context]
    st.markdown(f"""
    <div style="background: rgba(93, 155, 255, 0.1); border-radius: 8px; padding: 12px; margin: 16px 0;">
        <small style="color: #4b5563;"><strong>{selected_info['icon']} {st.session_state.selected_context.capitalize()}:</strong> {selected_info['description']}</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Message Input
    st.markdown("### ✍️ Your message:")
    user_input = st.text_area(
        "",
        placeholder="Paste the message you received or write your response here...",
        height=150,
        label_visibility="collapsed",
        key="message_input"
    )
    
    # Character counter
    char_count = len(user_input)
    counter_class = "error" if char_count > 2000 else "warning" if char_count > 1500 else ""
    st.markdown(f"""
    <div class="char-counter {counter_class}">
        {char_count}/2000 characters
    </div>
    """, unsafe_allow_html=True)
    
    # Action Buttons - Mobile Optimized
    st.markdown("### 🚀 Choose action:")
    
    # Check if we have valid input
    has_valid_input = user_input.strip() and char_count <= 2000
    
    col1, col2 = st.columns(2)
    
    with col1:
        analyze_clicked = st.button(
            "🔍 Analyze Their Message",
            use_container_width=True,
            disabled=not has_valid_input,
            help="Understand the real emotions behind their words",
            key="analyze_btn"
        )
    
    with col2:
        improve_clicked = st.button(
            "✨ Improve My Response", 
            type="primary",
            use_container_width=True,
            disabled=not has_valid_input,
            help="Get a better version that heals instead of hurts",
            key="improve_btn"
        )
    
    # Process button clicks
    if analyze_clicked and has_valid_input:
        with st.spinner(f"🤔 {selected_model['name']} is analyzing..."):
            result, error = call_api(user_input, "analyze", st.session_state.selected_context, st.session_state.selected_model)
        
        if error:
            st.error(f"❌ {error}")
        else:
            st.session_state.current_result = result
            st.session_state.current_action = "analyze"
            add_to_history(user_input, result, "analyze", st.session_state.selected_context, st.session_state.selected_model)
    
    elif improve_clicked and has_valid_input:
        with st.spinner(f"🤔 {selected_model['name']} is improving..."):
            result, error = call_api(user_input, "improve", st.session_state.selected_context, st.session_state.selected_model)
        
        if error:
            st.error(f"❌ {error}")
        else:
            st.session_state.current_result = result
            st.session_state.current_action = "improve"
            add_to_history(user_input, result, "improve", st.session_state.selected_context, st.session_state.selected_model)
    
    # Show warning if no valid input
    elif (analyze_clicked or improve_clicked) and not has_valid_input:
        if not user_input.strip():
            st.warning("⚠️ Please enter a message to analyze or improve.")
        elif char_count > 2000:
            st.warning("⚠️ Message too long. Please keep it under 2000 characters.")
    
    # Display current result if exists
    if st.session_state.current_result and st.session_state.current_action:
        result = st.session_state.current_result
        action = st.session_state.current_action
        
        # Display result
        result_class = "analysis-result" if action == "analyze" else "improvement-result"
        action_icon = "🔍" if action == "analyze" else "✨"
        action_title = "Message Analysis" if action == "analyze" else "Improved Response"
        
        st.markdown(f"""
        <div class="result-container {result_class}">
            <h4 style="margin-top: 0; color: #1f2937;">{action_icon} {action_title}</h4>
            <div style="font-size: 12px; color: #6b7280; margin-bottom: 12px;">Generated by: {selected_model['name']}</div>
            <div style="line-height: 1.6; color: #374151;">{result}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Mobile-optimized selectable text
        st.markdown("### 📱 Tap to select and copy:")
        st.markdown(f"""
        <div class="selectable-text">
            {result}
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Clear Result", use_container_width=True):
            st.session_state.current_result = None
            st.session_state.current_action = None
            st.rerun()
    
    # History Management Section
    st.markdown("---")
    st.markdown("### 📚 History Management")
    
    hist_cols = st.columns([1, 1])
    
    with hist_cols[0]:
        # Download History
        if st.session_state.message_history:
            download_link = download_history()
            if download_link:
                st.markdown(download_link, unsafe_allow_html=True)
        else:
            st.button("📥 Download", disabled=True, help="No history to download")
    
    with hist_cols[1]:
        # Upload History
        if st.button("📤 Upload History", use_container_width=True):
            st.session_state.show_upload = not getattr(st.session_state, 'show_upload', False)
    
    # Upload interface
    if getattr(st.session_state, 'show_upload', False):
        uploaded_file = st.file_uploader(
            "Choose history file",
            type=['json'],
            key="history_upload"
        )
        
        if uploaded_file:
            success, message = upload_history(uploaded_file)
            if success:
                st.success(message)
                st.session_state.show_upload = False
                st.rerun()
            else:
                st.error(message)
    
    # Show History
    if st.session_state.message_history:
        with st.expander(f"📖 Recent History ({len(st.session_state.message_history)} items)", expanded=False):
            for i, item in enumerate(st.session_state.message_history[:10]):
                action_icon = "🔍" if item['action'] == "analyze" else "✨"
                context_info = CONTEXTS[item['context']]
                timestamp = datetime.fromisoformat(item['timestamp']).strftime("%m/%d %H:%M")
                model_name = get_model_name(item.get('model', 'Unknown'))
                
                st.markdown(f"""
                <div style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; margin: 8px 0; background: #f9fafb;">
                    <div style="font-size: 14px; color: #6b7280; margin-bottom: 8px;">
                        {action_icon} {timestamp} - {context_info['icon']} {item['context'].capitalize()} - 🧠 {model_name}
                    </div>
                    <div style="font-size: 13px; color: #374151; margin-bottom: 8px;">
                        <strong>Original:</strong> {item['original'][:100]}{'...' if len(item['original']) > 100 else ''}
                    </div>
                    <div style="font-size: 13px; color: #374151;">
                        <strong>Result:</strong> {item['result'][:150]}{'...' if len(item['result']) > 150 else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6b7280; font-size: 14px; padding: 20px 0;">
        💡 <strong>Tip:</strong> Try different AI models to see which works best for your communication style!<br>
        Analyze their message first to understand their emotions, then improve your response!<br>
        Made with ❤️ for better human connections
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
