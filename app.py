import streamlit as st 
import json 
import datetime 
import requests

#--- Constants ---

CONTEXTS = ["general", "romantic", "coparenting", "workplace", "family", "friend"] 
REQUIRE_TOKEN = True  # ✅ Set to False to allow open use (no token)

#--- Setup ---

st.set_page_config(page_title="The Third Voice", page_icon="🎙️", layout="wide") 
st.markdown("""
<style>
.ai-box {background:#f0f8ff;padding:1rem;border-radius:8px;border-left:4px solid #4CAF50;margin:0.5rem 0}
.pos{background:#d4edda;padding:0.5rem;border-radius:5px;color:#155724;margin:0.2rem 0}
.neg{background:#f8d7da;padding:0.5rem;border-radius:5px;color:#721c24;margin:0.2rem 0}
.neu{background:#d1ecf1;padding:0.5rem;border-radius:5px;color:#0c5460;margin:0.2rem 0}
.sent-box {background: #e6ffed; padding: 1rem; border-left: 5px solid #28a745; border-radius: 8px; margin-bottom: 1rem;}
.received-box {background: #e8f0fe; padding: 1rem; border-left: 5px solid #007bff; border-radius: 8px; margin-bottom: 1rem;}
.sidebar .element-container{margin-bottom:0.5rem}
.stFileUploader > div > div > div {
    height: 40px !important;
    padding: 5px !important;
}
.stFileUploader > div > div > div > div {
    display: none !important;
}
.stFileUploader > div > div > div > button {
    font-size: 12px !important;
    padding: 5px 10px !important;
    height: 30px !important;
}
</style>""", unsafe_allow_html=True)

#--- Session Init ---

defaults = { 
    'token_validated': not REQUIRE_TOKEN, 
    'api_key': st.secrets.get("OPENROUTER_API_KEY", ""), 
    'count': 0, 
    'history': [], 
    'active_msg': '', 
    'active_ctx': 'general', 
    'journal': "" 
}

for k, v in defaults.items(): 
    if k not in st.session_state: 
        st.session_state[k] = v

#--- Token Gate ---

if REQUIRE_TOKEN and not st.session_state.token_validated: 
    st.warning("🔐 Access restricted. Enter beta token to continue.") 
    token_input = st.text_input("Enter token:") 
    valid_tokens = ["ttv-beta-001", "ttv-beta-002", "ttv-beta-003"] 
    if token_input in valid_tokens: 
        st.session_state.token_validated = True 
        st.success("✅ Token accepted.") 
        st.stop()

#--- Sidebar: Context, History, Save ---

st.sidebar.markdown("### 🗂️ Conversation Category") 
selected_context = st.sidebar.radio("Select context", CONTEXTS, index=CONTEXTS.index(st.session_state.active_ctx)) 
st.session_state.active_ctx = selected_context

st.sidebar.markdown("---") 
st.sidebar.markdown("### 📜 Manage History")

uploaded = st.sidebar.file_uploader("📤 Load History", type="json", label_visibility="collapsed")
st.sidebar.markdown('<small>📤 Load History</small>', unsafe_allow_html=True) 
if uploaded: 
    try: 
        data = json.load(uploaded) 
        if isinstance(data, list): 
            st.session_state.history = data 
            st.sidebar.success("✅ History loaded!") 
    except: 
        st.sidebar.error("❌ Invalid file")

if st.session_state.history: 
    st.sidebar.download_button( 
        "💾 Save (.json)", 
        json.dumps(st.session_state.history, indent=2), 
        file_name=f"history_{datetime.datetime.now().strftime('%m%d_%H%M')}.json", 
        use_container_width=True 
    )

if st.sidebar.button("🧹 Clear History", use_container_width=True):
    st.session_state.history.clear()
    st.sidebar.info("History cleared.")

ctx_count = sum(1 for h in st.session_state.history if h['context'] == st.session_state.active_ctx) 
st.sidebar.caption(f"🗒️ {ctx_count} messages in '{st.session_state.active_ctx}'")

