import streamlit as st
import json
import datetime
import requests

# Constants
CONTEXTS = ["general", "romantic", "coparenting", "workplace", "family", "friend"]
REQUIRE_TOKEN = True

# First-time user template data
TEMPLATE_DATA = {
    'contacts': {
        'General': {'context': 'general', 'history': []},
        'Sarah (Partner)': {
            'context': 'romantic',
            'history': [
                {
                    "id": "template_coach_1",
                    "time": "07/15 14:30",
                    "type": "coach",
                    "original": "You never listen to me",
                    "result": "I feel like I'm not being heard when we talk. Could we find a way to communicate better?",
                    "sentiment": "improved",
                    "model": "Example"
                },
                {
                    "id": "template_translate_1",
                    "time": "07/15 18:45",
                    "type": "translate",
                    "original": "Fine, whatever",
                    "result": "This likely means they're frustrated and feeling dismissed. They may need some space or reassurance that their concerns are valid.",
                    "sentiment": "neutral",
                    "model": "Example"
                }
            ]
        },
        'Mike (Coworker)': {
            'context': 'workplace',
            'history': [
                {
                    "id": "template_coach_2",
                    "time": "07/16 09:15",
                    "type": "coach",
                    "original": "Your code is wrong and needs to be fixed",
                    "result": "I noticed some issues in the code that we should address. Could we review it together when you have time?",
                    "sentiment": "improved",
                    "model": "Example"
                }
            ]
        },
        'Mom (Family)': {
            'context': 'family',
            'history': [
                {
                    "id": "template_translate_2",
                    "time": "07/16 16:20",
                    "type": "translate",
                    "original": "I'm just saying maybe you should call more often",
                    "result": "She's expressing that she misses you and would like more regular contact. This comes from a place of love and wanting to stay connected.",
                    "sentiment": "neutral",
                    "model": "Example"
                }
            ]
        },
        'Alex (Friend)': {
            'context': 'friend',
            'history': [
                {
                    "id": "template_coach_3",
                    "time": "07/17 12:00",
                    "type": "coach",
                    "original": "Can't believe you bailed on me again",
                    "result": "I was really looking forward to our plans and felt disappointed when they got cancelled. Is everything okay?",
                    "sentiment": "improved",
                    "model": "Example"
                }
            ]
        }
    },
    'journal_entries': {
        'Sarah (Partner)': {
            'what_worked': 'Using "I feel" statements instead of "you never" helps avoid defensiveness',
            'what_didnt': 'Texting about serious topics when we\'re both stressed',
            'insights': 'She communicates better in person and needs time to process',
            'patterns': 'We tend to miscommunicate most in the evenings when we\'re tired'
        },
        'Mike (Coworker)': {
            'what_worked': 'Scheduling dedicated review time instead of dropping feedback suddenly',
            'what_didnt': 'Being too direct about problems without offering solutions',
            'insights': 'He\'s more receptive to feedback when it\'s framed as collaboration',
            'patterns': 'Morning communications are more effective than end-of-day'
        },
        'Mom (Family)': {
            'what_worked': 'Calling at regular times so she knows when to expect it',
            'what_didnt': 'Dismissing her concerns as "nagging"',
            'insights': 'Her comments about calling more often come from love, not criticism',
            'patterns': 'She worries more when life changes are happening'
        },
        'Alex (Friend)': {
            'what_worked': 'Being honest about disappointment while staying caring',
            'what_didnt': 'Making accusations instead of expressing feelings',
            'insights': 'Our friendship is strong enough to handle honest conversations',
            'patterns': 'We both struggle with last-minute plan changes'
        }
    },
    'feedback_data': {
        'template_coach_1': 'positive',
        'template_translate_1': 'positive',
        'template_coach_2': 'neutral',
        'template_translate_2': 'positive',
        'template_coach_3': 'positive'
    },
    'user_stats': {
        'total_messages': 5,
        'coached_messages': 3,
        'translated_messages': 2
    }
}

# Setup
st.set_page_config(page_title="The Third Voice", page_icon="🎙️", layout="wide")

