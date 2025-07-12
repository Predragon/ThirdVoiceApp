import streamlit as st
from transformers import pipeline
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
        # Initialize local sentiment analyzer
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            device=-1  # Use CPU (set to 0 for GPU if available)
        )
        self.emotion_analyzer = None  # Placeholder for future emotion model
        self.model_status = {
            "sentiment": "working",
            "emotion": "unknown"
        }
        self.last_test_time = datetime.now()
        self.warmup_complete = True  # Local models load instantly

    def analyze_sentiment(self, text: str, show_debug: bool = False) -> Dict:
        """Analyze sentiment using local model"""
        if not text or len(text.strip()) < 2:
            return {"success": False, "error": "Text too short"}
        
        text = text.strip()[:512]
        try:
            start_time = time.time()
            result = self.sentiment_analyzer(text)[0]
            response_time = time.time() - start_time
            
            if show_debug:
                st.write(f"🔍 **Debug Info:** - Sentiment analysis completed in {response_time:.2f}s")
                st.write(f"Raw result: {result}")
            
            return {
                "success": True,
                "sentiment": result["label"].lower(),
                "confidence": result["score"],
                "response_time": response_time,
                "error": None
            }
        except Exception as e:
            if show_debug:
                st.error(f"💥 Sentiment analysis error: {str(e)}")
            return {"success": False, "error": str(e)}

    def analyze_emotion(self, text: str, show_debug: bool = False) -> Dict:
        """Placeholder for emotion analysis (rule-based fallback for now)"""
        if not text or len(text.strip()) < 2:
            return {"success": False, "error": "Text too short"}
        
        # Placeholder: Return dummy data or implement rule-based emotion detection
        return {
            "success": False,
            "error": "Emotion analysis not implemented locally. Using rule-based reframing.",
            "primary_emotion": {"label": "neutral", "score": 1.0},
            "emotions": [{"label": "neutral", "score": 1.0}]
        }

    def warm_up_models(self, show_progress: bool = True):
        """Warm up local models (instant for sentiment, placeholder for emotion)"""
        if show_progress:
            st.info("🔥 Warming up local AI models... This should be instant.")
        
        test_text = "I am feeling great today!"
        sentiment_result = self.analyze_sentiment(test_text, show_debug=False)
        emotion_result = self.analyze_emotion(test_text, show_debug=False)
        
        self.model_status["sentiment"] = "working" if sentiment_result["success"] else "error"
        self.model_status["emotion"] = "unknown"  # No local emotion model yet
        self.last_test_time = datetime.now()
        self.warmup_complete = self.model_status["sentiment"] == "working"
        
        if show_progress:
            if self.warmup_complete:
                st.success("🎉 Sentiment model is ready!")
            else:
                st.error("⚠️ Sentiment model failed to load.")
        
        return {
            "sentiment_working": sentiment_result["success"],
            "emotion_working": False,
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
        """Generate improved message with local sentiment analysis"""
        sentiment_analysis = self.analyze_sentiment(message, show_debug=show_debug)
        emotion_analysis = self.analyze_emotion(message, show_debug=show_debug)
        
        ai_working = sentiment_analysis.get("success")
        
        if sentiment_analysis.get("success") and sentiment_analysis.get("sentiment") in ["negative"]:
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
        return base_reframe  # Emotion data is placeholder, so use base reframe

    def _enhance_positive_message(self, message: str, context: str, sentiment_data: Dict, emotion_data: Dict) -> str:
        """Enhance positive messages"""
        if sentiment_data.get("success") and sentiment_data.get("sentiment") in ["positive"]:
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
    <p>🤖 <strong>Powered by Local AI Models</strong></p>
</div>
""", unsafe_allow_html=True)

# Model Status Display
status = ai_coach.get_model_status()
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if status["sentiment"] == "working":
        st.markdown('<div class="model-status status-working">✅ Sentiment AI: Ready</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="model-status status-error">❌ Sentiment AI: Error</div>', unsafe_allow_html=True)

with col2:
    if status["emotion"] == "working":
        st.markdown('<div class="model-status status-working">✅ Emotion AI: Ready</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="model-status status-loading">⏳ Emotion AI: Not Available</div>', unsafe_allow_html=True)

with col3:
    if st.button("🔥 Warm Up Models"):
        with st.spinner("Warming up local AI models..."):
            results = ai_coach.warm_up_models(show_progress=True)
            if results["sentiment_working"]:
                st.success("🎉 Sentiment model is ready!")
                st.session_state.models_warmed_up = True
                st.rerun()
            else:
                st.error("❌ Sentiment model failed to load. Check deployment resources.")

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
                if not ai_coach.warmup_complete:
                    st.warning("⚠️ AI models are not fully warmed up. Please click 'Warm Up Models' and try again.")
                else:
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
                                st.success("✅ Sentiment AI is working!")
                            else:
                                st.warning("⚠️ Sentiment AI failed. Using rule-based reframing.")
                            
                            # Original message
                            st.markdown("#### 📝 Original Message")
                            st.markdown(f'<div class="original-message">{result["original"]}</div>', unsafe_allow_html=True)
                            
                            # Sentiment analysis
                            st.markdown("#### 😊 Sentiment Analysis")
                            if result["sentiment_analysis"]["success"]:
                                sentiment = result["sentiment_analysis"]["sentiment"]
                                confidence = result["sentiment_analysis"]["confidence"]
                                st.markdown(f'<div class="ai-response">Sentiment: <strong>{sentiment}</strong> ({confidence:.1%})</div>', unsafe_allow_html=True)
                                if st.session_state.debug_mode:
                                    st.markdown('<div class="debug-info">')
                                    st.write(f"Response time: {result['sentiment_analysis']['response_time']:.2f}s")
                                    st.write(f"Raw result: {result['sentiment_analysis']}")
                                    st.markdown('</div>')
                            else:
                                st.markdown(f'<div class="warning-box">⚠️ Sentiment analysis failed: {result["sentiment_analysis"]["error"]}</div>', unsafe_allow_html=True)
                            
                            # Emotion analysis
                            st.markdown("#### 😢 Emotion Analysis")
                            if result["emotion_analysis"]["success"]:
                                primary = result["emotion_analysis"]["primary_emotion"]
                                st.markdown(f'<div class="ai-response"><span class="emotion-pill emotion-primary">{primary["label"]} ({primary["score"]:.1%})</span></div>', unsafe_allow_html=True)
                                if st.session_state.debug_mode:
                                    st.markdown('<div class="debug-info">')
                                    st.write(f"Response time: {result['emotion_analysis']['response_time']:.2f}s")
                                    st.write(f"All emotions: {result['emotion_analysis']['emotions']}")
                                    st.markdown('</div>')
                                secondary_emotions = [e for e in result["emotion_analysis"]["emotions"] if e["label"] != primary["label"]]
                                if secondary_emotions:
                                    st.markdown("Other detected emotions:")
                                    for emotion in secondary_emotions:
                                        st.markdown(f'<span class="emotion-pill emotion-secondary">{emotion["label"]} ({emotion["score"]:.1%})</span>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="warning-box">⚠️ Emotion analysis not available: {result["emotion_analysis"]["error"]}</div>', unsafe_allow_html=True)
                            
                            # Reframed message
                            st.markdown("#### ✨ Suggested Reframe")
                            st.markdown(f'<div class="reframe-box">{result["reframed"]}</div>', unsafe_allow_html=True)
                            st.code(result["reframed"], language=None)
            else:
                st.warning("Please enter a message to analyze.")

with tab2:
    st.markdown("### 🔍 Emotional Translator")
    st.markdown("Understand the emotions behind your message (rule-based for now).")
    st.warning("Emotion analysis is not yet implemented locally. Suggestions are rule-based.")
    # Placeholder content; add emotion model later if desired

with tab3:
    st.markdown("### 🧠 AI Models")
    st.markdown("Details about the AI models powering The Third Voice.")
    
    status = ai_coach.get_model_status()
    st.markdown("#### Model Status")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Sentiment Model**: `distilbert-base-uncased-finetuned-sst-2-english`")
        st.markdown(f"Status: **{status['sentiment'].capitalize()}**")
    with col2:
        st.markdown(f"**Emotion Model**: None (Rule-based)")
        st.markdown(f"Status: **{status['emotion'].capitalize()}**")
    
    if status["last_test"]:
        st.markdown(f"Last tested: {status['last_test'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    st.markdown("#### About the Models")
    st.markdown("""
    - **Sentiment Model**: Uses a local `distilbert` model for offline sentiment analysis (positive/negative).
    - **Emotion Model**: Currently unavailable locally; reframing relies on rule-based logic.
    - Models run on-device, avoiding API dependencies.
    """)

with tab4:
    st.markdown("### ℹ️ About The Third Voice")
    st.markdown("""
    **The Third Voice** is an AI-powered tool designed to help you communicate with emotional intelligence. It analyzes your message's tone and suggests reframed versions to foster constructive dialogue, now using local models for reliability.

    **Features**:
    - Local sentiment analysis
    - Rule-based reframing
    - Context-aware suggestions

    **Created by**: A team passionate about improving communication through AI.

    For more information, visit [Hugging Face](https://huggingface.co) for model details.
    """)

if __name__ == "__main__":
    # Auto-warm models on first load if not already warmed
    if not st.session_state.models_warmed_up:
        def run_warmup():
            ai_coach.warm_up_models(show_progress=False)
            st.session_state.models_warmed_up = True
        threading.Thread(target=run_warmup, daemon=True).start()
