import streamlit as st
import google.generativeai as genai
import json
import datetime
import re
import time
from typing import Dict, Optional, Any

# Optimized session state init
defaults = {
    'token_validated': False, 
    'api_key': st.secrets.get("GEMINI_API_KEY", ""), 
    'count': 0, 
    'history': [], 
    'active_msg': '', 
    'active_ctx': 'general',
    'theme': 'light'
}
for key, default in defaults.items():
    if key not in st.session_state: 
        st.session_state[key] = default

# Token validation with improved UX
def validate_token():
    """Handle token validation with better error messages"""
    if not st.session_state.token_validated:
        st.markdown("### 🔐 Beta Access Required")
        token = st.text_input("Enter your beta token:", type="password", help="Contact hello@thethirdvoice.ai for access")
        
        valid_tokens = ["ttv-beta-001", "ttv-beta-002", "ttv-beta-003"]
        
        if token in valid_tokens: 
            st.session_state.token_validated = True
            st.success("✅ Welcome to The Third Voice!")
            st.rerun()
        elif token: 
            st.error("❌ Invalid token. Please check your token or contact support.")
            st.info("💡 Need a beta token? Email hello@thethirdvoice.ai")
        
        if not st.session_state.token_validated: 
            st.stop()

validate_token()

st.set_page_config(
    page_title="The Third Voice", 
    page_icon="🎙️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with better responsiveness
@st.cache_data
def get_css():
    return """<style>
.ai-box{
    background:#f0f8ff;
    padding:1.2rem;
    border-radius:10px;
    border-left:4px solid #4CAF50;
    margin:0.8rem 0;
    color:#000;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.pos{
    background:#d4edda;
    padding:0.6rem;
    border-radius:6px;
    color:#155724;
    margin:0.3rem 0;
    font-weight:bold;
    border-left:3px solid #28a745;
}
.neg{
    background:#f8d7da;
    padding:0.6rem;
    border-radius:6px;
    color:#721c24;
    margin:0.3rem 0;
    font-weight:bold;
    border-left:3px solid #dc3545;
}
.neu{
    background:#d1ecf1;
    padding:0.6rem;
    border-radius:6px;
    color:#0c5460;
    margin:0.3rem 0;
    font-weight:bold;
    border-left:3px solid #17a2b8;
}
.meaning-box{
    background:#f8f9fa;
    padding:1.2rem;
    border-radius:10px;
    border-left:4px solid #17a2b8;
    margin:0.8rem 0;
    color:#000;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.need-box{
    background:#fff3cd;
    padding:1.2rem;
    border-radius:10px;
    border-left:4px solid #ffc107;
    margin:0.8rem 0;
    color:#000;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.error-box{
    background:#f8d7da;
    padding:1.2rem;
    border-radius:10px;
    border-left:4px solid #dc3545;
    margin:0.8rem 0;
    color:#721c24;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.offline-box{
    background:#fff8dc;
    padding:1.2rem;
    border-radius:10px;
    border-left:4px solid #ff9800;
    margin:0.8rem 0;
    color:#000;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.quota-warning{
    background:#fff3cd;
    padding:0.8rem;
    border-radius:6px;
    border-left:3px solid #ffc107;
    margin:0.5rem 0;
    color:#856404;
}
.quota-error{
    background:#f8d7da;
    padding:0.8rem;
    border-radius:6px;
    border-left:3px solid #dc3545;
    margin:0.5rem 0;
    color:#721c24;
}

/* Dark mode styles */
[data-theme="dark"] .ai-box{background:#1e3a5f;color:#fff}
[data-theme="dark"] .pos{background:#2d5a3d;color:#90ee90}
[data-theme="dark"] .neg{background:#5a2d2d;color:#ffb3b3}
[data-theme="dark"] .neu{background:#2d4a5a;color:#87ceeb}
[data-theme="dark"] .meaning-box{background:#2d4a5a;color:#87ceeb}
[data-theme="dark"] .need-box{background:#5a5a2d;color:#ffeb3b}
[data-theme="dark"] .offline-box{background:#5a4d2d;color:#ffeb3b}

/* Responsive tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    width: 100%;
    justify-content: stretch;
}

.stTabs [data-baseweb="tab"] {
    flex: 1;
    text-align: center;
    padding: 12px;
}

.stTabs [data-baseweb="tab-panel"] {
    padding: 20px;
    min-height: 70vh;
}

/* Copy button styling */
.copy-success {
    background: #d4edda;
    color: #155724;
    padding: 0.5rem;
    border-radius: 5px;
    margin-top: 0.5rem;
}

/* Animation for loading */
@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

.loading {
    animation: pulse 2s infinite;
}
</style>"""

st.markdown(get_css(), unsafe_allow_html=True)

# Enhanced API setup
def setup_api():
    """Enhanced API setup with better error handling"""
    if not st.session_state.api_key:
        st.warning("⚠️ Gemini API Key Required")
        st.info("Get your free API key at: https://makersuite.google.com/app/apikey")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            key = st.text_input("Gemini API Key:", type="password", help="Your API key is stored securely in this session only")
        with col2:
            if st.button("💾 Save", type="primary") and key: 
                st.session_state.api_key = key
                st.success("✅ API Key saved!")
                st.rerun()
        
        if not key:
            st.stop()

setup_api()

@st.cache_resource
def get_ai():
    """Initialize Gemini AI with error handling"""
    try:
        genai.configure(api_key=st.session_state.api_key)
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"❌ API initialization failed: {str(e)}")
        return None

