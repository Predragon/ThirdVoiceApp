import streamlit as st
import json
import datetime
import requests
from streamlit_local_storage import LocalStorage

# Constants
CONTEXTS = ["general", "romantic", "coparenting", "workplace", "family", "friend"]
REQUIRE_TOKEN = True

# Setup
st.set_page_config(page_title="The Third Voice", page_icon="🎙️", layout="wide")
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
.auto-save-indicator {
    position: fixed;
    top: 10px;
    right: 10px;
    background: rgba(76,175,80,0.9);
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-size: 0.8rem;
    z-index: 1000;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
}
.storage-controls {
    background: rgba(63,81,181,0.1);
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
    border-left: 4px solid #3F51B5;
}
</style>""", unsafe_allow_html=True)

# Initialize LocalStorage
@st.cache_resource
def get_local_storage():
    return LocalStorage()

localS = get_local_storage()

# Session defaults
defaults = {
    'token_validated': not REQUIRE_TOKEN,
    'api_key': st.secrets.get("OPENROUTER_API_KEY", ""),
    'contacts': {'General': {'context': 'general', 'history': []}},
    'active_contact': 'General',
    'journal_entries': {},
    'feedback_data': {},
    'user_stats': {'total_messages': 0, 'coached_messages': 0, 'translated_messages': 0},
    'remember_token': False,
    'auto_save_enabled': True,
    'data_loaded': False
}

# Initialize session state
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Auto-load data from localStorage on first run
def load_from_local_storage():
    """Load data from localStorage if available"""
    if not st.session_state.data_loaded:
        try:
            # Load main data
            contacts_data = localS.getItem("ttv_contacts", key="load_contacts")
            journal_data = localS.getItem("ttv_journal", key="load_journal")
            feedback_data = localS.getItem("ttv_feedback", key="load_feedback")
            stats_data = localS.getItem("ttv_stats", key="load_stats")
            settings_data = localS.getItem("ttv_settings", key="load_settings")
            
            # Parse and load contacts
            if "load_contacts" in st.session_state and st.session_state["load_contacts"]:
                loaded_contacts = json.loads(st.session_state["load_contacts"])
                if loaded_contacts:
                    st.session_state.contacts = loaded_contacts
            
            # Parse and load journal
            if "load_journal" in st.session_state and st.session_state["load_journal"]:
                loaded_journal = json.loads(st.session_state["load_journal"])
                if loaded_journal:
                    st.session_state.journal_entries = loaded_journal
            
            # Parse and load feedback
            if "load_feedback" in st.session_state and st.session_state["load_feedback"]:
                loaded_feedback = json.loads(st.session_state["load_feedback"])
                if loaded_feedback:
                    st.session_state.feedback_data = loaded_feedback
            
            # Parse and load stats
            if "load_stats" in st.session_state and st.session_state["load_stats"]:
                loaded_stats = json.loads(st.session_state["load_stats"])
                if loaded_stats:
                    st.session_state.user_stats = loaded_stats
            
            # Parse and load settings
            if "load_settings" in st.session_state and st.session_state["load_settings"]:
                loaded_settings = json.loads(st.session_state["load_settings"])
                if loaded_settings:
                    st.session_state.auto_save_enabled = loaded_settings.get('auto_save_enabled', True)
                    st.session_state.remember_token = loaded_settings.get('remember_token', False)
            
            # Load token if remember is enabled
            if st.session_state.remember_token:
                token_data = localS.getItem("ttv_token", key="load_token")
                if "load_token" in st.session_state and st.session_state["load_token"]:
                    st.session_state.token_validated = True
            
            st.session_state.data_loaded = True
            
        except Exception as e:
            st.sidebar.error(f"Error loading data: {str(e)}")

# Auto-save function
def auto_save_data():
    """Auto-save data to localStorage"""
    if st.session_state.auto_save_enabled:
        try:
            # Save main data
            localS.setItem("ttv_contacts", json.dumps(st.session_state.contacts))
            localS.setItem("ttv_journal", json.dumps(st.session_state.journal_entries))
            localS.setItem("ttv_feedback", json.dumps(st.session_state.feedback_data))
            localS.setItem("ttv_stats", json.dumps(st.session_state.user_stats))
            
            # Save settings
            settings = {
                'auto_save_enabled': st.session_state.auto_save_enabled,
                'remember_token': st.session_state.remember_token,
                'last_saved': datetime.datetime.now().isoformat()
            }
            localS.setItem("ttv_settings", json.dumps(settings))
            
            # Save token if remember is enabled
            if st.session_state.remember_token and st.session_state.token_validated:
                localS.setItem("ttv_token", "validated")
            
            # Show auto-save indicator
            st.markdown('<div class="auto-save-indicator">✅ Auto-saved</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.sidebar.error(f"Auto-save error: {str(e)}")

# Load data on startup
load_from_local_storage()

# Token gate with remember option
if REQUIRE_TOKEN and not st.session_state.token_validated:
    st.markdown("# 🎙️ The Third Voice")
    st.markdown("*Your AI Communication Coach*")
    st.warning("🔐 Access restricted. Enter beta token to continue.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        token = st.text_input("Token:", type="password")
    with col2:
        st.session_state.remember_token = st.checkbox("Remember me", value=st.session_state.remember_token)
    
    if st.button("Validate"):
        if token in ["ttv-beta-001", "ttv-beta-002", "ttv-beta-003"]:
            st.session_state.token_validated = True
            if st.session_state.remember_token:
                localS.setItem("ttv_token", "validated")
            st.success("✅ Authorized")
            st.rerun()
        else:
            st.error("Invalid token")
    st.stop()

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

# Sidebar - Storage Controls
st.sidebar.markdown("### 💾 Storage Settings")
st.sidebar.markdown('<div class="storage-controls">', unsafe_allow_html=True)

# Auto-save toggle
st.session_state.auto_save_enabled = st.sidebar.checkbox(
    "🔄 Auto-save enabled", 
    value=st.session_state.auto_save_enabled,
    help="Automatically save data to browser storage"
)

# Clear all data button
if st.sidebar.button("🗑️ Clear All Browser Data"):
    if st.sidebar.button("⚠️ Confirm Clear All", type="secondary"):
        try:
            localS.deleteAll()
            st.session_state.clear()
            st.sidebar.success("✅ All data cleared")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error clearing data: {str(e)}")

# Manual save/load buttons
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("💾 Save Now"):
        auto_save_data()
        st.sidebar.success("✅ Saved!")

with col2:
    if st.button("📥 Load Now"):
        st.session_state.data_loaded = False
        load_from_local_storage()
        st.sidebar.success("✅ Loaded!")

st.sidebar.markdown("</div>", unsafe_allow_html=True)

# Sidebar - Contact Management
st.sidebar.markdown("### 👥 Your Contacts")

# Add new contact
with st.sidebar.expander("➕ Add Contact"):
    new_name = st.text_input("Name:")
    new_context = st.selectbox("Relationship:", CONTEXTS)
    if st.button("Add") and new_name and new_name not in st.session_state.contacts:
        st.session_state.contacts[new_name] = {'context': new_context, 'history': []}
        st.session_state.active_contact = new_name
        auto_save_data()  # Auto-save after adding contact
        st.success(f"Added {new_name}")
        st.rerun()

# Contact selection
contact_names = list(st.session_state.contacts.keys())
if contact_names:
    selected = st.sidebar.radio("Select Contact:", contact_names, 
                               index=contact_names.index(st.session_state.active_contact))
    if selected != st.session_state.active_contact:
        st.session_state.active_contact = selected
        auto_save_data()  # Auto-save when switching contacts

# Contact info
if st.session_state.active_contact in st.session_state.contacts:
    contact = st.session_state.contacts[st.session_state.active_contact]
    st.sidebar.markdown(f"**Context:** {contact['context']}")
    st.sidebar.markdown(f"**Messages:** {len(contact['history'])}")

# Delete contact
if st.sidebar.button("🗑️ Delete Contact") and st.session_state.active_contact != "General":
    del st.session_state.contacts[st.session_state.active_contact]
    st.session_state.active_contact = "General"
    auto_save_data()  # Auto-save after deleting contact
    st.rerun()

# File management (backup)
st.sidebar.markdown("---")
st.sidebar.markdown("### 📁 Manual Backup")
uploaded = st.sidebar.file_uploader("📤 Load History", type="json")
if uploaded:
    try:
        data = json.load(uploaded)
        st.session_state.contacts = data.get('contacts', st.session_state.contacts)
        st.session_state.journal_entries = data.get('journal_entries', {})
        st.session_state.feedback_data = data.get('feedback_data', {})
        st.session_state.user_stats = data.get('user_stats', st.session_state.user_stats)
        auto_save_data()  # Auto-save after loading file
        st.sidebar.success("✅ Data loaded!")
    except:
        st.sidebar.error("❌ Invalid file")

if st.sidebar.button("💾 Export Backup"):
    save_data = {
        'contacts': st.session_state.contacts,
        'journal_entries': st.session_state.journal_entries,
        'feedback_data': st.session_state.feedback_data,
        'user_stats': st.session_state.user_stats,
        'saved_at': datetime.datetime.now().isoformat()
    }
    filename = f"third_voice_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.json"
    st.sidebar.download_button(
        "📥 Download Backup", 
        json.dumps(save_data, indent=2),
        filename,
        "application/json",
        use_container_width=True
    )

# Header with new SVG logo placeholder
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # New SVG logo would go here
    st.markdown("""
    <div style="text-align: center">
        <svg width="200" height="100" viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="20" fill="#4CAF50" opacity="0.8"/>
            <circle cx="100" cy="50" r="20" fill="#2196F3" opacity="0.8"/>
            <circle cx="150" cy="50" r="20" fill="#FF9800" opacity="0.8"/>
            <path d="M 50 50 Q 100 30 150 50" stroke="#333" stroke-width="2" fill="none"/>
            <text x="100" y="85" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="bold">The Third Voice</text>
        </svg>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='text-align: center'><i>Created by Predrag Mirković</i></div>", unsafe_allow_html=True)

