import streamlit as st import requests import json import datetime

--- Constants ---

CONTEXTS = ["general", "romantic", "coparenting", "workplace", "family", "friend"] MODELS = { "Mixtral 8x7B": "mistral/mixtral-8x7b-instruct", "Claude 3 Sonnet": "anthropic/claude-3-sonnet", "LLaMA 3 8B": "meta-llama/llama-3-8b-instruct" }

--- Session Init ---

def default_session(): return { 'token_validated': False, 'count': 0, 'history': [], 'active_msg': '', 'active_ctx': 'general', 'model': list(MODELS.values())[0], 'mock_mode': False }

for key, val in default_session().items(): if key not in st.session_state: st.session_state[key] = val

--- Token Gate ---

if not st.session_state.token_validated: token = st.text_input("🔑 Beta Token:", type="password") if token in ["ttv-beta-001", "ttv-beta-002", "ttv-beta-003"]: st.session_state.token_validated = True st.success("✅ Welcome!") st.rerun() elif token: st.error("❌ Invalid token") st.stop()

--- Page Setup ---

st.set_page_config(page_title="The Third Voice", page_icon="🎙️", layout="wide")

st.markdown("""

<style>
.ai-box {background:#f0f8ff;padding:1rem;border-radius:8px;border-left:4px solid #4CAF50;margin:0.5rem 0}
.pos{background:#d4edda;padding:0.5rem;border-radius:5px;color:#155724;margin:0.2rem 0}
.neg{background:#f8d7da;padding:0.5rem;border-radius:5px;color:#721c24;margin:0.2rem 0}
.neu{background:#d1ecf1;padding:0.5rem;border-radius:5px;color:#0c5460;margin:0.2rem 0}
.sidebar .element-container{margin-bottom:0.5rem}
</style>""", unsafe_allow_html=True)

--- Sidebar ---

st.sidebar.title("🧠 The Third Voice") st.sidebar.markdown("### 🗂️ Conversation Category") selected_context = st.sidebar.radio("Select context", CONTEXTS, index=CONTEXTS.index(st.session_state.active_ctx)) st.session_state.active_ctx = selected_context

st.sidebar.markdown("### 🧠 Choose AI Model") model_label = st.sidebar.selectbox("Model:", list(MODELS.keys())) st.session_state.model = MODELS[model_label]

st.sidebar.checkbox("🧪 Mock mode (no AI call)", key="mock_mode")

st.sidebar.markdown("### 📜 History Management") uploaded = st.sidebar.file_uploader("📤 Load (.json)", type="json") if uploaded: try: st.session_state.history = json.load(uploaded) st.sidebar.success("✅ History loaded!") except: st.sidebar.error("❌ Invalid file")

if st.session_state.history: st.sidebar.download_button( "💾 Save (.json)", json.dumps(st.session_state.history, indent=2), file_name=f"history_{datetime.datetime.now().strftime('%m%d_%H%M')}.json", use_container_width=True )

--- Analyze Function (OpenRouter or Mock) ---

def analyze(msg, ctx, is_received=False): if st.session_state.mock_mode: return { "sentiment": "neutral", "emotion": "calm", "reframed": f"(Mock) {msg[::-1]}", "meaning": "(Mock meaning)", "need": "(Mock need)", "response": f"(Mock) Got your message: {msg}" }

try:
    prompt = f"Context: {ctx}. Reframe message: '{msg}'" if not is_received else f"Context: {ctx}. Analyze: '{msg}'"
    payload = {
        "model": st.session_state.model,
        "messages": [{"role": "user", "content": prompt}]
    }
    headers = {
        "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
        "HTTP-Referer": "https://thethirdvoice.ai",
        "X-Title": "The Third Voice MVP"
    }
    res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    reply = res.json()["choices"][0]["message"]["content"]
    # Parse reply or assume JSON
    try:
        return json.loads(reply)
    except:
        return {
            "sentiment": "neutral", "emotion": "unknown",
            "reframed": reply, "meaning": "...", "need": "...", "response": reply
        }
except Exception as e:
    st.warning(f"⚠️ AI error: {e}")
    return {
        "sentiment": "neutral", "emotion": "error",
        "reframed": msg, "meaning": "?", "need": "?", "response": "Sorry, something went wrong."
    }

--- Tabs ---

tab1, tab2, tab3, tab4 = st.tabs(["📤 Coach", "📥 Translate", "📜 History", "ℹ️ About"])

--- Coach Tab ---

with tab1: st.markdown("### ✍️ Improve Your Message") msg = st.text_area("Your message:", value=st.session_state.active_msg, height=80, key="coach_msg") if st.button("🚀 Improve", type="primary") and msg.strip(): st.session_state.count += 1 result = analyze(msg, st.session_state.active_ctx) sentiment = result.get("sentiment", "neutral") st.markdown(f'<div class="{sentiment[:3]}">{sentiment.title()} • {result.get("emotion", "mixed").title()}</div>', unsafe_allow_html=True) improved = result.get("reframed", msg) st.markdown(f'<div class="ai-box">{improved}</div>', unsafe_allow_html=True) st.session_state.history.append({ "time": datetime.datetime.now().strftime("%m/%d %H:%M"), "type": "send", "context": st.session_state.active_ctx, "original": msg, "result": improved, "sentiment": sentiment, "model": model_label })

--- Translate Tab ---

with tab2: st.markdown("### 🧠 Understand a Message You Received") msg = st.text_area("Received message:", value=st.session_state.active_msg, height=80, key="translate_msg") if st.button("🔍 Analyze", type="primary") and msg.strip(): st.session_state.count += 1 result = analyze(msg, st.session_state.active_ctx, True) sentiment = result.get("sentiment", "neutral") st.markdown(f'<div class="{sentiment[:3]}">{sentiment.title()} • {result.get("emotion", "mixed").title()}</div>', unsafe_allow_html=True) st.markdown(f"Meaning: {result.get('meaning', '...')}") st.markdown(f"Need: {result.get('need', '...')}") st.markdown(f'<div class="ai-box">{result.get('response', msg)}</div>', unsafe_allow_html=True) st.session_state.history.append({ "time": datetime.datetime.now().strftime("%m/%d %H:%M"), "type": "receive", "context": st.session_state.active_ctx, "original": msg, "result": result.get("response", msg), "sentiment": sentiment, "model": model_label })

--- History Tab ---

with tab3: st.markdown("### 📜 Conversation History") filter_ctx = st.selectbox("Filter by context:", CONTEXTS, index=CONTEXTS.index(st.session_state.active_ctx), key="filter") filtered = [h for h in st.session_state.history if h['context'] == filter_ctx] if not filtered: st.info("No messages for this context.") else: for i, entry in enumerate(reversed(filtered)): st.markdown(f"#### Message #{len(filtered)-i}") st.markdown(f"- 🕒 {entry['time']}") st.markdown(f"- 📤 Type: {entry['type']} | 🤖 Model: {entry['model']}") st.markdown(f"- 💬 Message: {entry['original']}") st.markdown(f"<div class='ai-box'>{entry['result']}</div>", unsafe_allow_html=True) st.markdown("---")

--- About Tab ---

with tab4: st.markdown("""### ℹ️ About The Third Voice AI-powered communication coach.

Features:

Coach your messages before sending

Translate messages you receive

Filterable conversation history

Supports multiple AI models (Claude, Mixtral, LLaMA)


Beta MVP v0.9.5 — Built by Predrag & Co-Founder GPT 😊 """)