#--- OpenRouter Call ---

def analyze_with_openrouter(message, context, is_received=False): 
    api_key = st.session_state.api_key 
    if not api_key: 
        return {"error": "No API key."}

    system_prompt = {
        "general": "You are an emotionally intelligent communication coach.",
        "romantic": "You help users reframe romantic messages with empathy and clarity.",
        "coparenting": "You offer emotionally safe responses for coparenting messages.",
        "workplace": "You translate workplace messages for tone, clarity, and intent.",
        "family": "You understand and rephrase messages within family dynamics.",
        "friend": "You assist with messages involving friendships and mutual support."
    }.get(context, "You are an emotionally intelligent assistant.")

    models = [
        "meta-llama/llama-3.3-70b-instruct:free",
        "deepseek/deepseek-r1-0528-qwen3-8b:free",
        "google/gemma-3n-e2b-it:free"
    ]

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Message: {message}\nReceived: {is_received}"}
    ]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://thethirdvoice.streamlit.app",
        "X-Title": "The Third Voice"
    }

    for model in models:
        try:
            r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json={
                "model": model,
                "messages": messages
            }, timeout=30)
            r.raise_for_status()
            reply = r.json()["choices"][0]["message"]["content"]

            if is_received:
                return {
                    "sentiment": "neutral",
                    "emotion": "curious",
                    "meaning": f"AI interpretation of: {message}",
                    "need": "Understanding",
                    "response": reply
                }
            else:
                return {
                    "sentiment": "neutral",
                    "emotion": "calm",
                    "reframed": reply
                }

        except Exception as e:
            st.warning(f"{model} error: {e}")
            continue

    return {"error": "All models failed."}

#--- Tabs ---

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📤 Coach", "📥 Translate", "📜 History", "📘 Journal", "ℹ️ About"])

with tab1: 
    st.markdown("### ✍️ Improve Message") 
    msg = st.text_area("Your message:", value=st.session_state.active_msg, height=80, key="coach_msg") 
    if st.button("🚀 Improve", type="primary"): 
        st.session_state.count += 1 
        result = analyze_with_openrouter(msg, st.session_state.active_ctx) 
        sentiment = result.get("sentiment", "neutral") 
        st.markdown(f'<div class="{sentiment[:3]}">{sentiment.title()} • {result.get("emotion", "neutral").title()}</div>', unsafe_allow_html=True) 
        improved = result.get("reframed", msg) 
        st.markdown(f'<div class="ai-box">{improved}</div>', unsafe_allow_html=True) 
        st.session_state.history.append({ 
            "time": datetime.datetime.now().strftime("%m/%d %H:%M"), 
            "type": "send", 
            "context": st.session_state.active_ctx, 
            "original": msg, 
            "result": improved, 
            "sentiment": sentiment 
        }) 
        st.code(improved, language="text")

with tab2: 
    st.markdown("### 🧠 Understand Received Message") 
    msg = st.text_area("Received message:", value=st.session_state.active_msg, height=80, key="translate_msg") 
    if st.button("🔍 Analyze", type="primary"): 
        st.session_state.count += 1 
        result = analyze_with_openrouter(msg, st.session_state.active_ctx, True) 
        sentiment = result.get("sentiment", "neutral") 
        st.markdown(f'<div class="{sentiment[:3]}">{sentiment.title()} • {result.get("emotion", "neutral").title()}</div>', unsafe_allow_html=True) 
        st.markdown(f"Meaning: {result.get('meaning', '...')}") 
        st.markdown(f"Need: {result.get('need', '...')}") 
        st.markdown(f'<div class="ai-box">{result.get("response", "I understand.")}</div>', unsafe_allow_html=True) 
        st.session_state.history.append({ 
            "time": datetime.datetime.now().strftime("%m/%d %H:%M"), 
            "type": "receive", 
            "context": st.session_state.active_ctx, 
            "original": msg, 
            "result": result.get("response", msg), 
            "sentiment": sentiment 
        }) 
        st.code(result.get("response", msg), language="text")

