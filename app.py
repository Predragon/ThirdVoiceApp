import streamlit as st
import json
import datetime
import requests

# Constants - Expanded relationship categories
CONTEXTS = ["general", "romantic", "coparenting", "workplace", "family", "friend", "sister", "mother", "father", "brother", "twin"]
REQUIRE_TOKEN = True

# Setup
st.set_page_config(page_title="The Third Voice", page_icon="🎙️", layout="wide")

# Enhanced CSS with improved styling
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
.feedback-section {background:rgba(0,200,83,0.1);padding:1rem;border-radius:8px;margin:1rem 0;border:1px solid #00c853}
.logo-container {text-align:center;margin:2rem 0}
.onboarding-tip {background:rgba(33,150,243,0.1);padding:1rem;border-radius:8px;border-left:4px solid #2196F3;margin:1rem 0}
.progress-badge {background:#4CAF50;color:white;padding:0.3rem 0.8rem;border-radius:20px;font-size:0.9rem;margin:0.2rem}
.community-link {background:rgba(156,39,176,0.1);padding:1rem;border-radius:8px;text-align:center;margin:1rem 0}
</style>""", unsafe_allow_html=True)

# Session defaults with enhanced features
defaults = {
    'token_validated': not REQUIRE_TOKEN,
    'has_completed_onboarding': False,
    'api_key': st.secrets.get("OPENROUTER_API_KEY", ""),
    'contacts': {'General': {'context': 'general', 'history': [], 'feedback': []}},
    'active_contact': 'General',
    'journal_entries': {},
    'user_feedback': [],
    'usage_stats': {'messages_coached': 0, 'messages_understood': 0, 'total_sessions': 0}
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# One-time token validation with persistence
if REQUIRE_TOKEN and not st.session_state.token_validated:
    st.markdown('<div class="logo-container"><h1>🎙️ The Third Voice</h1><p><i>Your AI Communication Coach</i></p></div>', unsafe_allow_html=True)
    st.warning("🔐 Beta Access Required")
    token = st.text_input("Enter your beta token:", type="password")
    if st.button("Validate Token"):
        if token in ["ttv-beta-001", "ttv-beta-002", "ttv-beta-003"]:
            st.session_state.token_validated = True
            st.session_state.usage_stats['total_sessions'] += 1
            st.success("✅ Welcome to The Third Voice beta!")
            st.balloons()
            st.rerun()
        else:
            st.error("❌ Invalid token. Please contact support.")
    st.stop()

# Enhanced AI response function with better prompts
def get_ai_response(message, context, is_received=False):
    if not st.session_state.api_key:
        return {"error": "No API key configured"}
    
    # Enhanced prompts differentiated by mode and context
    coaching_prompts = {
        "general": "You are an emotionally intelligent communication coach. Help rewrite this message to be clearer, more empathetic, and more effective while maintaining the sender's authentic voice.",
        "romantic": "You specialize in romantic communication. Help rewrite this message to be more loving, understanding, and emotionally connected while avoiding common relationship pitfalls.",
        "coparenting": "You are an expert in coparenting communication. Help rewrite this message to be child-focused, respectful, and collaborative while maintaining boundaries.",
        "workplace": "You are a professional communication expert. Help rewrite this message to be more professional, clear, and diplomatically effective in a work environment.",
        "family": "You understand family dynamics. Help rewrite this message to be more respectful, understanding, and healing while honoring family bonds.",
        "friend": "You specialize in friendship communication. Help rewrite this message to be more supportive, genuine, and strengthening to the friendship.",
        "sister": "You understand sister relationships. Help rewrite this message to be more understanding, supportive, and nurturing of the sisterly bond.",
        "mother": "You understand mother-child dynamics. Help rewrite this message to be more respectful, loving, and honoring of the mother relationship.",
        "father": "You understand father-child dynamics. Help rewrite this message to be more respectful, appreciative, and strengthening of the father relationship.",
        "brother": "You understand brother relationships. Help rewrite this message to be more supportive, understanding, and strengthening of the brotherhood.",
        "twin": "You understand the unique twin bond. Help rewrite this message to honor the special connection while maintaining healthy boundaries."
    }
    
    understanding_prompts = {
        "general": "You are an emotionally intelligent communication interpreter. Analyze this received message for underlying emotions, needs, and intentions. Provide insight into what they really mean and suggest how to respond empathetically.",
        "romantic": "You specialize in romantic communication patterns. Analyze this message from a romantic partner for emotional subtext, attachment needs, and love language. Suggest a loving, understanding response.",
        "coparenting": "You are an expert in coparenting communication. Analyze this message for child-focused concerns, stress factors, and collaborative opportunities. Suggest a response that prioritizes the children's wellbeing.",
        "workplace": "You are a professional communication analyst. Decode this workplace message for professional concerns, power dynamics, and business objectives. Suggest a diplomatically effective response.",
        "family": "You understand family communication patterns. Analyze this message for family dynamics, generational factors, and emotional needs. Suggest a response that heals and strengthens family bonds.",
        "friend": "You specialize in friendship dynamics. Analyze this message for friendship needs, support requests, and social cues. Suggest a response that strengthens the friendship.",
        "sister": "You understand sister relationships. Analyze this message for sisterly dynamics, support needs, and emotional bonds. Suggest a response that nurtures the sister relationship.",
        "mother": "You understand mother communication patterns. Analyze this message for maternal concerns, care expressions, and emotional needs. Suggest a respectful, loving response.",
        "father": "You understand father communication patterns. Analyze this message for paternal concerns, guidance attempts, and emotional expressions. Suggest a respectful, appreciative response.",
        "brother": "You understand brother relationships. Analyze this message for brotherly dynamics, support needs, and connection attempts. Suggest a response that strengthens the brotherhood.",
        "twin": "You understand the unique twin connection. Analyze this message for twin-specific dynamics, shared understanding, and emotional bonds. Suggest a response that honors the twin relationship."
    }
    
    if is_received:
        system_prompt = understanding_prompts.get(context, understanding_prompts["general"])
    else:
        system_prompt = coaching_prompts.get(context, coaching_prompts["general"])
    
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
            
            # Extract model name for display
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
    
    return {"error": "All AI models are currently unavailable. Please try again later."}

# Feedback collection function
def collect_feedback(message_id, feedback_type, rating, comment=""):
    feedback_entry = {
        "id": message_id,
        "type": feedback_type,
        "rating": rating,
        "comment": comment,
        "timestamp": datetime.datetime.now().isoformat(),
        "contact": st.session_state.active_contact
    }
    st.session_state.user_feedback.append(feedback_entry)
    return feedback_entry

# Onboarding flow
if not st.session_state.has_completed_onboarding:
    st.markdown('<div class="logo-container"><h1>🎙️ Welcome to The Third Voice</h1></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="onboarding-tip">
    <h3>🚀 Quick Start Guide</h3>
    <p><strong>The Third Voice</strong> is your AI communication coach that helps you:</p>
    <ul>
        <li><strong>📤 Coach Your Messages:</strong> Improve what you're about to send</li>
        <li><strong>📥 Understand Their Messages:</strong> Decode what they really mean</li>
        <li><strong>📝 Track Progress:</strong> Journal your communication wins</li>
    </ul>
    <p><strong>Try it now:</strong> Start with the "General" contact or add someone specific!</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("✅ Got it! Let's start communicating better"):
        st.session_state.has_completed_onboarding = True
        st.rerun()

# Sidebar - Enhanced Contact Management
st.sidebar.markdown("### 👥 Your Contacts")

# Add new contact with better UX
with st.sidebar.expander("➕ Add New Contact", expanded=False):
    new_name = st.text_input("Contact Name:", placeholder="e.g., Sarah, Mom, Boss")
    new_context = st.selectbox("Relationship Type:", CONTEXTS, 
                              help="Choose the relationship type for personalized coaching")
    if st.button("Add Contact") and new_name:
        if new_name not in st.session_state.contacts:
            st.session_state.contacts[new_name] = {
                'context': new_context, 
                'history': [],
                'feedback': [],
                'created': datetime.datetime.now().isoformat()
            }
            st.session_state.active_contact = new_name
            st.success(f"✅ Added {new_name}")
            st.rerun()
        else:
            st.error("Contact already exists!")

# Enhanced contact selection with stats
contact_names = list(st.session_state.contacts.keys())
if contact_names:
    selected = st.sidebar.radio("Select Contact:", contact_names, 
                               index=contact_names.index(st.session_state.active_contact))
    st.session_state.active_contact = selected

# Enhanced contact info display
if st.session_state.active_contact in st.session_state.contacts:
    contact = st.session_state.contacts[st.session_state.active_contact]
    st.sidebar.markdown(f"**Relationship:** {contact['context'].title()}")
    st.sidebar.markdown(f"**Messages:** {len(contact['history'])}")
    
    # Progress badges
    coached_msgs = sum(1 for h in contact['history'] if h['type'] == 'coach')
    understood_msgs = sum(1 for h in contact['history'] if h['type'] == 'translate')
    
    if coached_msgs > 0:
        st.sidebar.markdown(f'<span class="progress-badge">📤 {coached_msgs} Coached</span>', unsafe_allow_html=True)
    if understood_msgs > 0:
        st.sidebar.markdown(f'<span class="progress-badge">📥 {understood_msgs} Understood</span>', unsafe_allow_html=True)

# Enhanced file management
st.sidebar.markdown("---")
st.sidebar.markdown("### 💾 Data Management")

uploaded = st.sidebar.file_uploader("📤 Import Data", type="json", 
                                   help="Upload previously exported Third Voice data")
if uploaded:
    try:
        data = json.load(uploaded)
        st.session_state.contacts = data.get('contacts', st.session_state.contacts)
        st.session_state.journal_entries = data.get('journal_entries', {})
        st.session_state.user_feedback = data.get('user_feedback', [])
        st.session_state.usage_stats = data.get('usage_stats', st.session_state.usage_stats)
        st.sidebar.success("✅ Data imported successfully!")
    except Exception as e:
        st.sidebar.error("❌ Invalid file format")

if st.sidebar.button("💾 Export All Data"):
    save_data = {
        'contacts': st.session_state.contacts,
        'journal_entries': st.session_state.journal_entries,
        'user_feedback': st.session_state.user_feedback,
        'usage_stats': st.session_state.usage_stats,
        'exported_at': datetime.datetime.now().isoformat()
    }
    filename = f"third_voice_data_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    st.sidebar.download_button(
        "📥 Download Data", 
        json.dumps(save_data, indent=2),
        filename,
        "application/json",
        use_container_width=True,
        help="Download all your data (contacts, history, feedback, journals)"
    )

# Header with improved logo positioning
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    try:
        st.image("logo.png", width=300)  # Increased size
    except:
        st.markdown("# 🎙️ The Third Voice")
    st.markdown('<p style="text-align: center; margin-top: 1rem;"><i>Created by Predrag Mirković</i></p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Community link section
st.markdown("""
<div class="community-link">
    <h4>💬 Join Our Community</h4>
    <p>Share experiences, get tips, and connect with other users improving their communication</p>
    <a href="https://community.thethirdvoice.com" target="_blank" style="color: #9C27B0; text-decoration: none;">
        🚀 Join The Third Voice Community →
    </a>
</div>
""", unsafe_allow_html=True)

st.markdown(f"### 💬 Communicating with: **{st.session_state.active_contact}**")

# Enhanced main action buttons with proper colors
col1, col2 = st.columns(2)

# Custom button styling to match message colors
button_style = """
<style>
.coach-button {
    background: linear-gradient(90deg, #2196F3, #1976D2);
    color: white;
    border: none;
    padding: 0.8rem 2rem;
    border-radius: 8px;
    font-size: 1.1rem;
    font-weight: bold;
    width: 100%;
    margin: 0.5rem 0;
    cursor: pointer;
    transition: all 0.3s ease;
}
.coach-button:hover {
    background: linear-gradient(90deg, #1976D2, #1565C0);
    transform: translateY(-2px);
}
.understand-button {
    background: linear-gradient(90deg, #FFC107, #FF9800);
    color: white;
    border: none;
    padding: 0.8rem 2rem;
    border-radius: 8px;
    font-size: 1.1rem;
    font-weight: bold;
    width: 100%;
    margin: 0.5rem 0;
    cursor: pointer;
    transition: all 0.3s ease;
}
.understand-button:hover {
    background: linear-gradient(90deg, #FF9800, #F57C00);
    transform: translateY(-2px);
}
</style>
"""

st.markdown(button_style, unsafe_allow_html=True)

with col1:
    if st.button("📤 Coach My Message", use_container_width=True):
        st.session_state.active_mode = "coach"
        st.rerun()

with col2:
    if st.button("📥 Understand Their Message", use_container_width=True):
        st.session_state.active_mode = "translate"
        st.rerun()

# Initialize mode
if 'active_mode' not in st.session_state:
    st.session_state.active_mode = None

# Enhanced message input and processing
if st.session_state.active_mode:
    mode = st.session_state.active_mode
    
    # Mode-specific UI
    if mode == "coach":
        st.markdown('<div class="user-msg"><h4>📤 Your Message to Send</h4><p>I\'ll help you improve this message before you send it.</p></div>', unsafe_allow_html=True)
        message = st.text_area("What do you want to say?", height=120, 
                              placeholder="Type your message here...", 
                              key=f"{mode}_input")
        button_text = "🚀 Improve My Message"
    else:
        st.markdown('<div class="contact-msg"><h4>📥 Message You Received</h4><p>I\'ll help you understand what they really mean and how to respond.</p></div>', unsafe_allow_html=True)
        message = st.text_area("What did they say?", height=120, 
                              placeholder="Paste their message here...", 
                              key=f"{mode}_input")
        button_text = "🔍 Analyze & Respond"
    
    col1, col2 = st.columns([3, 1])
    with col1:
        process_button = st.button(button_text, type="primary")
    with col2:
        if st.button("↩️ Back"):
            st.session_state.active_mode = None
            st.rerun()
    
    if process_button:
        if message.strip():
            with st.spinner("🎙️ The Third Voice is analyzing..."):
                contact = st.session_state.contacts[st.session_state.active_contact]
                result = get_ai_response(message, contact['context'], mode == "translate")
                
                if "error" not in result:
                    # Display The Third Voice response
                    st.markdown("### 🎙️ The Third Voice Response:")
                    
                    if mode == "coach":
                        st.markdown(f'''
                        <div class="ai-response">
                            <h4>✨ Your Improved Message:</h4>
                            <p style="font-size: 1.1rem; line-height: 1.6;">{result["improved"]}</p>
                            <hr>
                            <small><i>💡 Generated by: {result["model"]}</i></small>
                        </div>
                        ''', unsafe_allow_html=True)
                        
                        st.session_state.usage_stats['messages_coached'] += 1
                        
                    else:
                        st.markdown(f'''
                        <div class="ai-response">
                            <h4>🔍 What They Really Mean:</h4>
                            <p style="font-size: 1.1rem; line-height: 1.6;">{result["response"]}</p>
                            <hr>
                            <small><i>💡 Generated by: {result["model"]}</i></small>
                        </div>
                        ''', unsafe_allow_html=True)
                        
                        st.session_state.usage_stats['messages_understood'] += 1
                    
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
                    
                    # Enhanced feedback collection
                    st.markdown("### 📊 How was this response?")
                    
                    feedback_col1, feedback_col2, feedback_col3 = st.columns(3)
                    
                    with feedback_col1:
                        if st.button("👍 Helpful", key=f"good_{history_entry['id']}"):
                            collect_feedback(history_entry['id'], mode, 5, "Helpful")
                            st.success("Thanks for your feedback! 🙏")
                    
                    with feedback_col2:
                        if st.button("👌 Okay", key=f"ok_{history_entry['id']}"):
                            collect_feedback(history_entry['id'], mode, 3, "Okay")
                            st.success("Thanks for your feedback! 🙏")
                    
                    with feedback_col3:
                        if st.button("👎 Not Helpful", key=f"bad_{history_entry['id']}"):
                            collect_feedback(history_entry['id'], mode, 1, "Not helpful")
                            st.success("Thanks for your feedback! We'll improve 🙏")
                    
                    # Additional feedback
                    with st.expander("💭 Share more detailed feedback"):
                        detailed_feedback = st.text_area("What could be improved?", 
                                                        placeholder="Your suggestions help us make The Third Voice better...")
                        if st.button("Submit Feedback"):
                            if detailed_feedback:
                                collect_feedback(history_entry['id'], mode, 3, detailed_feedback)
                                st.success("Thank you for the detailed feedback! 🙏")
                    
                    st.success("✅ Saved to your history")
                    
                else:
                    st.error(f"❌ {result['error']}")
                    
                    # Error feedback
                    st.markdown("### 🛠️ Having issues?")
                    if st.button("Report this error"):
                        collect_feedback("error", "system_error", 1, f"Error: {result['error']}")
                        st.success("Error reported. We'll look into it! 🔧")
        else:
            st.warning("⚠️ Please enter a message first.")

# Enhanced tabs with better features
tab1, tab2, tab3, tab4 = st.tabs(["📜 History", "📘 Journal", "📊 Progress", "ℹ️ About"])

with tab1:
    st.markdown(f"### 📜 Conversation History with {st.session_state.active_contact}")
    contact = st.session_state.contacts[st.session_state.active_contact]
    
    if not contact['history']:
        st.markdown("""
        <div class="onboarding-tip">
            <h4>📝 No messages yet!</h4>
            <p>Start by coaching a message you want to send or understanding a message you received.</p>
            <p><strong>Tip:</strong> Try the buttons above to get started!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Search and filter options
        search_term = st.text_input("🔍 Search history:", placeholder="Search messages...")
        filter_type = st.selectbox("Filter by:", ["All", "Coached Messages", "Understood Messages"])
        
        filtered_history = contact['history']
        
        if search_term:
            filtered_history = [h for h in filtered_history if search_term.lower() in h['original'].lower() or search_term.lower() in h['result'].lower()]
        
        if filter_type == "Coached Messages":
            filtered_history = [h for h in filtered_history if h['type'] == 'coach']
        elif filter_type == "Understood Messages":
            filtered_history = [h for h in filtered_history if h['type'] == 'translate']
        
        st.markdown(f"*Showing {len(filtered_history)} of {len(contact['history'])} messages*")
        
        for i, entry in enumerate(reversed(filtered_history)):
            with st.expander(f"**{entry['time']}** • {entry['type'].title()} • {entry['original'][:50]}..."):
                if entry['type'] == 'coach':
                    st.markdown(f'<div class="user-msg">📤 <strong>Original:</strong> {entry["original"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="ai-response">🎙️ <strong>Improved:</strong> {entry["result"]}<br><small><i>by {entry.get("model", "Unknown")}</i></small></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="contact-msg">📥 <strong>They said:</strong> {entry["original"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="ai-response">🎙️ <strong>Interpretation & Response:</strong> {entry["result"]}<br><small><i>by {entry.get("model", "Unknown")}</i></small></div>', unsafe_allow_html=True)
                
                # Export individual message
                if st.button(f"📄 Export", key=f"export_{i}"):
                    export_data = {
                        "message": entry,
                        "contact": st.session_state.active_contact,
                        "exported_at": datetime.datetime.now().isoformat()
                    }
                    st.download_button(
                        "Download Message",
                        json.dumps(export_data, indent=2),
                        f"message_{entry['time'].replace('/', '-').replace(' ', '_')}.json",
                        "application/json",
                        key=f"download_{i}"
                    )

with tab2:
    st.markdown(f"### 📘 Communication Journal - {st.session_state.active_contact}")
    
    # Enhanced journal with templates
    contact_key = st.session_state.active_contact
    
    if contact_key not in st.session_state.journal_entries:
        st.session_state.journal_entries[contact_key] = {
            'what_worked': '', 'what_didnt': '', 'insights': '', 'patterns': '',
            'goals': '', 'improvements': '', 'relationship_health': ''
        }
    
    journal = st.session_state.journal_entries[contact_key]
    
    # Journal templates
    with st.expander("📝 Journal Templates & Prompts"):
        st.markdown("""
        **Reflection Questions:**
        - What communication patterns do I notice?
        - When do our conversations go well vs. poorly?
        - What triggers misunderstandings?
        - How has my communication improved?
        - What does this person need to feel heard?
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="journal-section">', unsafe_allow_html=True)
        st.markdown("**💚 What's Working Well?**")
        journal['what_worked'] = st.text_area("", value=journal['what_worked'], 
                                            key=f"worked_{contact_key}", height=100,
                                            placeholder="What communication strategies are successful?")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown('<div class="journal-section">', unsafe_allow_html=True)
        st.markdown("**🔍 Patterns I've Noticed**")
        journal['patterns'] = st.text_area("", value=journal['patterns'], 
                                         key=f"patterns_{contact_key}", height=100,
                                         placeholder="What communication patterns do you see?")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown('<div class="journal-section">', unsafe_allow_html=True)
        st.markdown("**🎯 Communication Goals**")
        journal['goals'] = st.text_area("", value=journal['goals'], 
                                       key=f"goals_{contact_key}", height=100,
                                       placeholder="What do you want to improve?")
        st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="journal-section">', unsafe_allow_html=True)
    st.markdown("**⚠️ What Needs Improvement?**")
    
    # Properly call st.text_area
    journal['what_didnt'] = st.text_area(
        "", 
        value=journal['what_didnt'], 
        key=f"didnt_{contact_key}"
    )
    
    # Close the div opened above
    st.markdown("</div>", unsafe_allow_html=True)

# Later, separately for your AI response display:

if mode == "coach":
    st.markdown(f'''
    <div class="ai-response">
        <h4>✨ Your Improved Message:</h4>
        <p style="font-size: 1.1rem; line-height: 1.6;">{result["improved"]}</p>
        <hr>
        <small><i>💡 Generated by {result["model"]}</i></small>
    </div>
    ''', unsafe_allow_html=True)
else:
    st.markdown(f'''
    <div class="ai-response">
        <h4>🔎 Interpretation & Suggested Response:</h4>
        <p style="font-size: 1.1rem; line-height: 1.6;">{result["response"]}</p>
        <hr>
        <small><i>💡 Generated by {result["model"]}</i></small>
    </div>
    ''', unsafe_allow_html=True)