# Enhanced CSS with logo styles
st.markdown("""
<style>
.contact-card {background:rgba(76,175,80,0.1);padding:0.8rem;border-radius:8px;border-left:4px solid #4CAF50;margin:0.5rem 0;cursor:pointer}
.ai-response {background:rgba(76,175,80,0.1);padding:1rem;border-radius:8px;border-left:4px solid #4CAF50;margin:0.5rem 0}
.user-msg {background:rgba(33,150,243,0.1);padding:0.8rem;border-radius:8px;border-left:4px solid #2196F3;margin:0.3rem 0}
.contact-msg {background:rgba(255,193,7,0.1);padding:0.8rem;border-radius:8px;border-left:4px solid #FFC107;margin:0.3rem 0}
.pos {background:rgba(76,175,80,0.2);padding:0.5rem;border-radius:5px;margin:0.2rem 0}
.neg {background:rgba(244,67,54,0.2);padding:0.5rem;border-radius:5px;margin:0.2rem 0}
.neu {background:rgba(33,150,243,0.2);padding:0.5rem;border-radius:5px;margin:0.2rem 0}
.journal-section {background:rgba(156,39,176,0.1);padding:1rem;border-radius:8px;margin:0.5rem 0}
.main-actions {display:flex;gap:1rem;margin:1rem 0}
.main-actions button {flex:1;padding:0.8rem;font-size:1.1rem}
.feedback-section {background:rgba(0,150,136,0.1);padding:1rem;border-radius:8px;margin:1rem 0}
.stats-card {background:rgba(63,81,181,0.1);padding:1rem;border-radius:8px;margin:0.5rem 0;text-align:center}
.logo-container {display:flex;justify-content:center;align-items:center;margin:1rem 0}
.auto-save-indicator {
    position: fixed;
    top: 10px;
    right: 10px;
    background: #4CAF50;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.8rem;
    z-index: 1000;
    opacity: 0;
    transition: opacity 0.3s ease;
}
.auto-save-indicator.show {
    opacity: 1;
}
.welcome-banner {
    background: linear-gradient(135deg, #9C27B0, #673AB7);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
    text-align: center;
}
</style>""", unsafe_allow_html=True)

# Auto-save indicator
st.markdown('<div id="auto-save-indicator" class="auto-save-indicator">✓ Auto-saved</div>', unsafe_allow_html=True)

# JavaScript for localStorage functionality
st.markdown("""
<script>
// Auto-save functionality
function saveToLocalStorage(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
        showAutoSaveIndicator();
    } catch (e) {
        console.error('Failed to save to localStorage:', e);
    }
}

function loadFromLocalStorage(key) {
    try {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : null;
    } catch (e) {
        console.error('Failed to load from localStorage:', e);
        return null;
    }
}

function showAutoSaveIndicator() {
    const indicator = document.getElementById('auto-save-indicator');
    if (indicator) {
        indicator.classList.add('show');
        setTimeout(() => {
            indicator.classList.remove('show');
        }, 2000);
    }
}

// Save data when page unloads
window.addEventListener('beforeunload', function() {
    // This will be called by Streamlit when needed
});

// Auto-save trigger (called from Python)
window.triggerAutoSave = function(data) {
    saveToLocalStorage('third_voice_data', data);
};

// Load data trigger (called from Python)
window.loadAutoSave = function() {
    return loadFromLocalStorage('third_voice_data');
};

// Token management
window.saveToken = function(token) {
    if (token) {
        localStorage.setItem('third_voice_token', token);
    }
};

window.loadToken = function() {
    return localStorage.getItem('third_voice_token');
};

window.clearToken = function() {
    localStorage.removeItem('third_voice_token');
};
</script>
""", unsafe_allow_html=True)

# Session defaults
defaults = {
    'token_validated': not REQUIRE_TOKEN,
    'api_key': st.secrets.get("OPENROUTER_API_KEY", ""),
    'contacts': {'General': {'context': 'general', 'history': []}},
    'active_contact': 'General',
    'journal_entries': {},
    'feedback_data': {},
    'user_stats': {'total_messages': 0, 'coached_messages': 0, 'translated_messages': 0},
    'first_time_user': True,
    'auto_save_enabled': True,
    'remember_token': False
}

# Initialize session state
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Auto-load functionality
def load_auto_save():
    """Load data from localStorage if available"""
    if st.session_state.auto_save_enabled:
        # This would be called via JavaScript component in a real implementation
        # For now, we'll simulate the auto-load behavior
        pass

