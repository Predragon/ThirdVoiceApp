"""
The Third Voice AI - Combined Application
A revolutionary communication assistance platform built with love for families

Created by Predrag Mirković from detention, fighting to come home to Samantha 💖
"When both people are talking from pain, someone needs to be the third voice."
"""

import streamlit as st
import json
import datetime
import requests
from typing import Dict, Any, Optional, List

# =============================================
# Configuration and Constants
# =============================================

API_URL = "https://openrouter.ai/api/v1/chat/completions"
REQUIRE_TOKEN = False
VALID_TOKENS = ["ttv-beta-001", "ttv-beta-002", "ttv-beta-003"]
CONTEXTS = ["general", "romantic", "coparenting", "workplace", "family", "friend"]
AI_MODELS = [
    "google/gemma-2-9b-it:free",
    "meta-llama/llama-3.2-3b-instruct:free", 
    "microsoft/phi-3-mini-128k-instruct:free"
]

CSS_STYLES = """
<style>
.contact-card {
    background: rgba(76,175,80,0.1);
    padding: 0.8rem;
    border-radius: 8px;
    border-left: 4px solid #4CAF50;
    margin: 0.5rem 0;
    cursor: pointer;
}

.ai-response {
    background: rgba(76,175,80,0.1);
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #4CAF50;
    margin: 0.5rem 0;
}

.user-msg {
    background: rgba(33,150,243,0.1);
    padding: 0.8rem;
    border-radius: 8px;
    border-left: 4px solid #2196F3;
    margin: 0.3rem 0;
}

.contact-msg {
    background: rgba(255,193,7,0.1);
    padding: 0.8rem;
    border-radius: 8px;
    border-left: 4px solid #FFC107;
    margin: 0.3rem 0;
}

.pos {
    background: rgba(76,175,80,0.2);
    padding: 0.5rem;
    border-radius: 5px;
    margin: 0.2rem 0;
}

.neg {
    background: rgba(244,67,54,0.2);
    padding: 0.5rem;
    border-radius: 5px;
    margin: 0.2rem 0;
}

.neu {
    background: rgba(33,150,243,0.2);
    padding: 0.5rem;
    border-radius: 5px;
    margin: 0.2rem 0;
}

.journal-section {
    background: rgba(156,39,176,0.1);
    padding: 1rem;
    border-radius: 8px;
    margin: 0.5rem 0;
}

.main-actions {
    display: flex;
    gap: 1rem;
    margin: 1rem 0;
}

.main-actions button {
    flex: 1;
    padding: 0.8rem;
    font-size: 1.1rem;
}

.feedback-section {
    background: rgba(0,150,136,0.1);
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}

.stats-card {
    background: rgba(63,81,181,0.1);
    padding: 1rem;
    border-radius: 8px;
    margin: 0.5rem 0;
    text-align: center;
}
</style>
"""

def apply_styles():
    """Apply CSS styles to the app"""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)

def get_api_key():
    """Get API key from secrets or session state"""
    return st.secrets.get("OPENROUTER_API_KEY", st.session_state.get('api_key', ""))

# =============================================
# Prompts and AI Configuration
# =============================================

COACHING_PROMPTS = {
    "general": (
        "You are an emotionally intelligent communication coach. "
        "Help improve this message for clarity and empathy. "
        "Focus on being clear, kind, and constructive."
    ),
    
    "romantic": (
        "You help reframe romantic messages with empathy and clarity "
        "while maintaining intimacy. Preserve the love and connection "
        "while ensuring the message is received with care."
    ),
    
    "coparenting": (
        "You offer emotionally safe responses for coparenting focused "
        "on the children's wellbeing. Keep communication child-centered, "
        "respectful, and solution-oriented. Remember: the kids come first."
    ),
    
    "workplace": (
        "You translate workplace messages for professional tone and "
        "clear intent. Maintain professionalism while ensuring the "
        "message is direct, respectful, and actionable."
    ),
    
    "family": (
        "You understand family dynamics and help rephrase for better "
        "family relationships. Consider family history, respect boundaries, "
        "and promote healing and understanding."
    ),
    
    "friend": (
        "You assist with friendship communication to strengthen bonds "
        "and resolve conflicts. Focus on maintaining the friendship "
        "while addressing issues honestly and supportively."
    )
}