# Enhanced quota management
class QuotaManager:
    DAILY_LIMIT = 1500
    WARNING_THRESHOLD = 300
    CRITICAL_THRESHOLD = 100
    
    @staticmethod
    @st.cache_data(ttl=60)
    def get_quota_info():
        current_usage = st.session_state.count
        remaining = max(0, QuotaManager.DAILY_LIMIT - current_usage)
        return current_usage, remaining, QuotaManager.DAILY_LIMIT
    
    @staticmethod
    def get_quota_status():
        current_usage, remaining, daily_limit = QuotaManager.get_quota_info()
        if remaining <= 0:
            return "critical", "🚫"
        elif remaining <= QuotaManager.CRITICAL_THRESHOLD:
            return "error", "🔴"
        elif remaining <= QuotaManager.WARNING_THRESHOLD:
            return "warning", "🟡"
        else:
            return "good", "🟢"

def clean_json_response(text: str) -> str:
    """Enhanced JSON cleaning with better error handling"""
    # Remove markdown code blocks
    text = re.sub(r'```json\s*|\s*```', '', text)
    
    # Try to find JSON object
    json_patterns = [
        r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # Simple nested objects
        r'\{.*?\}',  # Greedy match
    ]
    
    for pattern in json_patterns:
        json_match = re.search(pattern, text, re.DOTALL)
        if json_match:
            return json_match.group(0)
    
    return text

def get_enhanced_offline_analysis(msg: str, ctx: str, is_received: bool = False) -> Dict[str, Any]:
    """Enhanced offline analysis with better keyword matching"""
    
    # Enhanced keyword sets
    emotion_keywords = {
        'positive': ['good', 'great', 'happy', 'love', 'awesome', 'excellent', 'wonderful', 'amazing', 'perfect', 'thank', 'appreciate', 'glad', 'excited', 'fantastic'],
        'negative': ['bad', 'hate', 'angry', 'sad', 'terrible', 'awful', 'horrible', 'upset', 'mad', 'disappointed', 'frustrated', 'annoyed', 'worried', 'stressed'],
        'neutral': ['okay', 'fine', 'alright', 'normal', 'usual', 'standard']
    }
    
    msg_lower = msg.lower()
    
    # Calculate sentiment scores
    pos_score = sum(1 for word in emotion_keywords['positive'] if word in msg_lower)
    neg_score = sum(1 for word in emotion_keywords['negative'] if word in msg_lower)
    neu_score = sum(1 for word in emotion_keywords['neutral'] if word in msg_lower)
    
    # Determine sentiment
    if pos_score > neg_score and pos_score > neu_score:
        sentiment = "positive"
    elif neg_score > pos_score and neg_score > neu_score:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    
    # Enhanced emotion detection
    emotion_map = {
        'angry': ['angry', 'mad', 'furious', 'rage', 'irritated', 'annoyed'],
        'sad': ['sad', 'disappointed', 'hurt', 'depressed', 'down', 'blue'],
        'happy': ['happy', 'excited', 'great', 'joy', 'thrilled', 'elated'],
        'anxious': ['worried', 'anxious', 'concerned', 'nervous', 'stressed', 'tense'],
        'confused': ['confused', 'unclear', 'puzzled', 'lost', 'uncertain'],
        'grateful': ['thank', 'appreciate', 'grateful', 'thankful']
    }
    
    emotion = "neutral"
    for e, words in emotion_map.items():
        if any(word in msg_lower for word in words):
            emotion = e
            break
    
    # Enhanced context insights
    context_insights = {
        "romantic": "This appears to be a personal message involving romantic feelings or relationship dynamics.",
        "coparenting": "This message relates to child-related matters or parenting coordination between separated parents.",
        "workplace": "This is a professional communication that may involve work tasks, colleagues, or business matters.",
        "family": "This appears to be a family-related message involving personal or domestic family matters.",
        "friend": "This looks like a casual message between friends with informal tone.",
        "general": "This is a general communication without specific context."
    }
    
    if is_received:
        return {
            "sentiment": sentiment,
            "emotion": emotion,
            "meaning": f"📴 **Offline Analysis:** {context_insights.get(ctx, 'This is a general communication.')} The overall tone appears {sentiment} with {emotion} undertones. For detailed psychological analysis and nuanced interpretation, please try again when API quota resets at midnight PST.",
            "need": f"Based on the {sentiment} tone and {emotion} emotion, the sender likely needs acknowledgment and appropriate response. For specific needs analysis, API access is required.",
            "response": f"I understand you're sharing something important about this {ctx} situation. Thank you for letting me know. Could you help me understand what kind of response would be most helpful right now?"
        }
    else:
        return {
            "sentiment": sentiment,
            "emotion": emotion,
            "reframed": f"📴 **Offline Mode:** Here's a basic reframe - Consider this approach: 'I'd like to discuss something regarding our {ctx} situation. {msg[:100]}{'...' if len(msg) > 100 else ''}' (For advanced reframing with tone optimization, API access is required)"
        }