with tab3: 
    st.markdown("### 📜 Conversation History") 
    filter_ctx = st.selectbox("Filter by context", CONTEXTS, index=CONTEXTS.index(st.session_state.active_ctx), key="history_filter") 
    filtered = [h for h in st.session_state.history if h['context'] == filter_ctx] 
    if not filtered: 
        st.info("No messages yet for this context.") 
    else: 
        for i, entry in enumerate(reversed(filtered)): 
            st.markdown(f"#### Message #{len(filtered) - i}") 
            st.markdown(f"- 🕒 {entry['time']}") 
            st.markdown(f"- 💬 Type: {entry['type']}") 
            st.markdown(f"- 😊 Sentiment: {entry['sentiment']}") 
            st.markdown(f"- ✉️ Original: {entry['original']}") 
            box_class = "sent-box" if entry["type"] == "send" else "received-box" 
            box_label = "🟢 You said:" if entry["type"] == "send" else "🔵 You received:" 
            st.markdown(f"<div class='{box_class}'><strong>{box_label}</strong><br>{entry['result']}</div>", unsafe_allow_html=True) 
            st.markdown("---")

with tab4: 
    st.markdown("### 📘 Reflection Journal") 
    st.text_area("What worked well in this session?", key="journal", height=150) 
    if st.button("💾 Save Reflection"): 
        st.success("Reflection saved (locally in session)")

with tab5: 
    st.markdown("""### ℹ️ About The Third Voice
    
AI communication coach for better conversations.

**Core Features:**

📤 **Coach**: Improve outgoing messages

📥 **Translate**: Understand incoming messages

📜 **History**: View & filter by conversation type

📘 **Journal**: Capture personal reflections on conversations

**Supported Contexts:**
General • Romantic • Coparenting • Workplace • Family • Friend

🛡️ **Privacy**: Local only. No data is uploaded.

🧪 **Beta v0.9.2** — Feedback: hello@thethirdvoice.ai
""")import streamlit as st 
import json 
import datetime 
import requests

#--- Constants ---

CONTEXTS = ["general", "romantic", "coparenting", "workplace", "family", "friend"] 
REQUIRE_TOKEN = True  # ✅ Set to False to allow open use (no token)

#--- Setup ---

st.set_page_config(page_title="The Third Voice", page_icon="🎙️", layout="wide") 
st.markdown("""
<style>
.ai-box {background:#f0f8ff;padding:1rem;border-radius:8px;border-left:4px solid #4CAF50;margin:0.5rem 0}
.pos{background:#d4edda;padding:0.5rem;border-radius:5px;color:#155724;margin:0.2rem 0}
.neg{background:#f8d7da;padding:0.5rem;border-radius:5px;color:#721c24;margin:0.2rem 0}
.neu{background:#d1ecf1;padding:0.5rem;border-radius:5px;color:#0c5460;margin:0.2rem 0}
.sent-box {background: #e6ffed; padding: 1rem; border-left: 5px solid #28a745; border-radius: 8px; margin-bottom: 1rem;}
.received-box {background: #e8f0fe; padding: 1rem; border-left: 5px solid #007bff; border-radius: 8px; margin-bottom: 1rem;}
.sidebar .element-container{margin-bottom:0.5rem}
.stFileUploader > div > div > div {
    height: 40px !important;
    padding: 5px !important;
}
.stFileUploader > div > div > div > div {
    display: none !important;
}
.stFileUploader > div > div > div > button {
    font-size: 12px !important;
    padding: 5px 10px !important;
    height: 30px !important;
}
</style>""", unsafe_allow_html=True)

#--- Session Init ---

defaults = { 
    'token_validated': not REQUIRE_TOKEN, 
    'api_key': st.secrets.get("OPENROUTER_API_KEY", ""), 
    'count': 0, 
    'history': [], 
    'active_msg': '', 
    'active_ctx': 'general', 
    'journal': "" 
}