EMERGENCY_PROMPTS = {
    "conflict": (
        "This seems like a tense situation. Focus on de-escalation, "
        "finding common ground, and preventing further harm to the relationship."
    ),
    
    "apology": (
        "This appears to be an apology. Help make it sincere, specific, "
        "and focused on repair rather than justification."
    ),
    
    "difficult_news": (
        "This seems to contain difficult news. Help deliver it with "
        "compassion, clarity, and support for the recipient."
    )
}

def get_system_prompt(context: str, is_received: bool = False) -> str:
    """Generate system prompt based on context and message type"""
    base_prompt = COACHING_PROMPTS.get(context, COACHING_PROMPTS["general"])
    
    if is_received:
        action_prompt = (
            "Analyze this received message and suggest how to respond. "
            "Help understand the underlying emotions and needs, then "
            "provide guidance on how to reply with empathy and wisdom."
        )
    else:
        action_prompt = (
            "Improve this message before sending. Make it clearer, "
            "more empathetic, and more likely to achieve positive outcomes. "
            "Maintain the sender's authentic voice while enhancing the message."
        )
    
    return f"{base_prompt} {action_prompt}"

def create_message_payload(message: str, context: str, is_received: bool = False) -> list:
    """Create the message payload for AI API"""
    system_prompt = get_system_prompt(context, is_received)
    
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Message: {message}"}
    ]

def detect_message_type(message: str) -> str:
    """Simple detection of message type for special handling"""
    message_lower = message.lower()
    
    # Check for conflict indicators
    if any(word in message_lower for word in ['angry', 'upset', 'frustrated', 'mad', 'hate']):
        return "conflict"
    
    # Check for apology indicators  
    if any(word in message_lower for word in ['sorry', 'apologize', 'my fault', 'forgive']):
        return "apology"
    
    # Check for difficult news indicators
    if any(word in message_lower for word in ['bad news', 'problem', 'issue', 'concern', 'worried']):
        return "difficult_news"
    
    return "normal"

# =============================================
# Utility Functions
# =============================================

def get_ai_response(message: str, context: str, is_received: bool = False) -> Dict[str, Any]:
    """Get AI response from OpenRouter API with fallback models"""
    api_key = st.session_state.get('api_key', '')
    if not api_key:
        return {"error": "No API key configured"}
    
    # Create the message payload
    messages = create_message_payload(message, context, is_received)
    
    # Try each model in sequence for reliability
    for model in AI_MODELS:
        try:
            response = requests.post(
                API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=30
            )
            
            response.raise_for_status()
            result_data = response.json()
            
            if "choices" in result_data and len(result_data["choices"]) > 0:
                ai_reply = result_data["choices"][0]["message"]["content"]
                model_name = format_model_name(model)
                
                # Detect message type for special handling
                message_type = detect_message_type(message)
                
                return format_ai_response(
                    message=message,
                    ai_reply=ai_reply,
                    model=model_name,
                    is_received=is_received,
                    message_type=message_type
                )
            
        except requests.exceptions.RequestException as e:
            # Log the error and try next model
            continue
        except Exception as e:
            # Unexpected error, try next model
            continue
    
    return {"error": "All AI models failed to respond"}

def format_ai_response(message: str, ai_reply: str, model: str, is_received: bool, message_type: str) -> Dict[str, Any]:
    """Format the AI response into a standardized structure"""
    if is_received:
        return {
            "type": "translate",
            "sentiment": "neutral",
            "meaning": f"Interpretation: {ai_reply[:100]}...",
            "response": ai_reply,
            "original": message,
            "model": model,
            "message_type": message_type
        }
    else:
        return {
            "type": "coach", 
            "sentiment": "improved",
            "original": message,
            "improved": ai_reply,
            "model": model,
            "message_type": message_type
        }