# Auto-save functionality
def trigger_auto_save():
    """Trigger auto-save to localStorage"""
    if st.session_state.auto_save_enabled:
        save_data = {
            'contacts': st.session_state.contacts,
            'journal_entries': st.session_state.journal_entries,
            'feedback_data': st.session_state.feedback_data,
            'user_stats': st.session_state.user_stats,
            'first_time_user': st.session_state.first_time_user,
            'auto_saved_at': datetime.datetime.now().isoformat()
        }
        # This would trigger the JavaScript auto-save function
        st.components.v1.html(f"""
        <script>
        if (typeof window.triggerAutoSave === 'function') {{
            window.triggerAutoSave({json.dumps(save_data)});
        }}
        </script>
        """, height=0)

# Token management with remember option
def handle_token_validation():
    """Handle token validation with remember option"""
    if REQUIRE_TOKEN and not st.session_state.token_validated:
        st.markdown("""
        <div class="logo-container">
            <svg viewBox="0 0 400 120" xmlns="http://www.w3.org/2000/svg" width="350">
              <defs>
                <linearGradient id="gradient3" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" style="stop-color:#9C27B0;stop-opacity:1" />
                  <stop offset="100%" style="stop-color:#673AB7;stop-opacity:1" />
                </linearGradient>
              </defs>
              
              <!-- Sound Wave Pattern -->
              <g stroke="#9C27B0" stroke-width="2" fill="none" opacity="0.4">
                <path d="M 20 56 Q 30 46 40 56 Q 50 66 60 56 Q 70 46 80 56 Q 90 66 100 56 Q 110 46 120 56"/>
                <path d="M 25 46 Q 35 36 45 46 Q 55 56 65 46 Q 75 36 85 46 Q 95 56 105 46 Q 115 36 125 46"/>
                <path d="M 25 66 Q 35 76 45 66 Q 55 56 65 66 Q 75 76 85 66 Q 95 56 105 66 Q 115 76 125 66"/>
              </g>
              
              <!-- AI Nodes -->
              <circle cx="40" cy="56" r="2" fill="#9C27B0" opacity="0.7"/>
              <circle cx="65" cy="46" r="2" fill="#9C27B0" opacity="0.7"/>
              <circle cx="85" cy="66" r="2" fill="#9C27B0" opacity="0.7"/>
              <circle cx="105" cy="46" r="2" fill="#9C27B0" opacity="0.7"/>
              
              <!-- Connection lines -->
              <line x1="40" y1="56" x2="65" y2="46" stroke="#9C27B0" stroke-width="1" opacity="0.5"/>
              <line x1="65" y1="46" x2="85" y2="66" stroke="#9C27B0" stroke-width="1" opacity="0.5"/>
              <line x1="85" y1="66" x2="105" y2="46" stroke="#9C27B0" stroke-width="1" opacity="0.5"/>
              
              <!-- Number "3" -->
              <text x="30" y="70" font-family="Arial, sans-serif" font-size="48" font-weight="bold" fill="url(#gradient3)">3</text>
              
              <!-- Sound wave bars -->
              <rect x="52" y="40" width="2" height="8" fill="#9C27B0" opacity="0.6"/>
              <rect x="56" y="35" width="2" height="18" fill="#9C27B0" opacity="0.6"/>
              <rect x="60" y="38" width="2" height="12" fill="#9C27B0" opacity="0.6"/>
              <rect x="64" y="42" width="2" height="6" fill="#9C27B0" opacity="0.6"/>
              
              <rect x="52" y="65" width="2" height="10" fill="#9C27B0" opacity="0.6"/>
              <rect x="56" y="62" width="2" height="16" fill="#9C27B0" opacity="0.6"/>
              <rect x="60" y="67" width="2" height="8" fill="#9C27B0" opacity="0.6"/>
              <rect x="64" y="70" width="2" height="4" fill="#9C27B0" opacity="0.6"/>
              
              <!-- Text -->
              <text x="150" y="45" font-family="Arial, sans-serif" font-size="24" font-weight="300" fill="#2C3E50">The Third</text>
              <text x="150" y="70" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#9C27B0">Voice</text>
              <text x="150" y="88" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D" opacity="0.8">AI Communication Coach</text>
            </svg>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='text-align: center'><i>Created by Predrag Mirković</i></div>", unsafe_allow_html=True)
        st.warning("🔐 Access restricted. Enter beta token to continue.")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            token = st.text_input("Token:", type="password", key="token_input")
        with col2:
            remember = st.checkbox("Remember me", key="remember_token")
        
        if st.button("Validate"):
            if token in ["ttv-beta-001", "ttv-beta-002", "ttv-beta-003"]:
                st.session_state.token_validated = True
                st.session_state.remember_token = remember
                if remember:
                    # Save token to localStorage
                    st.components.v1.html(f"""
                    <script>
                    if (typeof window.saveToken === 'function') {{
                        window.saveToken('{token}');
                    }}
                    </script>
                    """, height=0)
                st.success("✅ Authorized")
                st.rerun()
            else:
                st.error("Invalid token")
        
        # Auto-load saved token
        if not st.session_state.token_validated:
            st.components.v1.html("""
            <script>
            if (typeof window.loadToken === 'function') {
                const savedToken = window.loadToken();
                if (savedToken && ['ttv-beta-001', 'ttv-beta-002', 'ttv-beta-003'].includes(savedToken)) {
                    // Auto-validate saved token
                    window.parent.postMessage({type: 'auto_validate_token', token: savedToken}, '*');
                }
            }
            </script>
            """, height=0)
        
        st.stop()

# Call token validation
handle_token_validation()

# First-time user experience
if st.session_state.first_time_user and len(st.session_state.contacts) == 1:
    st.markdown("""
    <div class="welcome-banner">
        <h2>🎉 Welcome to The Third Voice!</h2>
        <p>Your AI communication coach is ready to help you build better relationships.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🚀 Start with Examples", type="primary"):
            # Load template data
            st.session_state.contacts = TEMPLATE_DATA['contacts']
            st.session_state.journal_entries = TEMPLATE_DATA['journal_entries']
            st.session_state.feedback_data = TEMPLATE_DATA['feedback_data']
            st.session_state.user_stats = TEMPLATE_DATA['user_stats']
            st.session_state.first_time_user = False
            st.session_state.active_contact = 'Sarah (Partner)'
            trigger_auto_save()
            st.success("✅ Sample data loaded! Explore the examples to see how it works.")
            st.rerun()
    
    with col2:
        if st.button("📖 Quick Tour"):
            st.info("""
            **How The Third Voice works:**
            1. **Select a contact** - Each relationship gets personalized coaching
            2. **Coach your messages** - Improve what you're about to send
            3. **Understand their messages** - Decode the real meaning
            4. **Learn and grow** - Use the journal to track insights
            """)
    
    with col3:
        if st.button("✨ Start Fresh"):
            st.session_state.first_time_user = False
            st.rerun()

# API function
def get_ai_response(message, context, is_received=False):
    if not st.session_state.api_key:
        return {"error": "No API key"}
    
    prompts = {
        "general": "You are an emotionally intelligent communication coach. Help improve this message for clarity and empathy.",
        "romantic": "You help reframe romantic messages with empathy and clarity while maintaining intimacy.",
        "coparenting": "You offer emotionally safe responses for coparenting focused on the children's wellbeing.",
        "workplace": "You translate workplace messages for professional tone and clear intent.",
        "family": "You understand family dynamics and help rephrase for better family relationships.",
        "friend": "You assist with friendship communication to strengthen bonds and resolve conflicts."
    }
    
    if is_received:
        system_prompt = f"{prompts.get(context, prompts['general'])} Analyze this received message and suggest how to respond."
    else:
        system_prompt = f"{prompts.get(context, prompts['general'])} Improve this message before sending."
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Message: {message}"}
    ]
    
    models = [
        "google/gemma-2-9b-it:free",
        "meta-llama/llama-3.2-3b-instruct:free",
        "microsoft/phi-3-mini-128k-instruct:free"
    ]
    
    for model in models:
        try:
            r = requests.post("https://openrouter.ai/api/v1/chat/completions", 
                headers={"Authorization": f"Bearer {st.session_state.api_key}"},
                json={"model": model, "messages": messages}, timeout=30)
            r.raise_for_status()
            reply = r.json()["choices"][0]["message"]["content"]
            
            model_name = model.split("/")[-1].replace(":free", "").replace("-", " ").title()
            
            if is_received:
                return {
                    "type": "translate",
                    "sentiment": "neutral",
                    "meaning": f"Interpretation: {reply[:100]}...",
                    "response": reply,
                    "model": model_name
                }
            else:
                return {
                    "type": "coach",
                    "sentiment": "improved",
                    "original": message,
                    "improved": reply,
                    "model": model_name
                }
        except Exception as e:
            continue
    
    return {"error": "All models failed"}