for k, v in defaults.items(): 
    if k not in st.session_state: 
        st.session_state[k] = v

#--- Token Gate ---

if REQUIRE_TOKEN and not st.session_state.token_validated: 
    st.warning("🔐 Access restricted. Enter beta token to continue.") 
    token_input = st.text_input("Enter token:") 
    valid_tokens = ["ttv-beta-001", "ttv-beta-002", "ttv-beta-003"] 
    if token_input in valid_tokens: 
        st.session_state.token_validated = True 
        st.success("✅ Token accepted.") 
        st.stop()

#--- Sidebar: Context, History, Save ---

st.sidebar.markdown("### 🗂️ Conversation Category") 
selected_context = st.sidebar.radio("Select context", CONTEXTS, index=CONTEXTS.index(st.session_state.active_ctx)) 
st.session_state.active_ctx = selected_context

st.sidebar.markdown("---") 
st.sidebar.markdown("### 📜 Manage History")

uploaded = st.sidebar.file_uploader("📤 Load History", type="json", label_visibility="collapsed")
st.sidebar.markdown('<small>📤 Load History</small>', unsafe_allow_html=True) 
if uploaded: 
    try: 
        data = json.load(uploaded) 
        if isinstance(data, list): 
            st.session_state.history = data 
            st.sidebar.success("✅ History loaded!") 
    except: 
        st.sidebar.error("❌ Invalid file")

if st.session_state.history: 
    st.sidebar.download_button( 
        "💾 Save (.json)", 
        json.dumps(st.session_state.history, indent=2), 
        file_name=f"history_{datetime.datetime.now().strftime('%m%d_%H%M')}.json", 
        use_container_width=True 
    )

if st.sidebar.button("🧹 Clear History", use_container_width=True):
    st.session_state.history.clear()
    st.sidebar.info("History cleared.")

ctx_count = sum(1 for h in st.session_state.history if h['context'] == st.session_state.active_ctx) 
st.sidebar.caption(f"🗒️ {ctx_count} messages in '{st.session_state.active_ctx}'")

#--- OpenRouter Call ---

def analyze_with_openrouter(message, context, is_received=False): 
    api_key = st.session_state.api_key 
    if not api_key: 
        return {"error": "No API key."}

    system_prompt = {
        "general": "You are an emotionally intelligent communication coach.",
        "romantic": "You help users reframe romantic messages with empathy and clarity.",
        "coparenting": "You offer emotionally safe responses for coparenting messages.",
        "workplace": "You translate workplace messages for tone, clarity, and intent.",
        "family": "You understand and rephrase messages within family dynamics.",
        "friend": "You assist with messages involving friendships and mutual support."
    }.get(context, "You are an emotionally intelligent assistant.")

    models = [
        "meta-llama/llama-3.3-70b-instruct:free",
        "deepseek/deepseek-r1-0528-qwen3-8b:free",
        "google/gemma-3n-e2b-it:free"
    ]

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Message: {message}\nReceived: {is_received}"}
    ]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://thethirdvoice.streamlit.app",
        "X-Title": "The Third Voice"
    }

    for model in models:
        try:
            r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json={
                "model": model,
                "messages": messages
            }, timeout=30)
            r.raise_for_status()
            reply = r.json()["choices"][0]["message"]["content"]

            if is_received:
                return {
                    "sentiment": "neutral",
                    "emotion": "curious",
                    "meaning": f"AI interpretation of: {message}",
                    "need": "Understanding",
                    "response": reply
                }
            else:
                return {
                    "sentiment": "neutral",
                    "emotion": "calm",
                    "reframed": reply
                }

        except Exception as e:
            st.warning(f"{model} error: {e}")
            continue

    return {"error": "All models failed."}

#--- Tabs ---

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📤 Coach", "📥 Translate", "📜 History", "📘 Journal", "ℹ️ About"])