def format_model_name(model_string: str) -> str:
    """Format model string into a readable name"""
    return (model_string
            .split("/")[-1]
            .replace(":free", "")
            .replace("-", " ")
            .title())

def create_history_entry(message: str, result: Dict[str, Any], entry_type: str) -> Dict[str, Any]:
    """Create a standardized history entry"""
    timestamp = datetime.datetime.now()
    
    return {
        "id": f"{entry_type}_{timestamp.timestamp()}",
        "time": timestamp.strftime("%m/%d %H:%M"),
        "type": entry_type,
        "original": message,
        "result": result.get("improved" if entry_type == "coach" else "response", ""),
        "sentiment": result.get("sentiment", "neutral"),
        "model": result.get("model", "Unknown"),
        "message_type": result.get("message_type", "normal"),
        "timestamp": timestamp.isoformat()
    }

def validate_token(token: str) -> bool:
    """Validate beta access token"""
    return token in VALID_TOKENS

def generate_filename(prefix: str = "third_voice") -> str:
    """Generate a timestamped filename"""
    timestamp = datetime.datetime.now().strftime('%m%d_%H%M')
    return f"{prefix}_{timestamp}.json"

def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def format_time_ago(timestamp_str: str) -> str:
    """Format timestamp as time ago"""
    try:
        timestamp = datetime.datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        now = datetime.datetime.now()
        diff = now - timestamp
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"
    except:
        return "Unknown"

def sanitize_input(text: str) -> str:
    """Sanitize user input for safety"""
    text = text.strip()
    if len(text) > 5000:  # Reasonable limit for messages
        text = text[:5000]
    return text

def get_message_stats(history: list) -> Dict[str, int]:
    """Calculate statistics for message history"""
    if not history:
        return {'total': 0, 'coached': 0, 'translated': 0}
    
    coached = sum(1 for entry in history if entry.get('type') == 'coach')
    translated = sum(1 for entry in history if entry.get('type') == 'translate')
    
    return {
        'total': len(history),
        'coached': coached,
        'translated': translated
    }

def health_check() -> Dict[str, bool]:
    """Perform basic health checks"""
    checks = {
        'api_key_configured': bool(st.session_state.get('api_key')),
        'session_initialized': 'contacts' in st.session_state,
        'active_contact_valid': (
            st.session_state.get('active_contact', '') in 
            st.session_state.get('contacts', {})
        )
    }
    
    return checks

# =============================================
# Session State Management
# =============================================

def get_default_contact_name(context: str) -> str:
    """Get a friendly default name for each context."""
    context_names = {
        'general': 'General',
        'romantic': 'My Partner ❤️',
        'coparenting': 'Co-Parent 👨‍👩‍👧',
        'workplace': 'Work Contact 💼',
        'family': 'Family Member 👨‍👩‍👧‍👦',
        'friend': 'Friend 👯'
    }
    return context_names.get(context, context.title())

def initialize_session_state():
    """Initialize all session state variables with defaults"""
    # Generate default contacts and journals from CONTEXTS
    default_contacts = {}
    default_journals = {}
    
    for context in CONTEXTS:
        contact_name = get_default_contact_name(context)
        default_contacts[contact_name] = {
            'context': context,
            'history': []
        }
        default_journals[contact_name] = {
            'what_worked': '',
            'what_didnt': '',
            'insights': '',
            'patterns': ''
        }
    
    defaults = {
        # Authentication
        'token_validated': not REQUIRE_TOKEN,
        'api_key': st.secrets.get("OPENROUTER_API_KEY", ""),
        
        # Core data structures
        'contacts': default_contacts,
        'active_contact': get_default_contact_name('romantic'),  # Changed to My Partner ❤️
        'journal_entries': default_journals,
        'feedback_data': {},
        
        # User statistics
        'user_stats': {
            'total_messages': 0,
            'coached_messages': 0,
            'translated_messages': 0
        },
        
        # UI state
        'active_mode': None,  # 'coach' or 'translate'
        'show_advanced': False,
        'last_save_time': None
    }
    
    # Set defaults only if not already set
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get_current_contact():
    """Get the currently active contact"""
    return st.session_state.contacts[st.session_state.active_contact]