st.markdown(f"### 💬 Communicating with: **{st.session_state.active_contact}**")

# Main action buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("📤 Coach My Message", type="primary", use_container_width=True):
        st.session_state.active_mode = "coach"
        st.rerun()
with col2:
    if st.button("📥 Understand Their Message", type="primary", use_container_width=True):
        st.session_state.active_mode = "translate"
        st.rerun()

# Initialize mode
if 'active_mode' not in st.session_state:
    st.session_state.active_mode = None

# Message input and processing
if st.session_state.active_mode:
    mode = st.session_state.active_mode
    
    # Back button
    if st.button("← Back"):
        st.session_state.active_mode = None
        st.rerun()
    
    # Color-coded input area
    input_class = "user-msg" if mode == "coach" else "contact-msg"
    st.markdown(f'<div class="{input_class}"><strong>{"📤 Your message to send:" if mode == "coach" else "📥 Message you received:"}</strong></div>', unsafe_allow_html=True)
    
    message = st.text_area("", height=120, key=f"{mode}_input", label_visibility="collapsed", 
                          placeholder="Type your message here..." if mode == "coach" else "Paste their message here...")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        process_btn = st.button(f"{'🚀 Improve My Message' if mode == 'coach' else '🔍 Analyze & Respond'}", type="secondary")
    with col2:
        if st.button("Clear", type="secondary"):
            st.session_state[f"{mode}_input"] = ""
            st.rerun()
    
    if process_btn and message.strip():
        with st.spinner("🎙️ The Third Voice is analyzing..."):
            contact = st.session_state.contacts[st.session_state.active_contact]
            result = get_ai_response(message, contact['context'], mode == "translate")
            
            if "error" not in result:
                st.markdown("### 🎙️ The Third Voice says:")
                
                if mode == "coach":
                    st.markdown(f'<div class="ai-response"><strong>✨ Your improved message:</strong><br><br>{result["improved"]}<br><br><small><i>Generated by: {result["model"]}</i></small></div>', unsafe_allow_html=True)
                    st.session_state.user_stats['coached_messages'] += 1
                else:
                    st.markdown(f'<div class="ai-response"><strong>🔍 What they really mean:</strong><br>{result["response"]}<br><br><small><i>Generated by: {result["model"]}</i></small></div>', unsafe_allow_html=True)
                    st.session_state.user_stats['translated_messages'] += 1
                
                # Save to history
                history_entry = {
                    "id": f"{mode}_{len(contact['history'])}_{datetime.datetime.now().timestamp()}",
                    "time": datetime.datetime.now().strftime("%m/%d %H:%M"),
                    "type": mode,
                    "original": message,
                    "result": result.get("improved" if mode == "coach" else "response", ""),
                    "sentiment": result.get("sentiment", "neutral"),
                    "model": result.get("model", "Unknown")
                }
                
                contact['history'].append(history_entry)
                st.session_state.user_stats['total_messages'] += 1
                
                # Auto-save after processing message
                auto_save_data()
                
                # Simple feedback
                st.markdown("### 📊 Was this helpful?")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("👍 Yes", key=f"good_{history_entry['id']}"):
                        st.session_state.feedback_data[history_entry['id']] = "positive"
                        auto_save_data()  # Auto-save feedback
                        st.success("Thanks for the feedback!")
                
                with col2:
                    if st.button("👌 Okay", key=f"ok_{history_entry['id']}"):
                        st.session_state.feedback_data[history_entry['id']] = "neutral"
                        auto_save_data()  # Auto-save feedback
                        st.success("Thanks for the feedback!")
                
                with col3:
                    if st.button("👎 No", key=f"bad_{history_entry['id']}"):
                        st.session_state.feedback_data[history_entry['id']] = "negative"
                        auto_save_data()  # Auto-save feedback
                        st.success("Thanks for the feedback!")
                
                st.markdown("---")
                
                # Quick actions after AI response
                if mode == "coach":
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📋 Copy Improved Message", key=f"copy_{history_entry['id']}"):
                            st.code(result["improved"])
                            st.success("✅ Message ready to copy!")
                    with col2:
                        if st.button("📝 Make Another Version", key=f"retry_{history_entry['id']}"):
                            st.session_state[f"{mode}_input"] = message
                            st.rerun()
                
                else:  # translate mode
                    if st.button("💬 Draft a Reply", key=f"draft_{history_entry['id']}"):
                        st.session_state.active_mode = "coach"
                        st.session_state["coach_input"] = ""
                        st.rerun()
            
            else:
                st.error(f"❌ {result['error']}")