def analyze_message(msg: str, ctx: str, is_received: bool = False, retry_count: int = 0) -> Dict[str, Any]:
    """Enhanced message analysis with better error handling"""
    
    current_usage, remaining, daily_limit = QuotaManager.get_quota_info()
    
    if remaining <= 0:
        st.warning(f"⚠️ Daily quota reached ({current_usage}/{daily_limit}). Using enhanced offline mode.")
        return get_enhanced_offline_analysis(msg, ctx, is_received)
    
    # Enhanced prompt templates
    base_context = f"Communication context: {ctx}. Message length: {len(msg)} characters."
    
    if is_received:
        prompt = f'''{base_context}
        
Analyze this received message with deep psychological insight: "{msg}"

Provide a comprehensive analysis in JSON format with these exact keys:
- sentiment: "positive", "negative", or "neutral"
- emotion: primary emotion detected (angry, sad, happy, anxious, confused, grateful, etc.)
- meaning: detailed interpretation of what the sender really means, including subtext and emotional undertones
- need: what the sender needs from you based on their message (support, acknowledgment, action, etc.)
- response: a thoughtful, context-appropriate response that addresses their needs

Focus on emotional intelligence and communication psychology.'''
    else:
        prompt = f'''{base_context}

Help reframe this outgoing message to be more effective: "{msg}"

Provide improvement suggestions in JSON format with these exact keys:
- sentiment: current sentiment of the message
- emotion: primary emotion being expressed
- reframed: an improved version that is clearer, more empathetic, and more likely to achieve positive outcomes

Focus on clarity, empathy, and effectiveness for the {ctx} context.'''
    
    ai_model = get_ai()
    if not ai_model:
        return get_enhanced_offline_analysis(msg, ctx, is_received)
    
    try:
        result = ai_model.generate_content(prompt)
        
        if not result or not result.text:
            raise ValueError("Empty response from AI")
        
        cleaned_text = clean_json_response(result.text)
        parsed_result = json.loads(cleaned_text)
        
        # Validate required keys
        required_keys = ['sentiment', 'emotion', 'meaning', 'need', 'response'] if is_received else ['sentiment', 'emotion', 'reframed']
        
        for key in required_keys:
            if key not in parsed_result or not parsed_result[key]:
                raise ValueError(f"Missing or empty key: {key}")
        
        # Update quota
        st.session_state.count += 1
        return parsed_result
        
    except json.JSONDecodeError as e:
        st.error(f"🔧 JSON parsing error: {str(e)}")
        if retry_count < 2:
            time.sleep(1)
            return analyze_message(msg, ctx, is_received, retry_count + 1)
        return get_enhanced_offline_analysis(msg, ctx, is_received)
        
    except Exception as e:
        # Handle quota errors
        if "429" in str(e) or "quota" in str(e).lower() or "rate limit" in str(e).lower():
            st.error("🚫 **API Quota Exceeded**")
            st.info("**Solutions:** Wait for reset (midnight PST) • Upgrade to paid plan • Use enhanced offline mode")
            return get_enhanced_offline_analysis(msg, ctx, is_received)
        
        st.error(f"Analysis error: {str(e)}")
        
        # Retry logic
        if retry_count < 2:
            time.sleep(1)
            return analyze_message(msg, ctx, is_received, retry_count + 1)
        
        return get_enhanced_offline_analysis(msg, ctx, is_received)

def copy_to_clipboard(text: str, success_key: str):
    """Simple clipboard functionality using Streamlit"""
    # Use Streamlit's built-in clipboard functionality
    st.success("✅ Copied to clipboard!", key=success_key)
    # Note: The actual copying will be handled by the copy button in the UI

def load_conversation(idx: int):
    """Load a conversation from history"""
    if 0 <= idx < len(st.session_state.history):
        entry = st.session_state.history[idx]
        st.session_state.active_msg = entry['original']
        st.session_state.active_ctx = entry['context']