def add_contact(name: str, context: str) -> bool:
    """Add a new contact to the system"""
    if name in st.session_state.contacts:
        return False
    
    st.session_state.contacts[name] = {
        'context': context,
        'history': []
    }
    st.session_state.journal_entries[name] = {
        'what_worked': '',
        'what_didnt': '',
        'insights': '',
        'patterns': ''
    }
    st.session_state.active_contact = name
    return True

def delete_contact(name: str) -> bool:
    """Delete a contact (except General)"""
    if name == "General" or name not in st.session_state.contacts:
        return False
    
    del st.session_state.contacts[name]
    if name in st.session_state.journal_entries:
        del st.session_state.journal_entries[name]
    
    # Switch to General if we deleted the active contact
    if st.session_state.active_contact == name:
        st.session_state.active_contact = get_default_contact_name('general')
    
    return True

def add_history_entry(contact_name: str, entry: dict):
    """Add a history entry to a specific contact"""
    if contact_name in st.session_state.contacts:
        st.session_state.contacts[contact_name]['history'].append(entry)

def update_user_stats(stat_type: str):
    """Update user statistics"""
    if stat_type in st.session_state.user_stats:
        st.session_state.user_stats[stat_type] += 1

def set_feedback(entry_id: str, feedback_type: str):
    """Set feedback for a specific entry"""
    st.session_state.feedback_data[entry_id] = feedback_type

def get_contact_stats(contact_name: str) -> dict:
    """Get statistics for a specific contact"""
    if contact_name not in st.session_state.contacts:
        return {'total': 0, 'coached': 0, 'translated': 0}
    
    history = st.session_state.contacts[contact_name]['history']
    
    return {
        'total': len(history),
        'coached': sum(1 for h in history if h['type'] == 'coach'),
        'translated': sum(1 for h in history if h['type'] == 'translate')
    }

def get_feedback_stats() -> dict:
    """Get overall feedback statistics"""
    feedback_counts = {
        'positive': 0,
        'neutral': 0,
        'negative': 0
    }
    
    for feedback in st.session_state.feedback_data.values():
        if feedback in feedback_counts:
            feedback_counts[feedback] += 1
    
    return feedback_counts