# Conversation History
if st.session_state.active_contact in st.session_state.contacts:
    contact = st.session_state.contacts[st.session_state.active_contact]
    
    if contact['history']:
        st.markdown("---")
        st.markdown("### 📚 Conversation History")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            show_coached = st.checkbox("📤 Show Coached", value=True)
        with col2:
            show_translated = st.checkbox("📥 Show Translated", value=True)
        with col3:
            if st.button("🗑️ Clear History"):
                if st.button("⚠️ Confirm Clear", type="secondary"):
                    contact['history'] = []
                    auto_save_data()
                    st.success("✅ History cleared!")
                    st.rerun()
        
        # Display history
        history = contact['history']
        filtered_history = []
        
        for entry in reversed(history):  # Show newest first
            if (entry['type'] == 'coach' and show_coached) or (entry['type'] == 'translate' and show_translated):
                filtered_history.append(entry)
        
        if filtered_history:
            for entry in filtered_history:
                icon = "📤" if entry['type'] == 'coach' else "📥"
                type_text = "You sent" if entry['type'] == 'coach' else "You received"
                
                with st.expander(f"{icon} {type_text} • {entry['time']} • {entry['model']}"):
                    st.markdown(f"**Original:** {entry['original']}")
                    st.markdown(f"**Response:** {entry['result']}")
                    
                    # Show feedback if available
                    if entry['id'] in st.session_state.feedback_data:
                        feedback = st.session_state.feedback_data[entry['id']]
                        feedback_emoji = {"positive": "👍", "neutral": "👌", "negative": "👎"}
                        st.markdown(f"**Feedback:** {feedback_emoji[feedback]} {feedback}")
        else:
            st.info("No messages match your filter criteria.")
    else:
        st.info("💡 No conversation history yet. Start by coaching a message or translating one!")