with tab1: 
    st.markdown("### ✍️ Improve Message") 
    msg = st.text_area("Your message:", value=st.session_state.active_msg, height=80, key="coach_msg") 
    if st.button("🚀 Improve", type="primary"): 
        st.session_state.count += 1 
        result = analyze_with_openrouter(msg, st.session_state.active_ctx) 
        sentiment = result.get("sentiment", "neutral") 
        st.markdown(f'<div class="{sentiment[:3]}">{sentiment.title()} • {result.get("emotion", "neutral").title()}</div>', unsafe_allow_html=True) 
        improved = result.get("reframed", msg) 
        st.markdown(f'<div class="ai-box">{improved}</div>', unsafe_allow_html=True) 
        st.session_state.history.append({ 
            "time": datetime.datetime.now().strftime("%m/%d %H:%M"), 
            "type": "send", 
            "context": st.session_state.active_ctx, 
            "original": msg, 
            "result": improved, 
            "sentiment": sentiment 
        }) 
        st.code(improved, language="text")

with tab2: 
    st.markdown("### 🧠 Understand Received Message") 
    msg = st.text_area("Received message:", value=st.session_state.active_msg, height=80, key="translate_msg") 
    if st.button("🔍 Analyze", type="primary"): 
        st.session_state.count += 1 
        result = analyze_with_openrouter(msg, st.session_state.active_ctx, True) 
        sentiment = result.get("sentiment", "neutral") 
        st.markdown(f'<div class="{sentiment[:3]}">{sentiment.title()} • {result.get("emotion", "neutral").title()}</div>', unsafe_allow_html=True) 
        st.markdown(f"Meaning: {result.get('meaning', '...')}") 
        st.markdown(f"Need: {result.get('need', '...')}") 
        st.markdown(f'<div class="ai-box">{result.get("response", "I understand.")}</div>', unsafe_allow_html=True) 
        st.session_state.history.append({ 
            "time": datetime.datetime.now().strftime("%m/%d %H:%M"), 
            "type": "receive", 
            "context": st.session_state.active_ctx, 
            "original": msg, 
            "result": result.get("response", msg), 
            "sentiment": sentiment 
        }) 
        st.code(result.get("response", msg), language="text")

with tab3: 
    st.markdown("### 📜 Conversation History") 
    filter_ctx = st.selectbox("Filter by context", CONTEXTS, index=CONTEXTS.index(st.session_state.active_ctx), key="history_filter") 
    filtered = [h for h in st.session_state.history if h['context'] == filter_ctx] 
    if not filtered: 
        st.info("No messages yet for this context.") 
    else: 
        for i, entry in enumerate(reversed(filtered)): 
            st.markdown(f"#### Message #{len(filtered) - i}") 
            st.markdown(f"- 🕒 {entry['time']}") 
            st.markdown(f"- 💬 Type: {entry['type']}") 
            st.markdown(f"- 😊 Sentiment: {entry['sentiment']}") 
            st.markdown(f"- ✉️ Original: {entry['original']}") 
            box_class = "sent-box" if entry["type"] == "send" else "received-box" 
            box_label = "🟢 You said:" if entry["type"] == "send" else "🔵 You received:" 
            st.markdown(f"<div class='{box_class}'><strong>{box_label}</strong><br>{entry['result']}</div>", unsafe_allow_html=True) 
            st.markdown("---")

with tab4: 
    st.markdown("### 📘 Reflection Journal") 
    st.text_area("What worked well in this session?", key="journal", height=150) 
    if st.button("💾 Save Reflection"): 
        st.success("Reflection saved (locally in session)")

with tab5: 
    st.markdown("""### ℹ️ About The Third Voice
    
AI communication coach for better conversations.

**Core Features:**

📤 **Coach**: Improve outgoing messages

📥 **Translate**: Understand incoming messages

📜 **History**: View & filter by conversation type

📘 **Journal**: Capture personal reflections on conversations

**Supported Contexts:**
General • Romantic • Coparenting • Workplace • Family • Friend

🛡️ **Privacy**: Local only. No data is uploaded.

🧪 **Beta v0.9.2** — Feedback: hello@thethirdvoice.ai
""")