# Sidebar - Contact Management
st.sidebar.markdown("### 👥 Your Contacts")

# Auto-save settings
with st.sidebar.expander("⚙️ Settings"):
    st.session_state.auto_save_enabled = st.checkbox("Enable auto-save", value=st.session_state.auto_save_enabled)
    
    if st.button("💾 Manual Save"):
        trigger_auto_save()
        st.success("Data saved!")
    
    if st.button("🔄 Load Saved Data"):
        load_auto_save()
        st.success("Data loaded!")
    
    if st.button("🗑️ Clear All Data"):
        if st.button("⚠️ Confirm Delete"):
            for key in ['contacts', 'journal_entries', 'feedback_data', 'user_stats']:
                st.session_state[key] = defaults[key]
            st.session_state.first_time_user = True
            st.components.v1.html("""
            <script>
            localStorage.removeItem('third_voice_data');
            </script>
            """, height=0)
            st.success("All data cleared!")
            st.rerun()
    
    if REQUIRE_TOKEN:
        if st.button("🚪 Logout"):
            st.session_state.token_validated = False
            st.components.v1.html("""
            <script>
            if (typeof window.clearToken === 'function') {
                window.clearToken();
            }
            </script>
            """, height=0)
            st.rerun()

# Add new contact
st.sidebar.markdown("#### ➕ Add Contact")
new_contact = st.sidebar.text_input("Name:")
new_context = st.sidebar.selectbox("Context:", CONTEXTS)