# Journal Section
st.markdown("---")
st.markdown("### 📖 Communication Journal")

with st.expander("📝 Add Journal Entry"):
    journal_text = st.text_area("Reflect on your communication:", height=100)
    journal_mood = st.selectbox("How are you feeling about this relationship?", 
                               ["😊 Great", "😐 Okay", "😔 Struggling", "😤 Frustrated", "❤️ Connected"])
    
    if st.button("💾 Save Entry") and journal_text.strip():
        entry_id = f"journal_{datetime.datetime.now().timestamp()}"
        st.session_state.journal_entries[entry_id] = {
            'contact': st.session_state.active_contact,
            'text': journal_text,
            'mood': journal_mood,
            'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        auto_save_data()
        st.success("✅ Journal entry saved!")
        st.rerun()

# Display recent journal entries
if st.session_state.journal_entries:
    st.markdown("**Recent Entries:**")
    contact_entries = [(k, v) for k, v in st.session_state.journal_entries.items() 
                      if v['contact'] == st.session_state.active_contact]
    
    if contact_entries:
        # Show last 3 entries
        for entry_id, entry in sorted(contact_entries, key=lambda x: x[1]['date'], reverse=True)[:3]:
            st.markdown(f'<div class="journal-section">'
                       f'<strong>{entry["mood"]} • {entry["date"]}</strong><br>'
                       f'{entry["text"]}</div>', unsafe_allow_html=True)
    else:
        st.info("No journal entries for this contact yet.")

# Feedback Summary
st.markdown("---")
st.markdown("### 📊 Your Progress")

# Statistics
stats = st.session_state.user_stats
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f'<div class="stats-card"><h3>{stats["total_messages"]}</h3><p>Total Messages</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="stats-card"><h3>{stats["coached_messages"]}</h3><p>Messages Coached</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="stats-card"><h3>{stats["translated_messages"]}</h3><p>Messages Translated</p></div>', unsafe_allow_html=True)

