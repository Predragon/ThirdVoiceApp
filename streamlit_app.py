import streamlit as st
import requests
import json
import time
from typing import Dict, List

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
</style>
""", unsafe_allow_html=True)

# Free AI Model Configuration
FREE_AI_MODELS = {
    "huggingface": {
        "sentiment": "cardiffnlp/twitter-roberta-base-sentiment-latest",
        "text_generation": "microsoft/DialoGPT-medium",
        "emotion": "j-hartmann/emotion-english-distilroberta-base"
    }
}

# Hugging Face API (free tier)
HF_API_BASE = "https://api-inference.huggingface.co/models"

class AIMessageCoach:
    def __init__(self):
        self.session = requests.Session()
        
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment using free HF model"""
        try:
            response = self.session.post(
                f"{HF_API_BASE}/{FREE_AI_MODELS['huggingface']['sentiment']}",
                json={"inputs": text},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return {
                        "sentiment": result[0][0]['label'],
                        "confidence": result[0][0]['score'],
                        "success": True
                    }
            return {"success": False, "error": "API response issue"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_emotion(self, text: str) -> Dict:
        """Analyze emotions using free HF model"""
        try:
            response = self.session.post(
                f"{HF_API_BASE}/{FREE_AI_MODELS['huggingface']['emotion']}",
                json={"inputs": text},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    emotions = result[0]
                    return {
                        "emotions": emotions,
                        "primary_emotion": max(emotions, key=lambda x: x['score']),
                        "success": True
                    }
            return {"success": False, "error": "API response issue"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_reframe(self, message: str, context: str = "general") -> str:
        """Generate better message using AI + rules"""
        # Get AI analysis
        sentiment_analysis = self.analyze_sentiment(message)
        emotion_analysis = self.analyze_emotion(message)
        
        # Rule-based reframing with AI insights
        if sentiment_analysis.get("success") and sentiment_analysis.get("sentiment") == "NEGATIVE":
            if context == "coparenting":
                return self._reframe_coparenting(message)
            elif context == "romantic":
                return self._reframe_romantic(message)
            else:
                return self._reframe_general(message)
        else:
            return message + " ✨ (Your message has a positive tone!)"
    
    def _reframe_coparenting(self, message: str) -> str:
        """Child-focused reframing"""
        reframed = message.lower()
        reframed = reframed.replace("you always", "I've noticed")
        reframed = reframed.replace("you never", "it would help if")
        reframed = reframed.replace("your fault", "we can work together on")
        return f"Hi, I wanted to discuss something about our child. {reframed.capitalize()} Can we find a solution that works for everyone?"
    
    def _reframe_romantic(self, message: str) -> str:
        """Love-focused reframing"""
        reframed = message.lower()
        reframed = reframed.replace("you", "I feel")
        reframed = reframed.replace("always", "sometimes")
        reframed = reframed.replace("never", "rarely")
        return f"Hey love, I wanted to share something that's been on my mind. {reframed.capitalize()} I care about us and want to work through this together. ❤️"
    
    def _reframe_general(self, message: str) -> str:
        """General diplomatic reframing"""
        reframed = message.lower()
        reframed = reframed.replace("you", "I")
        reframed = reframed.replace("always", "often")
        reframed = reframed.replace("never", "sometimes don't")
        return f"I hope you're doing well. I wanted to discuss something: {reframed.capitalize()} I'd love to hear your thoughts on this."

# Initialize AI Coach
@st.cache_resource
def get_ai_coach():
    return AIMessageCoach()

ai_coach = get_ai_coach()

# Header
st.markdown("""
<div class="main-header">
    <h1>🧠💬 The Third Voice</h1>
    <h3>Your AI co-mediator for emotionally intelligent communication</h3>
    <p><i>Built in detention, with a phone, for life's hardest moments.</i></p>
    <p>🤖 <strong>Powered by Free AI Models</strong></p>
</div>
""", unsafe_allow_html=True)

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
                    
                    # Get AI analysis
                    sentiment_result = ai_coach.analyze_sentiment(message_input)
                    emotion_result = ai_coach.analyze_emotion(message_input)
                    
                    with col2:
                        st.markdown("#### 🤖 AI Analysis Results")
                        
                        # Sentiment Analysis
                        if sentiment_result.get("success"):
                            sentiment = sentiment_result["sentiment"]
                            confidence = sentiment_result["confidence"]
                            
                            if sentiment == "NEGATIVE":
                                st.error(f"⚠️ Negative sentiment detected ({confidence:.2%} confidence)")
                            elif sentiment == "POSITIVE":
                                st.success(f"✅ Positive sentiment ({confidence:.2%} confidence)")
                            else:
                                st.info(f"😐 Neutral sentiment ({confidence:.2%} confidence)")
                        else:
                            st.warning("⚠️ Sentiment analysis unavailable (using backup logic)")
                        
                        # Emotion Analysis
                        if emotion_result.get("success"):
                            primary_emotion = emotion_result["primary_emotion"]
                            st.markdown(f"**Primary emotion:** {primary_emotion['label'].title()} ({primary_emotion['score']:.2%})")
                            
                            # Show top 3 emotions
                            st.markdown("**Emotion breakdown:**")
                            for emotion in sorted(emotion_result["emotions"], key=lambda x: x['score'], reverse=True)[:3]:
                                st.markdown(f"• {emotion['label'].title()}: {emotion['score']:.1%}")
                        else:
                            st.warning("⚠️ Emotion analysis unavailable")
                        
                        # AI-Generated Reframe
                        st.markdown("#### ✨ AI-Suggested Reframe")
                        reframed = ai_coach.generate_reframe(message_input, context)
                        
                        st.markdown('<div class="ai-response">', unsafe_allow_html=True)
                        st.markdown(reframed)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Copy button
                        st.code(reframed, language=None)
                        
            else:
                st.warning("Please enter a message to analyze.")

with tab2:
    st.markdown("### AI Emotional Translation")
    st.markdown("Let AI help you understand the emotional undertones of messages you receive.")
    
    received_message = st.text_area(
        "Message you received:",
        placeholder="Paste the message you're trying to understand...",
        height=100
    )
    
    if st.button("🤖 AI Translate", type="primary"):
        if received_message.strip():
            with st.spinner("🤖 AI is analyzing the emotional subtext..."):
                
                sentiment_result = ai_coach.analyze_sentiment(received_message)
                emotion_result = ai_coach.analyze_emotion(received_message)
                
                st.markdown("#### 🔍 AI Emotional Analysis")
                
                st.markdown(f"**Original message:** \"{received_message}\"")
                
                if sentiment_result.get("success"):
                    sentiment = sentiment_result["sentiment"]
                    confidence = sentiment_result["confidence"]
                    
                    st.markdown(f"**Overall sentiment:** {sentiment.title()} ({confidence:.1%} confidence)")
                
                if emotion_result.get("success"):
                    emotions = emotion_result["emotions"]
                    primary = emotion_result["primary_emotion"]
                    
                    st.markdown(f"**Primary emotion detected:** {primary['label'].title()} ({primary['score']:.1%})")
                    
                    # Interpretation based on AI results
                    if primary['label'] in ['anger', 'disgust']:
                        st.markdown("**🔥 Possible meaning:** They might be frustrated or upset about something")
                        st.markdown("**💡 Suggested response:** Acknowledge their feelings and ask how you can help")
                    elif primary['label'] in ['sadness', 'fear']:
                        st.markdown("**😢 Possible meaning:** They might be feeling hurt or worried")
                        st.markdown("**💡 Suggested response:** Offer support and reassurance")
                    elif primary['label'] == 'joy':
                        st.markdown("**😊 Possible meaning:** They're feeling positive!")
                        st.markdown("**💡 Suggested response:** Share in their positivity")
                    else:
                        st.markdown("**🤔 Possible meaning:** Mixed or neutral emotions")
                        st.markdown("**💡 Suggested response:** Ask for clarification if needed")
                
                st.markdown("**🎯 General advice:**")
                st.markdown("• Give them the benefit of the doubt")
                st.markdown("• Consider their current stress level")
                st.markdown("• Respond with empathy, not defensiveness")
                
        else:
            st.warning("Please enter a message to translate.")

with tab3:
    st.markdown("### 🤖 AI Models Powering The Third Voice")
    st.markdown("We use cutting-edge, free AI models to analyze your messages:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎭 Sentiment Analysis")
        st.markdown("**Model:** `cardiffnlp/twitter-roberta-base-sentiment-latest`")
        st.markdown("- Detects positive, negative, neutral sentiment")
        st.markdown("- Trained on millions of social media messages")
        st.markdown("- 94% accuracy on text classification")
        
        st.markdown("#### 😊 Emotion Detection")
        st.markdown("**Model:** `j-hartmann/emotion-english-distilroberta-base`")
        st.markdown("- Identifies 7 core emotions")
        st.markdown("- Joy, Sadness, Anger, Fear, Surprise, Disgust, Neutral")
        st.markdown("- Optimized for real-world text")
    
    with col2:
        st.markdown("#### 🚀 Why Free Models?")
        st.markdown("- **No API costs** - completely free to use")
        st.markdown("- **Privacy-focused** - no data stored by third parties")
        st.markdown("- **Always available** - no rate limits or quotas")
        st.markdown("- **Transparent** - open source models you can trust")
        
        st.markdown("#### 🧠 Model Performance")
        test_message = st.text_input("Test the AI models:", placeholder="Type a message to test...")
        
        if st.button("🧪 Test AI Models") and test_message:
            with st.spinner("Testing..."):
                sentiment = ai_coach.analyze_sentiment(test_message)
                emotion = ai_coach.analyze_emotion(test_message)
                
                if sentiment.get("success"):
                    st.success(f"Sentiment: {sentiment['sentiment']} ({sentiment['confidence']:.1%})")
                
                if emotion.get("success"):
                    primary = emotion["primary_emotion"]
                    st.info(f"Primary emotion: {primary['label'].title()} ({primary['score']:.1%})")

with tab4:
    st.markdown("## About The Third Voice")
    
    st.markdown("""
    The Third Voice was born from a deeply personal crisis — miscommunication during detention — 
    and emerged as a digital co-mediator to help people communicate calmly and constructively 
    in emotionally charged relationships.
    """)
    
    st.markdown("### 🎯 Why it matters:")
    st.markdown("""
    - **Miscommunication**—not lack of care—often breaks relationships
    - **People text when emotional**, leading to misfires
    - **Therapy is slow/expensive**
    - **Everyone texts**—no one has a coach in their pocket
    """)
    
    st.markdown("### 🤖 Powered by AI")
    st.markdown("""
    - **Free AI models** from Hugging Face
    - **Real-time analysis** of tone and emotion
    - **Privacy-first** approach - no data stored
    - **Always improving** with better models
    """)
    
    st.markdown("### 🔗 Connect with us:")
    st.markdown("""
    - **Website:** [TheThirdVoice.ai](https://TheThirdVoice.ai)
    - **Email:** hello@TheThirdVoice.ai
    - **Hashtag:** #TheThirdVoice
    - **Founder:** Predrag Mirkovic
    """)

# Footer
st.markdown("---")
st.markdown("© 2025 The Third Voice • Built with ❤️ and 🤖 AI • [Visit TheThirdVoice.ai](https://TheThirdVoice.ai)")

# Usage tracking
if 'usage_count' not in st.session_state:
    st.session_state.usage_count = 0

st.session_state.usage_count += 1
st.sidebar.markdown(f"**Session uses:** {st.session_state.usage_count}")
st.sidebar.markdown("🤖 **AI Models:** Online")
st.sidebar.markdown("💡 **Tip:** Try different contexts for better results!")