if st.sidebar.button("Add Contact"):
    if new_contact and new_contact not in st.session_state.contacts:
        st.session_state.contacts[new_contact] = {'context': new_context, 'history': []}
        st.session_state.journal_entries[new_contact] = {
            'what_worked': '', 'what_didnt': '', 'insights': '', 'patterns': ''
        }
        st.sidebar.success(f"✅ Added {new_contact}")
        trigger_auto_save()
        st.rerun()
    elif new_contact in st.session_state.contacts:
        st.sidebar.error("Contact already exists")
    else:
        st.sidebar.error("Please enter a name")

# Contact selection
st.sidebar.markdown("#### 📞 Select Contact")
for contact in st.session_state.contacts:
    context = st.session_state.contacts[contact]['context']
    count = len(st.session_state.contacts[contact]['history'])
    
    if st.sidebar.button(f"{contact} ({context}) - {count} messages", 
                         key=f"contact_{contact}"):
        st.session_state.active_contact = contact
        st.rerun()

# Delete contact
if st.session_state.active_contact != 'General':
    if st.sidebar.button(f"🗑️ Delete {st.session_state.active_contact}"):
        if st.sidebar.button("⚠️ Confirm Delete Contact"):
            del st.session_state.contacts[st.session_state.active_contact]
            if st.session_state.active_contact in st.session_state.journal_entries:
                del st.session_state.journal_entries[st.session_state.active_contact]
            st.session_state.active_contact = 'General'
            trigger_auto_save()
            st.rerun()

# Main content area
st.markdown(f"## 💬 {st.session_state.active_contact}")

# Display current context
current_context = st.session_state.contacts[st.session_state.active_contact]['context']
st.markdown(f"**Context:** {current_context.title()}")

