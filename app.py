import streamlit as st
import json
import datetime
import requests

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
</style>""", unsafe_allow_html=True)

# Session defaults
defaults = {
    'token_validated': not REQUIRE_TOKEN,
    'api_key': st.secrets.get("OPENROUTER_API_KEY", ""),
    'contacts': {'General': {'context': 'general', 'history': []}},
    'active_contact': 'General',
    'journal_entries': {}
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Token gate
if REQUIRE_TOKEN and not st.session_state.token_validated:
    st.warning("🔐 Access restricted. Enter beta token to continue.")
    token = st.text_input("Token:")
    if token in ["ttv-beta-001", "ttv-beta-002", "ttv-beta-003"]:
        st.session_state.token_validated = True
        st.success("✅ Authorized")
        st.rerun()
    st.stop()

# API function
def get_ai_response(message, context, is_received=False):
    if not st.session_state.api_key:
        return {"error": "No API key"}
    
    prompts = {
        "general": "You are an emotionally intelligent communication coach.",
        "romantic": "You help reframe romantic messages with empathy and clarity.",
        "coparenting": "You offer emotionally safe responses for coparenting.",
        "workplace": "You translate workplace messages for tone and intent.",
        "family": "You understand family dynamics and rephrase accordingly.",
        "friend": "You assist with friendship communication."
    }
    
    system_prompt = prompts.get(context, prompts["general"])
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Message: {message}\nReceived: {is_received}"}
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
        except:
            continue
    
    return {"error": "All models failed"}

# Sidebar - Contact Management
st.sidebar.markdown("### 👥 Your Contacts")

# Add new contact
with st.sidebar.expander("➕ Add Contact"):
    new_name = st.text_input("Name:")
    new_context = st.selectbox("Relationship:", CONTEXTS)
    if st.button("Add") and new_name:
        st.session_state.contacts[new_name] = {'context': new_context, 'history': []}
        st.session_state.active_contact = new_name
        st.success(f"Added {new_name}")
        st.rerun()

# Contact selection
contact_names = list(st.session_state.contacts.keys())
if contact_names:
    selected = st.sidebar.radio("Select Contact:", contact_names, 
                               index=contact_names.index(st.session_state.active_contact))
    st.session_state.active_contact = selected

# Contact info
if st.session_state.active_contact in st.session_state.contacts:
    contact = st.session_state.contacts[st.session_state.active_contact]
    st.sidebar.markdown(f"**Context:** {contact['context']}")
    st.sidebar.markdown(f"**Messages:** {len(contact['history'])}")

# File management
st.sidebar.markdown("---")
uploaded = st.sidebar.file_uploader("📤 Load History", type="json")
if uploaded:
    try:
        data = json.load(uploaded)
        st.session_state.contacts = data.get('contacts', st.session_state.contacts)
        st.session_state.journal_entries = data.get('journal_entries', {})
        st.sidebar.success("✅ Loaded!")
    except:
        st.sidebar.error("❌ Invalid file")

if st.sidebar.button("💾 Save All"):
    save_data = {
        'contacts': st.session_state.contacts,
        'journal_entries': st.session_state.journal_entries
    }
    filename = f"third_voice_{datetime.datetime.now().strftime('%m%d_%H%M')}.json"
    st.sidebar.download_button(
        "📥 Download File", 
        json.dumps(save_data, indent=2),
        filename,
        "application/json",
        use_container_width=True
    )

# Header with logo and branding
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("logo.png", width=200)
    except:
        st.markdown("# 🎙️")
    st.markdown("<div style='text-align: center'><i>Created by Predrag Mirković</i></div>", unsafe_allow_html=True)

st.markdown(f"### 💬 Communicating with: **{st.session_state.active_contact}**")

# Main action buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("📤 Coach My Message", type="primary", use_container_width=True):
        st.session_state.active_mode = "coach"
with col2:
    if st.button("📥 Understand Their Message", type="primary", use_container_width=True):
        st.session_state.active_mode = "translate"

# Initialize mode
if 'active_mode' not in st.session_state:
    st.session_state.active_mode = None

# Message input and processing
if st.session_state.active_mode:
    mode = st.session_state.active_mode
    label = "Your message to send:" if mode == "coach" else "Message you received:"
    
    # Color-coded input area
    input_class = "user-msg" if mode == "coach" else "contact-msg"
    st.markdown(f'<div class="{input_class}"><strong>{"📤 Your message:" if mode == "coach" else "📥 Their message:"}</strong></div>', unsafe_allow_html=True)
    
    message = st.text_area(label, height=120, key=f"{mode}_input", label_visibility="collapsed")
    
    if st.button(f"{'🚀 Improve' if mode == 'coach' else '🔍 Analyze'}", type="secondary"):
        if message:
            with st.spinner("The Third Voice is analyzing..."):
                contact = st.session_state.contacts[st.session_state.active_contact]
                result = get_ai_response(message, contact['context'], mode == "translate")
                
                if "error" not in result:
                    # Display The Third Voice response
                    st.markdown("### 🎙️ The Third Voice says:")
                    
                    if mode == "coach":
                        st.markdown(f'<div class="ai-response"><strong>Your improved message:</strong><br><br>{result["improved"]}<br><br><small><i>Generated by: {result["model"]}</i></small></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="ai-response"><strong>What they really mean:</strong><br>{result["meaning"]}<br><br><strong>How to respond:</strong><br>{result["response"]}<br><br><small><i>Generated by: {result["model"]}</i></small></div>', unsafe_allow_html=True)
                    
                    # Save to history
                    history_entry = {
                        "time": datetime.datetime.now().strftime("%m/%d %H:%M"),
                        "type": mode,
                        "original": message,
                        "result": result.get("improved" if mode == "coach" else "response", ""),
                        "sentiment": result.get("sentiment", "neutral"),
                        "model": result.get("model", "Unknown")
                    }
                    
                    contact['history'].append(history_entry)
                    st.success("✅ Saved to history")
                else:
                    st.error(f"Sorry, I couldn't process that: {result['error']}")
        else:
            st.warning("Please enter a message first.")

# Tabs for additional features
tab1, tab2, tab3 = st.tabs(["📜 History", "📘 Journal", "ℹ️ About"])

with tab1:
    st.markdown(f"### 📜 History with {st.session_state.active_contact}")
    contact = st.session_state.contacts[st.session_state.active_contact]
    
    if not contact['history']:
        st.info(f"No messages yet with {st.session_state.active_contact}.")
    else:
        for i, entry in enumerate(reversed(contact['history'])):
            st.markdown(f"**{entry['time']}** • {entry['type'].title()}")
            
            # Original message
            if entry['type'] == 'coach':
                st.markdown(f'<div class="user-msg">📤 You wanted to send: {entry["original"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="ai-response">🎙️ Third Voice improved: {entry["result"]}<br><small><i>by {entry.get("model", "Unknown")}</i></small></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="contact-msg">📥 They sent: {entry["original"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="ai-response">🎙️ Third Voice interpreted: {entry["result"]}<br><small><i>by {entry.get("model", "Unknown")}</i></small></div>', unsafe_allow_html=True)
            
            st.markdown("---")

with tab2:
    st.markdown(f"### 📘 Communication Journal - {st.session_state.active_contact}")
    contact_key = st.session_state.active_contact
    
    if contact_key not in st.session_state.journal_entries:
        st.session_state.journal_entries[contact_key] = {
            'what_worked': '', 'what_didnt': '', 'insights': '', 'patterns': ''
        }
    
    journal = st.session_state.journal_entries[contact_key]
    
    st.markdown('<div class="journal-section">', unsafe_allow_html=True)
    st.markdown("**What communication strategies worked well?**")
    journal['what_worked'] = st.text_area("", value=journal['what_worked'], key=f"worked_{contact_key}", height=80)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('<div class="journal-section">', unsafe_allow_html=True)
    st.markdown("**What didn't work or caused issues?**")
    journal['what_didnt'] = st.text_area("", value=journal['what_didnt'], key=f"didnt_{contact_key}", height=80)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('<div class="journal-section">', unsafe_allow_html=True)
    st.markdown("**Key insights about this relationship?**")
    journal['insights'] = st.text_area("", value=journal['insights'], key=f"insights_{contact_key}", height=80)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('<div class="journal-section">', unsafe_allow_html=True)
    st.markdown("**Communication patterns noticed?**")
    journal['patterns'] = st.text_area("", value=journal['patterns'], key=f"patterns_{contact_key}", height=80)
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown("""### ℹ️ About The Third Voice
    
**The communication coach that's there when you need it most.**

Instead of repairing relationships after miscommunication damage, The Third Voice helps you communicate better in real-time.

**How it works:**
1. **Select your contact** - Each relationship gets personalized coaching
2. **Coach your messages** - Improve what you're about to send
3. **Understand their messages** - Decode the real meaning behind their words
4. **Build better patterns** - Journal and learn from each interaction

**Privacy First:** All data stays on your device. Save and load your own files.

**Beta v0.9.3** — Built with ❤️ to heal relationships through better communication.

*"When both people are talking from pain, someone needs to be the third voice."*
""")
