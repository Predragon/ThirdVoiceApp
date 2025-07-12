import streamlit as st
import requests
import json
import time
from typing import Dict, List
import threading
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="The Third Voice",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: #f9f9f9;
    }
    
    .ai-response {
        background: #f0f8ff;
        border-left: 4px solid #4CAF50;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    
    .warning-box {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    
    .debug-info {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        padding: 0.5rem;
        border-radius: 5px;
        font-family: monospace;
        font-size: 0.8rem;
    }
    
    .model-status {
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    
    .status-working { background: #d4edda; color: #155724; }
    .status-loading { background: #fff3cd; color: #856404; }
    .status-error { background: #f8d7da; color: #721c24; }
    
    .reframe-box {
        background: #e8f5e8;
        border: 2px solid #4CAF50;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .original-message {
        background: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    
    .emotion-pill {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        margin: 0.25rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .emotion-primary { background: #4CAF50; color: white; }
    .emotion-secondary { background: #e0e0e0; color: #333; }
</style>
""", unsafe_allow_html=True)

class AIMessageCoach:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TheThirdVoice/1.0',
            'Accept': 'application/json'
        })
        self.models = {
            "sentiment": "cardiffnlp/twitter-roberta-base-sentiment-latest",
            "emotion": "j-hartmann/emotion-english-distilroberta-base"
        }
        self.model_status = {
            "sentiment": "unknown",
            "emotion": "unknown"
        }
        self.last_test_time = None
        
    def _make_hf_request(self, model_name: str, text: str, max_retries: int = 3, show_debug: bool = False) -> Dict:
        """Make request to Hugging Face with comprehensive error handling"""
        url = f"https://api-inference.huggingface.co/models/{model_name}"
        
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                response = self.session.post(
                    url,
                    json={"inputs": text},
                    timeout=45
                )
                response_time = time.time() - start_time
                
                if show_debug:
                    st.write(f"🔍 **Debug Info:**")
                    st.write(f"- Model: `{model_name.split('/')[-1]}`")
                    st.write(f"- Attempt: {attempt + 1}/{max_retries}")
                    st.write(f"- Status: {response.status_code}")
                    st.write(f"- Response time: {response_time:.2f}s")
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        if show_debug:
                            st.success(f"✅ Success! Model responded in {response_time:.2f}s")
                        return {"success": True, "data": result, "response_time": response_time}
                    except json.JSONDecodeError:
                        if show_debug:
                            st.error("❌ Invalid JSON response")
                        continue
                
                elif response.status_code == 503:
                    try:
                        error_data = response.json()
                        estimated_time = error_data.get('estimated_time', 20)
                    except:
                        estimated_time = 20 + (attempt * 10)
                    
                    if show_debug:
                        st.warning(f"⏳ Model loading... estimated {estimated_time}s")
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i in range(int(estimated_time)):
                        progress_bar.progress((i + 1) / estimated_time)
                        status_text.text(f"Loading model... {i+1}/{int(estimated_time)}s")
                        time.sleep(1)
                    
                    progress_bar.empty()
                    status_text.empty()
                    continue
                
                elif response.status_code == 429:
                    wait_time = 60 + (attempt * 30)
                    if show_debug:
                        st.warning(f"⏱️ Rate limited. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                
                elif response.status_code == 400:
                    if show_debug:
                        st.error(f"❌ Bad request: {response.text}")
                    return {"success": False, "error": "Invalid input text"}
                
                else:
                    if show_debug:
                        st.error(f"❌ HTTP {response.status_code}: {response.text}")
                    time.sleep(5)
                    continue
                    
            except requests.exceptions.Timeout:
                if show_debug:
                    st.warning(f"⏰ Request timeout (attempt {attempt + 1}/{max_retries})")
                time.sleep(5)
                continue
                
            except requests.exceptions.ConnectionError:
                if show_debug:
                    st.error(f"🌐 Connection error (attempt {attempt + 1}/{max_retries})")
                time.sleep(10)
                continue
                
            except Exception as e:
                if show_debug:
                    st.error(f"💥 Unexpected error: {str(e)}")
                break
        
        return {"success": False, "error": "Max retries exceeded"}
    
    def analyze_sentiment(self, text: str, show_debug: bool = False) -> Dict:
        """Analyze sentiment with comprehensive error handling"""
        if not text or len(text.strip()) < 2:
            return {"success": False, "error": "Text too short"}
        
        text = text.strip()[:512]
        
        result = self._make_hf_request(self.models["sentiment"], text, show_debug=show_debug)
        
        if result["success"]:
            data = result["data"]
            try:
                if isinstance(data, list) and len(data) > 0:
                    sentiment_data = data[0]
                    if isinstance(sentiment_data, list):
                        best_prediction = max(sentiment_data, key=lambda x: x.get('score', 0))
                        self.model_status["sentiment"] = "working"
                        return {
                            "sentiment": best_prediction['label'],
                            "confidence": best_prediction['score'],
                            "success": True,
                            "all_predictions": sentiment_data,
                            "response_time": result.get("response_time", 0)
                        }
            except Exception as e:
                if show_debug:
                    st.error(f"Error parsing sentiment data: {str(e)}")
        
        self.model_status["sentiment"] = "error"
        return {"success": False, "error": result.get("error", "Unknown error")}
    
    def analyze_emotion(self, text: str, show_debug: bool = False) -> Dict:
        """Analyze emotions with comprehensive error handling"""
        if not text or len(text.strip()) < 2:
            return {"success": False, "error": "Text too short"}
        
        text = text.strip()[:512]
        
        result = self._make_hf_request(self.models["emotion"], text, show_debug=show_debug)
        
        if result["success"]:
            data = result["data"]
            try:
                if isinstance(data, list) and len(data) > 0:
                    emotions = data[0]
                    if isinstance(emotions, list):
                        primary_emotion = max(emotions, key=lambda x: x.get('score', 0))
                        self.model_status["emotion"] = "working"
                        return {
                            "emotions": emotions,
                            "primary_emotion": primary_emotion,
                            "success": True,
                            "response_time": result.get("response_time", 0)
                        }
            except Exception as e:
                if show_debug:
                    st.error(f"Error parsing emotion data: {str(e)}")
        
        self.model_status["emotion"] = "error"
        return {"success": False, "error": result.get("error", "Unknown error")}
    
    def warm_up_models(self, show_progress: bool = True):
        """Warm up AI models on app start"""
        if show_progress:
            st.info("🔥 Warming up AI models... This may take 30-60 seconds on first use.")
            
        test_text = "I am feeling great today!"
        
        if show_progress:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Testing sentiment model...")
            sentiment_result = self.analyze_sentiment(test_text, show_debug=False)
            progress_bar.progress(0.5)
            
            status_text.text("Testing emotion model...")
            emotion_result = self.analyze_emotion(test_text, show_debug=False)
            progress_bar.progress(1.0)
            
            progress_bar.empty()
            status_text.empty()
        else:
            sentiment_result = self.analyze_sentiment(test_text, show_debug=False)
            emotion_result = self.analyze_emotion(test_text, show_debug=False)
        
        self.last_test_time = datetime.now()
        
        return {
            "sentiment_working": sentiment_result["success"],
            "emotion_working": emotion_result["success"],
            "sentiment_result": sentiment_result,
            "emotion_result": emotion_result
        }
    
    def get_model_status(self) -> Dict:
        """Get current status of AI models"""
        return {
            "sentiment": self.model_status["sentiment"],
            "emotion": self.model_status["emotion"],
            "last_test": self.last_test_time
        }
    
    def generate_reframe(self, message: str, context: str = "general", show_debug: bool = False) -> Dict:
        """Generate improved message with AI analysis"""
        sentiment_analysis = self.analyze_sentiment(message, show_debug=show_debug)
        emotion_analysis = self.analyze_emotion(message, show_debug=show_debug)
        
        ai_working = sentiment_analysis.get("success") or emotion_analysis.get("success")
        
        if sentiment_analysis.get("success") and sentiment_analysis.get("sentiment") in ["NEGATIVE", "LABEL_0"]:
            reframed = self._smart_reframe(message, context, sentiment_analysis, emotion_analysis)
        else:
            reframed = self._enhance_positive_message(message, context, sentiment_analysis, emotion_analysis)
        
        return {
            "original": message,
            "reframed": reframed,
            "sentiment_analysis": sentiment_analysis,
            "emotion_analysis": emotion_analysis,
            "ai_working": ai_working,
            "context": context
        }
    
    def _smart_reframe(self, message: str, context: str, sentiment_data: Dict, emotion_data: Dict) -> str:
        """AI-enhanced reframing for negative messages"""
        base_reframe = self._rule_based_reframe(message, context)
        
        if emotion_data.get("success"):
            primary_emotion = emotion_data["primary_emotion"]["label"]
            
            if primary_emotion in ["anger", "disgust"]:
                return f"I want to share something important with you. {base_reframe} I value our relationship and hope we can work through this together."
            elif primary_emotion in ["sadness", "fear"]:
                return f"I've been thinking about something and wanted to discuss it with you. {base_reframe} Your perspective would mean a lot to me."
            elif primary_emotion == "surprise":
                return f"Something unexpected came up that I'd like to discuss. {base_reframe} I'd appreciate your thoughts on this."
        
        return base_reframe
    
    def _enhance_positive_message(self, message: str, context: str, sentiment_data: Dict, emotion_data: Dict) -> str:
        """Enhance positive messages"""
        if sentiment_data.get("success") and sentiment_data.get("sentiment") in ["POSITIVE", "LABEL_1"]:
            return f"{message} ✨ (Your message has a positive tone!)"
        else:
            return self._rule_based_reframe(message, context)
    
    def _rule_based_reframe(self, message: str, context: str) -> str:
        """Enhanced rule-based reframing"""
        reframed = message.lower()
        
        replacements = {
            "you always": "I've noticed that sometimes",
            "you never": "it would help if",
            "you're so": "I feel",
            "you don't": "I'd appreciate if",
            "your fault": "we can work together on",
            "you make me": "I feel",
            "you should": "it might be helpful if",
            "why don't you": "would you consider",
            "you can't": "it's challenging to",
            "you won't": "I hope we can find a way to"
        }
        
        for old, new in replacements.items():
            reframed = reframed.replace(old, new)
        
        if context == "coparenting":
            return f"Hi, I wanted to discuss something about our child. {reframed.capitalize()} Can we find a solution that works for our family?"
        elif context == "romantic":
            return f"Hey love, I wanted to share something that's been on my mind. {reframed.capitalize()} I care about us and want to work through this together. ❤️"
        elif context == "workplace":
            return f"Hi, I wanted to discuss something with you. {reframed.capitalize()} I'd appreciate your thoughts on how we can move forward professionally."
        else:
            return f"I hope you're doing well. I wanted to discuss something: {reframed.capitalize()} I'd love to hear your perspective on this."

# Initialize AI Coach with caching
@st.cache_resource
def get_ai_coach():
    return AIMessageCoach()

# Initialize session state
if 'models_warmed_up' not in st.session_state:
    st.session_state.models_warmed_up = False
if 'debug_mode' not in st.session_state:
    st.session_state.debug_mode = False

ai_coach = get_ai_coach()

# Header
st.markdown("""
<div class="main-header">
    <h1>🧠💬 The Third Voice</h1>
    <h3>Your AI co-mediator for emotionally intelligent communication</h3>
    <p><i>Built in detention, with a phone, for life's hardest moments.</i></p>
    <p>🤖 <strong>Powered by Advanced AI Models</strong></p>
</div>
""", unsafe_allow_html=True)

# Model Status Display
status = ai_coach.get_model_status()
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if status["sentiment"] == "working":
        st.markdown('<div class="model-status status-working">✅ Sentiment AI: Ready</div>', unsafe_allow_html=True)
    elif status["sentiment"] == "error":
        st.markdown('<div class="model-status status-error">❌ Sentiment AI: Error</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="model-status status-loading">⏳ Sentiment AI: Unknown</div>', unsafe_allow_html=True)

with col2:
    if status["emotion"] == "working":
        st.markdown('<div class="model-status status-working">✅ Emotion AI: Ready</div>', unsafe_allow_html=True)
    elif status["emotion"] == "error":
        st.markdown('<div class="model-status status-error">❌ Emotion AI: Error</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="model-status status-loading">⏳ Emotion AI: Unknown</div>', unsafe_allow_html=True)

with col3:
    if st.button("🔥 Warm Up Models"):
        with st.spinner("Warming up AI models..."):
            results = ai_coach.warm_up_models(show_progress=True)
            if results["sentiment_working"] and results["emotion_working"]:
                st.success("🎉 All AI models are ready!")
                st.session_state.models_warmed_up = True
                st.rerun()
            elif results["sentiment_working"] or results["emotion_working"]:
                st.warning("⚠️ Some AI models are ready. App will work with fallback logic.")
            else:
                st.error("❌ AI models are having issues. App will use rule-based fallbacks.")

# Debug mode toggle
st.session_state.debug_mode = st.checkbox("🔧 Debug Mode", value=st.session_state.debug_mode)

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["✍️ AI Message Coach", "🔍 Emotional Translator", "🧠 AI Models", "ℹ️ About"])

with tab1:
    st.markdown("### AI-Powered Message Coaching")
    st.markdown("Real AI analysis of your message tone, emotions, and suggestions for improvement.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        message_input = st.text_area(
            "Your message draft:",
            placeholder="Type the message you want to send...",
            height=150,
            key="message_input"
        )
        
        context = st.selectbox(
            "Context:",
            ["general", "romantic", "coparenting", "workplace"],
            index=0
        )
        
        if st.button("🤖 AI Analysis & Reframe", type="primary"):
            if message_input.strip():
                with st.spinner("🤖 AI is analyzing your message..."):
                    result = ai_coach.generate_reframe(
                        message_input, 
                        context, 
                        show_debug=st.session_state.debug_mode
                    )
                    
                    with col2:
                        st.markdown("#### 🤖 AI Analysis Results")
                        
                        # Show AI status
                        if result["ai_working"]:
                            st.success("✅ AI models are working!")
                        else:
                            st.warning("⚠️ Using rule-based fallback due to AI model issues.")
                        
                        # Original message
                        st.markdown("#### 📝 Original Message")
                        st.markdown(f'<div class="original-message">{result["original"]}</div>', unsafe_allow_html=True)
                        
                        # Sentiment analysis
                        st.markdown("#### 😊 Sentiment Analysis")
                        if result["sentiment_analysis"]["success"]:
                            sentiment = result["sentiment_analysis"]["sentiment"]
                            confidence = result["sentiment_analysis"]["confidence"]
                            respon