# Main action buttons
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🤖 Coach My Message")
    user_message = st.text_area("What do you want to say?", height=100, key="coach_input")
    
    if st.button("✨ Coach This Message", type="primary"):
        if user_message:
            with st.spinner("Coaching your message..."):
                response = get_ai_response(user_message, current_context, is_received=False)
                
                if "error" in response:
                    st.error(f"Error: {response['error']}")
                else:
                    # Generate unique ID
                    message_id = f"msg_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    
                    # Create history entry
                    history_entry = {
                        "id": message_id,
                        "time": datetime.datetime.now().strftime("%m/%d %H:%M"),
                        "type": "coach",
                        "original": user_message,
                        "result": response["improved"],
                        "sentiment": response["sentiment"],
                        "model": response["model"]
                    }
                    
                    # Add to history
                    st.session_state.contacts[st.session_state.active_contact]['history'].append(history_entry)
                    st.session_state.user_stats['total_messages'] += 1
                    st.session_state.user_stats['coached_messages'] += 1
                    
                    # Display results
                    st.markdown('<div class="user-msg">', unsafe_allow_html=True)
                    st.markdown(f"**Original:** {user_message}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="ai-response">', unsafe_allow_html=True)
                    st.markdown(f"**Improved:** {response['improved']}")
                    st.markdown(f"*Model: {response['model']}*")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Feedback section
                    st.markdown('<div class="feedback-section">', unsafe_allow_html=True)
                    st.markdown("**Was this helpful?**")
                    col_pos, col_neu, col_neg = st.columns(3)
                    with col_pos:
                        if st.button("👍 Yes", key=f"pos_{message_id}"):
                            st.session_state.feedback_data[message_id] = 'positive'
                            st.success("Thanks for the feedback!")
                            trigger_auto_save()
                    with col_neu:
                        if st.button("🤷 Okay", key=f"neu_{message_id}"):
                            st.session_state.feedback_data[message_id] = 'neutral'
                            st.info("Thanks for the feedback!")
                            trigger_auto_save()
                    with col_neg:
                        if st.button("👎 No", key=f"neg_{message_id}"):
                            st.session_state.feedback_data[message_id] = 'negative'
                            st.error("Sorry it wasn't helpful!")
                            trigger_auto_save()
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    trigger_auto_save()
                    st.rerun()
        else:
            st.error("Please enter a message to coach")

with col2:
    st.markdown("### 🔍 Understand Their Message")
    received_message = st.text_area("What did they say?", height=100, key="translate_input")
    
    if st.button("🔍 Decode This Message", type="primary"):
        if received_message:
            with st.spinner("Analyzing their message..."):
                response = get_ai_response(received_message, current_context, is_received=True)
                
                if "error" in response:
                    st.error(f"Error: {response['error']}")
                else:
                    # Generate unique ID
                    message_id = f"msg_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    
                    # Create history entry
                    history_entry = {
                        "id": message_id,
                        "time": datetime.datetime.now().strftime("%m/%d %H:%M"),
                        "type": "translate",
                        "original": received_message,
                        "result": response["response"],
                        "sentiment": response["sentiment"],
                        "model": response["model"]
                    }
                    
                    # Add to history
                    st.session_state.contacts[st.session_state.active_contact]['history'].append(history_entry)
                    st.session_state.user_stats['total_messages'] += 1
                    st.session_state.user_stats['translated_messages'] += 1
                    
                    # Display results
                    st.markdown('<div class="contact-msg">', unsafe_allow_html=True)
                    st.markdown(f"**They said:** {received_message}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="ai-response">', unsafe_allow_html=True)
                    st.markdown(f"**What they likely mean:** {response['response']}")
                    st.markdown(f"*Model: {response['model']}*")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Feedback section
                    st.markdown('<div class="feedback-section">', unsafe_allow_html=True)
                    st.markdown("**Was this helpful?**")
                    col_pos, col_neu, col_neg = st.columns(3)
                    with col_pos:
                        if st.button("👍 Yes", key=f"pos_{message_id}"):
                            st.session_state.feedback_data[message_id] = 'positive'
                            st.success("Thanks for the feedback!")
                            trigger_auto_save()
                    with col_neu:
                        if st.button("🤷 Okay", key=f"neu_{message_id}"):
                            st.session_state.feedback_data[message_id] = 'neutral'
                            st.info("Thanks for the feedback!")
                            trigger_auto_save()
                    with col_neg:
                        if st.button("👎 No", key=f"neg_{message_id}"):
                            st.session_state.feedback_data[message_id] = 'negative'
                            st.error("Sorry it wasn't helpful!")
                            trigger_auto_save()
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    trigger_auto_save()
                    st.rerun()
        else:
            st.error("Please enter a message to decode")

# Message history
st.markdown("### 📜 Message History")
history = st.session_state.contacts[st.session_state.active_contact]['history']

if history:
    # Reverse to show newest first
    for msg in reversed(history):
        sentiment_class = {"improved": "pos", "neutral": "neu", "negative": "neg"}.get(msg['sentiment'], "neu")
        
        st.markdown(f'<div class="{sentiment_class}">', unsafe_allow_html=True)
        st.markdown(f"**{msg['time']}** - {msg['type'].title()}")
        st.markdown(f"**Original:** {msg['original']}")
        st.markdown(f"**Result:** {msg['result']}")
        st.markdown(f"*Model: {msg['model']}*")
        
        # Show feedback if available
        if msg['id'] in st.session_state.feedback_data:
            feedback = st.session_state.feedback_data[msg['id']]
            emoji = {"positive": "👍", "neutral": "🤷", "negative": "👎"}
            st.markdown(f"**Feedback:** {emoji.get(feedback, '❓')} {feedback}")
        
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("No messages yet. Start a conversation!")

# Journal section
st.markdown("### 📝 Communication Journal")
if st.session_state.active_contact in st.session_state.journal_entries:
    journal = st.session_state.journal_entries[st.session_state.active_contact]
    
    with st.expander("✏️ Edit Journal Entry"):
        col1, col2 = st.columns(2)
        
        with col1:
            what_worked = st.text_area("What worked well?", 
                                     value=journal.get('what_worked', ''), 
                                     height=100)
            insights = st.text_area("Key insights?", 
                                  value=journal.get('insights', ''), 
                                  height=100)
        
        with col2:
            what_didnt = st.text_area("What didn't work?", 
                                    value=journal.get('what_didnt', ''), 
                                    height=100)
            patterns = st.text_area("Communication patterns?", 
                                  value=journal.get('patterns', ''), 
                                  height=100)
        
        if st.button("💾 Save Journal"):
            st.session_state.journal_entries[st.session_state.active_contact] = {
                'what_worked': what_worked,
                'what_didnt': what_didnt,
                'insights': insights,
                'patterns': patterns
            }
            trigger_auto_save()
            st.success("Journal saved!")
    
    # Display current journal
    if any(journal.values()):
        st.markdown('<div class="journal-section">', unsafe_allow_html=True)
        if journal.get('what_worked'):
            st.markdown(f"**✅ What worked:** {journal['what_worked']}")
        if journal.get('what_didnt'):
            st.markdown(f"**❌ What didn't work:** {journal['what_didnt']}")
        if journal.get('insights'):
            st.markdown(f"**💡 Insights:** {journal['insights']}")
        if journal.get('patterns'):
            st.markdown(f"**🔄 Patterns:** {journal['patterns']}")
        st.markdown('</div>', unsafe_allow_html=True)

# Stats section
st.markdown("### 📊 Your Stats")
stats = st.session_state.user_stats
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="stats-card">', unsafe_allow_html=True)
    st.markdown(f"**Total Messages**")
    st.markdown(f"# {stats['total_messages']}")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="stats-card">', unsafe_allow_html=True)
    st.markdown(f"**Coached Messages**")
    st.markdown(f"# {stats['coached_messages']}")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="stats-card">', unsafe_allow_html=True)
    st.markdown(f"**Translated Messages**")
    st.markdown(f"# {stats['translated_messages']}")
    st.markdown('</div>', unsafe_allow_html=True)

# Feedback summary
positive_feedback = sum(1 for f in st.session_state.feedback_data.values() if f == 'positive')
total_feedback = len(st.session_state.feedback_data)

if total_feedback > 0:
    satisfaction = (positive_feedback / total_feedback) * 100
    st.markdown(f"**User Satisfaction:** {satisfaction:.1f}% ({positive_feedback}/{total_feedback} positive)")

# Footer
st.markdown("---")
st.markdown("*The Third Voice - Your AI Communication Coach*")
st.markdown("*Created by Predrag Mirković*")

# Auto-save on any state change
if st.session_state.auto_save_enabled:
    trigger_auto_save()