# Feedback analysis
if st.session_state.feedback_data:
    feedback_counts = {"positive": 0, "neutral": 0, "negative": 0}
    for feedback in st.session_state.feedback_data.values():
        feedback_counts[feedback] += 1
    
    st.markdown("**Feedback Summary:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f'<div class="pos">👍 Helpful: {feedback_counts["positive"]}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="neu">👌 Okay: {feedback_counts["neutral"]}</div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="neg">👎 Not helpful: {feedback_counts["negative"]}</div>', unsafe_allow_html=True)

# Contact insights
if st.session_state.active_contact in st.session_state.contacts:
    contact = st.session_state.contacts[st.session_state.active_contact]
    if contact['history']:
        st.markdown("**Communication Insights:**")
        
        coach_count = sum(1 for entry in contact['history'] if entry['type'] == 'coach')
        translate_count = sum(1 for entry in contact['history'] if entry['type'] == 'translate')
        
        if coach_count > translate_count:
            st.info("💡 You're actively working on improving your messages. Great job!")
        elif translate_count > coach_count:
            st.info("💡 You're focusing on understanding their messages. Good listening!")
        else:
            st.info("💡 You have a balanced approach to communication!")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; color: #666;">
    <p>🎙️ <strong>The Third Voice</strong> - Your AI Communication Coach</p>
    <p><em>Helping you communicate with empathy, clarity, and understanding</em></p>
    <p>Created by Predrag Mirković • Built with Streamlit & OpenRouter</p>
</div>
""", unsafe_allow_html=True)

# Auto-save indicator (if data was modified)
if st.session_state.auto_save_enabled:
    st.markdown('<div class="auto-save-indicator">🔄 Auto-save: ON</div>', unsafe_allow_html=True)