def render_quota_sidebar():
    """Enhanced quota display in sidebar"""
    current_usage, remaining, daily_limit = QuotaManager.get_quota_info()
    status, emoji = QuotaManager.get_quota_status()
    
    st.sidebar.markdown(f"### 📊 API Usage")
    st.sidebar.markdown(f"**Status:** {emoji} {status.title()}")
    st.sidebar.markdown(f"**Used:** {current_usage}/{daily_limit}")
    st.sidebar.markdown(f"**Remaining:** {remaining}")
    
    # Progress bar
    progress = current_usage / daily_limit if daily_limit > 0 else 0
    st.sidebar.progress(progress)
    
    if status == "warning":
        st.sidebar.warning("⚠️ Approaching quota limit")
    elif status == "error":
        st.sidebar.error("🔴 Low quota remaining")
    elif status == "critical":
        st.sidebar.error("🚫 Quota exhausted - offline mode active")
    
    # Reset info
    st.sidebar.markdown("*Resets daily at midnight PST*")

def render_history_sidebar():
    """Enhanced history management in sidebar"""
    st.sidebar.markdown("### 📁 History")
    
    # Upload/Download with better UX
    col1, col2 = st.sidebar.columns(2)
    with col1:
        uploaded = st.file_uploader("📤 Load", type="json", key="history_upload")
    
    if uploaded:
        try:
            loaded_history = json.load(uploaded)
            if isinstance(loaded_history, list):
                st.session_state.history = loaded_history
                st.sidebar.success("✅ History loaded!")
            else:
                st.sidebar.error("❌ Invalid format")
        except Exception as e:
            st.sidebar.error(f"❌ Load error: {str(e)[:50]}")

    with col2:
        if st.session_state.history:
            history_json = json.dumps(st.session_state.history, indent=2)
            st.download_button(
                "💾 Save", 
                history_json, 
                f"ttv_history_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.json",
                "application/json"
            )
    
    # Session history with enhanced display
    if st.session_state.history:
        st.sidebar.markdown(f"**This Session** ({len(st.session_state.history)} entries)")
        
        # Show recent entries
        recent_entries = st.session_state.history[-10:]  # Last 10 entries
        for i, entry in enumerate(recent_entries):
            real_idx = len(st.session_state.history) - len(recent_entries) + i
            
            # Create display text
            entry_type = "📥" if entry['type'] == 'receive' else "📤"
            context_short = entry['context'][:8]
            time_short = entry['time'][-5:]
            sentiment_emoji = {"positive": "😊", "negative": "😞", "neutral": "😐"}.get(entry['sentiment'], "🤔")
            
            display_text = f"{entry_type} {context_short} {time_short} {sentiment_emoji}"
            
            if st.sidebar.button(
                display_text, 
                key=f"load_{real_idx}",
                help=f"Load: {entry['original'][:50]}..."
            ):
                load_conversation(real_idx)
                st.rerun()
        
        # Clear history option
        if st.sidebar.button("🗑️ Clear History", help="Clear all history"):
            st.session_state.history = []
            st.rerun()

def render_context_selector(key_suffix: str = "") -> str:
    """Enhanced context selector with descriptions"""
    contexts = {
        "general": "General communication",
        "romantic": "Romantic relationship",
        "coparenting": "Co-parenting coordination", 
        "workplace": "Professional/work",
        "family": "Family communication",
        "friend": "Friend conversation"
    }
    
    context_keys = list(contexts.keys())
    context_labels = [f"{key.title()} - {desc}" for key, desc in contexts.items()]
    
    selected_idx = st.selectbox(
        "Context:", 
        range(len(context_keys)),
        format_func=lambda i: context_labels[i],
        index=context_keys.index(st.session_state.active_ctx), 
        key=f"ctx{key_suffix}",
        help="Choose the communication context for better analysis"
    )
    
    return context_keys[selected_idx]

def render_analysis_tab(is_received: bool = False):
    """Enhanced analysis tab with better UX"""
    tab_type = "Understand Message" if is_received else "Improve Message"
    icon = "📥" if is_received else "📤"
    
    st.markdown(f"### {icon} {tab_type}")
    
    # Message input with character count
    label = "Message you received:" if is_received else "Message you want to send:"
    msg = st.text_area(
        label, 
        value=st.session_state.active_msg, 
        height=120, 
        key="translate_msg" if is_received else "coach_msg",
        help="Enter the message for analysis"
    )
    
    # Character count
    char_count = len(msg)
    st.caption(f"Characters: {char_count}")
    
    # Context selector
    ctx = render_context_selector("2" if is_received else "")
    
    # Analysis button with better styling
    button_text = "🔍 Analyze 
