import streamlit as st
import requests
import json
import datetime

# --- Constants ---
CONTEXTS = ["general", "romantic", "coparenting", "workplace", "family", "friend"]
DEFAULT_MODEL = "openrouter/mistral:instruct"

# --- Session State Initialization ---
defaults = {
    'token_validated': True,
    'api_key': '',  # user will input
    'count': 0,
    'history': [],
    'active_msg': '',
    'active_ctx': 'general'
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- Page Setup ---
st.set_page_config(page_title="The Third Voice", page_icon="🎙️", layout="wide")
st.markdown("""
<style>
.ai-box {background:#f0f8ff;padding:1rem;border-radius:8px;border-left:4px solid #4CAF50;margin:0.5rem 0}
.pos{background:#d4edda;padding:0.5rem;border-radius:5px;color:#155724;margin:0.2rem 0}
.neg{background:#f8d7da;padding:0.5rem;border-radius:5px;color:#721c24;margin:0.2rem 0}
.neu{background:#d1ecf1;padding:0.5rem;border-radius:5px;color:#0c5460;margin:0.2rem 0}
.sidebar .element-container{margin-bottom:0.5rem}
</style>
""", unsafe_allow_html=True)

# --- OpenRouter LLM Call ---
def call_openrouter(prompt: str, model: str = DEFAULT_MODEL) -> str:
    if not st.session_state.api_key:
        return "⚠️ No API key provided."
    headers = {
        "Authorization": f"Bearer {st.session_state.api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"❌ Error: {str(e)}"

# --- Sidebar ---
st.sidebar.title("The Third Voice")
st.sidebar.markdown("### 🔑 OpenRouter API Key")
api_input = st.sidebar.text_input("Paste API key here", type="password")
if api_input:
    st.session_state.api_key = api_input.strip()
st.sidebar.markdown("### 🗂️ Conversation Context")
ctx = st.sidebar.radio("Select context", CONTEXTS, index=CONTEXTS.index(st.session_state.active_ctx))
st.session_state.active_ctx = ctx

# --- File Upload / Download ---
st.sidebar.markdown("---")
uploaded = st.sidebar.file_uploader("📤 Load History (.json)", type="json")
if uploaded:
    try:
        history_data = json.load(uploaded)
        st.session_state.history = history_data
        st.sidebar.success("✅ History loaded!")
    except:
        st.sidebar.error("❌ Failed to load history")

if st.session_state.history:
    st.sidebar.download_button(
        "💾 Save History",
        data=json.dumps(st.session_state.history, indent=2),
        file_name=f"history_{datetime.datetime.now().strftime('%m%d_%H%M')}.json",
        use_container_width=True
    )
    if st.sidebar.button("🧹 Clear History", use_container_width=True):
        st.session_state.history.clear()
        st.sidebar.info("History cleared.")

# --- Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["📤 Coach", "📥 Translate", "📜 History", "ℹ️ About"])

# --- Coach Tab ---
with tab1:
    st.markdown("### ✍️ Improve Your Message")
    msg = st.text_area("Your message:", key="coach_msg")
    if st.button("🚀 Improve", type="primary"):
        st.session_state.count += 1
        prompt = f"""You're an AI communication coach. Rephrase this message in a more thoughtful, respectful, and clear way. Context: {ctx}. Message: {msg}"""
        result = call_openrouter(prompt)
        st.markdown(f'<div class="ai-box">{result}</div>', unsafe_allow_html=True)
        st.session_state.history.append({
            "time": datetime.datetime.now().strftime("%m/%d %H:%M"),
            "type": "send",
            "context": ctx,
            "original": msg,
            "result": result
        })
        st.code(result)

# --- Translate Tab ---
with tab2:
    st.markdown("### 🧠 Understand a Received Message")
    msg = st.text_area("Received message:", key="translate_msg")
    if st.button("🔍 Analyze", type="primary"):
        st.session_state.count += 1
        prompt = f"""You're an AI mediator. Help understand this message. Provide emotional tone, possible meaning, and a respectful reply. Context: {ctx}. Message: {msg}"""
        result = call_openrouter(prompt)
        st.markdown(f'<div class="ai-box">{result}</div>', unsafe_allow_html=True)
        st.session_state.history.append({
            "time": datetime.datetime.now().strftime("%m/%d %H:%M"),
            "type": "receive",
            "context": ctx,
            "original": msg,
            "result": result
        })
        st.code(result)

# --- History Tab ---
with tab3:
    st.markdown("### 📜 Message History")
    filter_ctx = st.selectbox("Filter by context", CONTEXTS, index=CONTEXTS.index(ctx))
    messages = [h for h in st.session_state.history if h["context"] == filter_ctx]
    if not messages:
        st.info("No messages for this context.")
    for i, h in enumerate(reversed(messages), 1):
        st.markdown(f"#### #{len(messages) - i + 1}")
        st.markdown(f"- ⏰ `{h['time']}`")
        st.markdown(f"- 🔁 **Type:** `{h['type']}`")
        st.markdown(f"- 💬 **Original:** {h['original']}`")
        st.markdown(f'<div class="ai-box">{h["result"]}</div>', unsafe_allow_html=True)
        st.markdown("---")

# --- About Tab ---
with tab4:
    st.markdown("""
### ℹ️ About The Third Voice

**The Third Voice** is a communication assistant that helps you:
- 📤 Reframe your own messages
- 📥 Interpret others' messages with empathy
- 🧠 Stay emotionally aware during difficult conversations

Built using [OpenRouter](https://openrouter.ai/) and Streamlit.

🧪 *Beta v0.9.2* — Feedback welcome: [hello@thethirdvoice.ai](mailto:hello@thethirdvoice.ai)
""")