def clear_session_data():
    """Clear all session data (for fresh start)"""
    keys_to_clear = [
        'contacts', 'active_contact', 'journal_entries',
        'feedback_data', 'user_stats', 'active_mode',
        'show_advanced', 'last_save_time'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    # Reinitialize with defaults
    initialize_session_state()

def export_session_data() -> dict:
    """Export session data for saving"""
    import datetime
    
    return {
        'contacts': st.session_state.contacts,
        'journal_entries': st.session_state.journal_entries,
        'feedback_data': st.session_state.feedback_data,
        'user_stats': st.session_state.user_stats,
        'exported_at': datetime.datetime.now().isoformat(),
        'version': '1.0.0'
    }

def import_session_data(data: dict) -> bool:
    """Import session data from saved file"""
    try:
        # Validate required keys exist
        required_keys = ['contacts', 'journal_entries', 'feedback_data', 'user_stats']
        if not all(key in data for key in required_keys):
            return False
        
        # Import the data
        st.session_state.contacts = data.get('contacts', {
            get_default_contact_name('general'): {'context': 'general', 'history': []}
        })
        st.session_state.journal_entries = data.get('journal_entries', {
            get_default_contact_name('general'): {
                'what_worked': '', 'what_didnt': '', 'insights': '', 'patterns': ''
            }
        })
        st.session_state.feedback_data = data.get('feedback_data', {})
        st.session_state.user_stats = data.get('user_stats', {
            'total_messages': 0,
            'coached_messages': 0,
            'translated_messages': 0
        })
        
        # Ensure active contact is valid
        if st.session_state.active_contact not in st.session_state.contacts:
            st.session_state.active_contact = get_default_contact_name('romantic')  # Changed to My Partner ❤️
        
        return True
        
    except Exception as e:
        st.error(f"Import failed: {str(e)}")
        return False

# =============================================
# UI Components
# =============================================

def authenticate_user():
    """Handle user authentication for beta access"""
    if REQUIRE_TOKEN and not st.session_state.get('token_validated', False):
        st.markdown("# 🎙️ The Third Voice")
        st.markdown("*Your AI Communication Coach*")
        st.warning("🔐 Access restricted. Enter beta token to continue.")
        
        token = st.text_input("Beta Token:", type="password")
        
        if st.button("Validate Access"):
            if validate_token(token):
                st.session_state.token_validated = True
                st.success("✅ Welcome to The Third Voice beta!")
                st.rerun()
            else:
                st.error("❌ Invalid token. Contact support for access.")
        
        st.stop()

def render_header():
    """Render the main header with logo and branding"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Try to load logo, fallback to text
        try:
            st.image("logo.svg", width=200)
        except:
            st.markdown("# 🎙️ The Third Voice")
        
        st.markdown(
            "<div style='text-align: center'>"
            "<i>Created by Predrag Mirković</i><br>"
            "<small>Building bridges through better communication</small>"
            "</div>", 
            unsafe_allow_html=True
        )

def render_sidebar():
    """Render the sidebar with contact management and data controls"""
    st.sidebar.markdown("### 👥 Your Contacts")
    
    # Add new contact
    with st.sidebar.expander("➕ Add Contact"):
        new_name = st.text_input("Contact Name:", key="new_contact_name")
        new_context = st.selectbox("Relationship Type:", CONTEXTS, key="new_contact_context")
        
        if st.button("Add Contact", key="add_contact_btn"):
            if new_name and new_name.strip():
                clean_name = sanitize_input(new_name.strip())
                if add_contact(clean_name, new_context):
                    st.success(f"✅ Added {clean_name}")
                    st.rerun()
                else:
                    st.error("Contact already exists!")
            else:
                st.error("Please enter a contact name.")
    
    # Contact selection
    contact_names = list(st.session_state.contacts.keys())
    if contact_names:
        selected = st.sidebar.radio(
            "Active Contact:", 
            contact_names, 
            index=contact_names.index(st.session_state.active_contact)
        )
        st.session_state.active_contact = selected
    
    # Contact info
    current_contact = get_current_contact()
    contact_stats = get_contact_stats(st.session_state.active_contact)
    
    st.sidebar.markdown(
        f"**Context:** {current_contact['context']}\n"
        f"**Total Messages:** {contact_stats['total']}\n"
        f"**Coached:** {contact_stats['coached']}\n"
        f"**Translated:** {contact_stats['translated']}"
    )
    
    # Delete contact (except General)
    if st.session_state.active_contact != "General":
        if st.sidebar.button("🗑️ Delete Contact", key="delete_contact"):
            if delete_contact(st.session_state.active_contact):
                st.success("Contact deleted")
                st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 💾 Data Management")
    
    # Data import
    uploaded_file = st.sidebar.file_uploader(
        "📤 Import Data", 
        type="json", 
        key="data_import"
    )
    
    if uploaded_file:
        try:
            data = json.load(uploaded_file)
            if import_session_data(data):
                st.sidebar.success("✅ Data imported successfully!")
                st.rerun()
            else:
                st.sidebar.error("❌ Import failed - invalid data")
        except Exception as e:
            st.sidebar.error(f"❌ Import error: {str(e)}")
    
    # Data export
    if st.sidebar.button("💾 Export Data", key="data_export"):
        export_data = export_session_data()
        filename = generate_filename()
        st.sidebar.download_button(
            "📥 Download Data",
            data=json.dumps(export_data, indent=2),
            file_name=filename,
            mime="application/json",
            use_container_width=True
        )

def render_main_interface():
    """Render the main communication interface"""
    st.markdown(f"### 💬 Communicating with: **{st.session_state.active_contact}**")
    
    # Mode selection buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(
            "📤 Coach My Message", 
            type="primary", 
            use_container_width=True,
            key="coach_mode_btn"
        ):
            st.session_state.active_mode = "coach"
            st.rerun()
    
    with col2:
        if st.button(
            "📥 Understand Their Message", 
            type="primary", 
            use_container_width=True,
            key="translate_mode_btn"
        ):
            st.session_state.active_mode = "translate"
            st.rerun()

def render_message_processor():
    """Handle message input and AI processing"""
    if not st.session_state.get('active_mode'):
        return
    
    mode = st.session_state.active_mode
    
    # Back button
    if st.button("← Back", key="back_btn"):
        st.session_state.active_mode = None
        st.rerun()
    
    # Mode-specific UI
    input_class = "user-msg" if mode == "coach" else "contact-msg"
    title_text = "📤 Your message to send:" if mode == "coach" else "📥 Message you received:"
    placeholder = "Type your message here..." if mode == "coach" else "Paste their message here..."
    
    st.markdown(
        f'<div class="{input_class}"><strong>{title_text}</strong></div>', 
        unsafe_allow_html=True
    )
    
    # Message input
    message = st.text_area(
        "",
        height=120,
        key=f"{mode}_input",
        label_visibility="collapsed",
        placeholder=placeholder
    )
    
    # Action buttons
    col1, col2 = st.columns([3, 1])
    
    with col1:
        process_btn_text = "🚀 Improve My Message" if mode == "coach" else "🔍 Analyze & Respond"
        process_btn = st.button(process_btn_text, type="primary", key="process_btn")
    
    with col2:
        if st.button("Clear", type="secondary", key="clear_btn"):
            st.session_state[f"{mode}_input"] = ""
            st.rerun()
    
    # Process message
    if process_btn and message.strip():
        clean_message = sanitize_input(message.strip())
        
        with st.spinner("🎙️ The Third Voice is analyzing..."):
            current_contact = get_current_contact()
            result = get_ai_response(clean_message, current_contact['context'], mode == "translate")
            
            if "error" not in result:
                render_ai_response(result, mode)
                
                # Create and save history entry
                history_entry = create_history_entry(clean_message, result, mode)
                add_history_entry(st.session_state.active_contact, history_entry)
                update_user_stats(mode)
                
                # Feedback section
                render_feedback_section(history_entry)
                
                st.success("✅ Saved to history")
            else:
                st.error(f"❌ {result['error']}")
    
    elif process_btn:
        st.warning("⚠️ Please enter a message first.")

def render_ai_response(result: dict, mode: str):
    """Display AI response in formatted manner"""
    st.markdown("### 🎙️ The Third Voice says:")
    
    if mode == "coach":
        st.markdown(
            f'<div class="ai-response">'
            f'<strong>✨ Your improved message:</strong><br><br>'
            f'{result.get("improved", "")}<br><br>'
            f'<small><i>Generated by: {result.get("model", "Unknown")}</i></small>'
            f'</div>', 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="ai-response">'
            f'<strong>🔍 What they really mean:</strong><br>'
            f'{result.get("response", "")}<br><br>'
            f'<small><i>Generated by: {result.get("model", "Unknown")}</i></small>'
            f'</div>', 
            unsafe_allow_html=True
        )

def render_feedback_section(history_entry: dict):
    """Render feedback collection interface"""
    st.markdown("### 📊 Was this helpful?")
    
    col1, col2, col3 = st.columns(3)
    feedback_options = [
        ("👍 Yes", "positive"),
        ("👌 Okay", "neutral"),
        ("👎 No", "negative")
    ]
    
    for idx, (label, sentiment) in enumerate(feedback_options):
        with [col1, col2, col3][idx]:
            if st.button(label, key=f"feedback_{sentiment}_{history_entry['id']}"):
                set_feedback(history_entry['id'], sentiment)
                st.success("Thanks for the feedback!")

def render_history_tab():
    """Render the conversation history tab"""
    st.markdown(f"### 📜 History with {st.session_state.active_contact}")
    
    current_contact = get_current_contact()
    history = current_contact.get('history', [])
    
    if not history:
        st.info(f"No messages yet with {st.session_state.active_contact}. Use the buttons above to get started!")
        return
    
    # Filter options
    filter_type = st.selectbox("Filter:", ["All", "Coached Messages", "Understood Messages"])
    
    filtered_history = history
    if filter_type == "Coached Messages":
        filtered_history = [h for h in history if h['type'] == 'coach']
    elif filter_type == "Understood Messages":
        filtered_history = [h for h in history if h['type'] == 'translate']
    
    # Display history entries
    for entry in reversed(filtered_history):
        preview_text = truncate_text(entry.get('original', ''), 50)
        
        with st.expander(f"**{entry['time']}** • {entry['type'].title()} • {preview_text}..."):
            if entry['type'] == 'coach':
                st.markdown(
                    f'<div class="user-msg">📤 <strong>Original:</strong> {entry["original"]}</div>', 
                    unsafe_allow_html=True
                )
                st.markdown(
                    f'<div class="ai-response">🎙️ <strong>Improved:</strong> {entry["result"]}<br>'
                    f'<small><i>by {entry.get("model", "Unknown")}</i></small></div>', 
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="contact-msg">📥 <strong>They said:</strong> {entry["original"]}</div>', 
                    unsafe_allow_html=True
                )
                st.markdown(
                    f'<div class="ai-response">🎙️ <strong>Analysis:</strong> {entry["result"]}<br>'
                    f'<small><i>by {entry.get("model", "Unknown")}</i></small></div>', 
                    unsafe_allow_html=True
                )
            
            # Show existing feedback
            feedback = st.session_state.feedback_data.get(entry.get('id'))
            if feedback:
                emoji_map = {"positive": "👍", "neutral": "👌", "negative": "👎"}
                st.markdown(f"*Your feedback: {emoji_map.get(feedback, '❓')}*")

def render_journal_tab():
    """Render the communication journal tab"""
    st.markdown(f"### 📘 Communication Journal - {st.session_state.active_contact}")
    
    contact_key = st.session_state.active_contact
    
    # Initialize journal entries for this contact if not exists
    if contact_key not in st.session_state.journal_entries:
        st.session_state.journal_entries[contact_key] = {
            'what_worked': '',
            'what_didnt': '',
            'insights': '',
            'patterns': ''
        }
    
    journal = st.session_state.journal_entries[contact_key]
    
    # Two-column layout for journal entries
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            '<div class="journal-section">**💚 What worked well?**</div>', 
            unsafe_allow_html=True
        )
        journal['what_worked'] = st.text_area(
            "",
            value=journal['what_worked'],
            key=f"worked_{contact_key}",
            height=100,
            placeholder="Communication strategies that were successful..."
        )
        
        st.markdown(
            '<div class="journal-section">**🔍 Key insights?**</div>', 
            unsafe_allow_html=True
        )
        journal['insights'] = st.text_area(
            "",
            value=journal['insights'],
            key=f"insights_{contact_key}",
            height=100,
            placeholder="Important realizations about this relationship..."
        )
    
    with col2:
        st.markdown(
            '<div class="journal-section">**⚠️ What didn\'t work?**</div>', 
            unsafe_allow_html=True
        )
        journal['what_didnt'] = st.text_area(
            "",
            value=journal['what_didnt'],
            key=f"didnt_{contact_key}",
            height=100,
            placeholder="What caused issues or misunderstandings..."
        )
        
        st.markdown(
            '<div class="journal-section">**📊 Patterns noticed?**</div>', 
            unsafe_allow_html=True
        )
        journal['patterns'] = st.text_area(
            "",
            value=journal['patterns'],
            key=f"patterns_{contact_key}",
            height=100,
            placeholder="Communication patterns you've observed..."
        )

def render_stats_tab():
    """Render the statistics and analytics tab"""
    st.markdown("### 📊 Your Communication Stats")
    
    # Overall stats
    stats = st.session_state.user_stats
    col1, col2, col3 = st.columns(3)
    
    stat_items = [
        (stats.get("total_messages", 0), "Total Messages"),
        (stats.get("coached_messages", 0), "Messages Coached"),
        (stats.get("translated_messages", 0), "Messages Understood")
    ]
    
    for idx, (stat, label) in enumerate(stat_items):
        with [col1, col2, col3][idx]:
            st.markdown(
                f'<div class="stats-card"><h3>{stat}</h3><p>{label}</p></div>', 
                unsafe_allow_html=True
            )
    
    # Stats by contact
    st.markdown("### 👥 By Contact")
    for name, contact in st.session_state.contacts.items():
        contact_stats = get_contact_stats(name)
        if contact_stats['total'] > 0:
            st.markdown(
                f"**{name}:** {contact_stats['total']} total "
                f"({contact_stats['coached']} coached, {contact_stats['translated']} understood)"
            )
    
    # Feedback summary
    feedback_stats = get_feedback_stats()
    if any(feedback_stats.values()):
        st.markdown("### 📝 Feedback Summary")
        st.markdown(
            f"👍 Positive: {feedback_stats['positive']} | "
            f"👌 Neutral: {feedback_stats['neutral']} | "
            f"👎 Negative: {feedback_stats['negative']}"
        )

def render_about_tab():
    """Render the about/help tab"""
    st.markdown("""
    ### ℹ️ About The Third Voice
    
    **The communication coach that's there when you need it most.**
    
    Instead of repairing relationships after miscommunication damage, The Third Voice helps you communicate better in real-time.
    
    **How it works:**
    1. **Select your contact** - Each relationship gets personalized coaching
    2. **Coach your messages** - Improve what you're about to send
    3. **Understand their messages** - Decode the real meaning behind their words
    4. **Build better patterns** - Journal and learn from each interaction
    
    **Key Features:**
    - 🎯 Context-aware coaching for different relationships
    - 📊 Track your communication progress
    - 📘 Personal journal for insights
    - 💾 Export/import your data
    - 🔒 Privacy-first design
    
    **Privacy First:** All data stays on your device. Save and load your own files.
    
    **Beta v1.0.0** — Built with ❤️ to heal relationships through better communication.
    
    *"When both people are talking from pain, someone needs to be the third voice."*
    
    ---
    
    **Support & Community:**
    - 💬 Join discussions at our community forum
    - 📧 Report bugs or suggest features
    - 🌟 Share your success stories
    
    **Technical Details:**
    - Powered by OpenRouter API
    - Uses multiple AI models for reliability
    - Built with Streamlit for easy deployment
    - Open source and community-driven
    """)

def render_tabs():
    """Render all application tabs"""
    tab1, tab2, tab3, tab4 = st.tabs(["📜 History", "📘 Journal", "📊 Stats", "ℹ️ About"])
    
    with tab1:
        render_history_tab()
    
    with tab2:
        render_journal_tab()
    
    with tab3:
        render_stats_tab()
    
    with tab4:
        render_about_tab()

# =============================================
# Main Application
# =============================================

def main():
    """Main application entry point"""
    # Configure the page
    st.set_page_config(
        page_title="The Third Voice AI",
        page_icon="🎙️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply styling
    apply_styles()
    
    # Initialize session state
    initialize_session_state()
    
    # Authenticate user
    authenticate_user()
    
    # Render main interface
    render_header()
    render_sidebar()
    render_main_interface()
    render_message_processor()
    render_tabs()
    
    # Health check in development
    if st.secrets.get("DEBUG", False):
        with st.expander("🔧 Debug Info"):
            st.json({
                "session_state_keys": list(st.session_state.keys()),
                "active_contact": st.session_state.get('active_contact'),
                "active_mode": st.session_state.get('active_mode'),
                "health_check": health_check()
            })

if __name__ == "__main__":
    main()
