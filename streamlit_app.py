import streamlit as st
import requests
import json
import time
from typing import Dict, List

class AIMessageCoach:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TheThirdVoice/1.0',
            'Accept': 'application/json'
        })
        
    def _make_hf_request(self, model_name: str, text: str, max_retries: int = 3) -> Dict:
        """Make request to Hugging Face with retry logic"""
        url = f"https://api-inference.huggingface.co/models/{model_name}"
        
        for attempt in range(max_retries):
            try:
                response = self.session.post(
                    url,
                    json={"inputs": text},
                    timeout=30  # Increased timeout
                )
                
                # Debug info
                st.write(f"🔍 Debug - Attempt {attempt + 1}: Status {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    st.write(f"✅ Success! Response: {result}")
                    return {"success": True, "data": result}
                
                elif response.status_code == 503:
                    # Model is loading
                    wait_time = 20 + (attempt * 10)
                    st.warning(f"🔄 Model loading... waiting {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                
                elif response.status_code == 429:
                    # Rate limited
                    st.warning(f"⏱️ Rate limited, waiting... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(10)
                    continue
                
                else:
                    st.error(f"❌ HTTP {response.status_code}: {response.text}")
                    
            except requests.exceptions.Timeout:
                st.warning(f"⏰ Request timeout (attempt {attempt + 1}/{max_retries})")
                time.sleep(5)
                continue
                
            except requests.exceptions.RequestException as e:
                st.error(f"🌐 Network error: {str(e)}")
                time.sleep(5)
                continue
                
            except Exception as e:
                st.error(f"💥 Unexpected error: {str(e)}")
                break
        
        return {"success": False, "error": "Max retries exceeded"}
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment with improved error handling"""
        if not text or len(text.strip()) < 3:
            return {"success": False, "error": "Text too short"}
        
        model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        result = self._make_hf_request(model_name, text)
        
        if result["success"]:
            data = result["data"]
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
                sentiment_data = data[0]
                # Find the highest confidence prediction
                best_prediction = max(sentiment_data, key=lambda x: x.get('score', 0))
                return {
                    "sentiment": best_prediction['label'],
                    "confidence": best_prediction['score'],
                    "success": True,
                    "all_predictions": sentiment_data
                }
        
        return {"success": False, "error": result.get("error", "Unknown error")}
    
    def analyze_emotion(self, text: str) -> Dict:
        """Analyze emotions with improved error handling"""
        if not text or len(text.strip()) < 3:
            return {"success": False, "error": "Text too short"}
        
        model_name = "j-hartmann/emotion-english-distilroberta-base"
        result = self._make_hf_request(model_name, text)
        
        if result["success"]:
            data = result["data"]
            if isinstance(data, list) and len(data) > 0:
                emotions = data[0]
                primary_emotion = max(emotions, key=lambda x: x.get('score', 0))
                return {
                    "emotions": emotions,
                    "primary_emotion": primary_emotion,
                    "success": True
                }
        
        return {"success": False, "error": result.get("error", "Unknown error")}
    
    def test_models(self) -> Dict:
        """Test if models are working"""
        test_text = "I am feeling great today!"
        
        st.write("🧪 Testing AI models...")
        
        # Test sentiment
        sentiment_result = self.analyze_sentiment(test_text)
        emotion_result = self.analyze_emotion(test_text)
        
        return {
            "sentiment_working": sentiment_result["success"],
            "emotion_working": emotion_result["success"],
            "sentiment_result": sentiment_result,
            "emotion_result": emotion_result
        }
    
    def generate_reframe(self, message: str, context: str = "general") -> str:
        """Generate better message using AI + rules"""
        # Get AI analysis
        sentiment_analysis = self.analyze_sentiment(message)
        emotion_analysis = self.analyze_emotion(message)
        
        # Enhanced rule-based reframing
        if sentiment_analysis.get("success"):
            if sentiment_analysis.get("sentiment") in ["NEGATIVE", "LABEL_0"]:
                return self._smart_reframe(message, context, sentiment_analysis, emotion_analysis)
            else:
                return message + " ✨ (Your message has a positive tone!)"
        else:
            # Fallback to rule-based only
            return self._fallback_reframe(message, context)
    
    def _smart_reframe(self, message: str, context: str, sentiment_data: Dict, emotion_data: Dict) -> str:
        """AI-enhanced reframing"""
        base_reframe = self._fallback_reframe(message, context)
        
        # Add AI insights
        if emotion_data.get("success"):
            primary_emotion = emotion_data["primary_emotion"]["label"]
            if primary_emotion in ["anger", "disgust"]:
                return f"I want to share something important with you. {base_reframe} I value our relationship and hope we can work through this together."
            elif primary_emotion in ["sadness", "fear"]:
                return f"I've been thinking about something and wanted to discuss it with you. {base_reframe} Your perspective would mean a lot to me."
        
        return base_reframe
    
    def _fallback_reframe(self, message: str, context: str) -> str:
        """Fallback rule-based reframing when AI is unavailable"""
        reframed = message.lower()
        
        # Common negative patterns
        reframed = reframed.replace("you always", "I've noticed that sometimes")
        reframed = reframed.replace("you never", "it would help if")
        reframed = reframed.replace("you're", "I feel")
        reframed = reframed.replace("your fault", "we can work together on")
        reframed = reframed.replace("you don't", "I'd appreciate if")
        
        if context == "coparenting":
            return f"Hi, I wanted to discuss something about our child. {reframed.capitalize()} Can we find a solution that works for our family?"
        elif context == "romantic":
            return f"Hey love, I wanted to share something that's been on my mind. {reframed.capitalize()} I care about us and want to work through this together. ❤️"
        elif context == "workplace":
            return f"Hi, I wanted to discuss something with you. {reframed.capitalize()} I'd appreciate your thoughts on how we can move forward."
        else:
            return f"I hope you're doing well. I wanted to discuss something: {reframed.capitalize()} I'd love to hear your perspective on this."

# Updated Streamlit interface
def main():
    st.title("🧠💬 The Third Voice - Debug Mode")
    
    # Initialize AI Coach
    if 'ai_coach' not in st.session_state:
        st.session_state.ai_coach = AIMessageCoach()
    
    ai_coach = st.session_state.ai_coach
    
    # Debug section
    st.markdown("## 🔧 Debug & Test")
    
    if st.button("🧪 Test AI Models"):
        test_results = ai_coach.test_models()
        
        st.write("### Test Results:")
        st.write(f"✅ Sentiment Model: {'Working' if test_results['sentiment_working'] else '❌ Not Working'}")
        st.write(f"✅ Emotion Model: {'Working' if test_results['emotion_working'] else '❌ Not Working'}")
        
        if test_results['sentiment_working']:
            st.success("🎉 AI models are working!")
        else:
            st.error("⚠️ AI models need time to load. Try again in 30 seconds.")
    
    st.markdown("---")
    
    # Regular interface
    st.markdown("## ✍️ Message Analysis")
    
    message_input = st.text_area(
        "Your message:",
        placeholder="Type your message here...",
        height=100
    )
    
    context = st.selectbox(
        "Context:",
        ["general", "romantic", "coparenting", "workplace"]
    )
    
    if st.button("🤖 Analyze Message"):
        if message_input.strip():
            with st.spinner("🤖 Analyzing your message..."):
                
                # Show debug info
                st.markdown("### 🔍 Debug Info")
                
                sentiment_result = ai_coach.analyze_sentiment(message_input)
                emotion_result = ai_coach.analyze_emotion(message_input)
                
                st.markdown("### 📊 Analysis Results")
                
                if sentiment_result.get("success"):
                    st.success(f"✅ Sentiment: {sentiment_result['sentiment']} ({sentiment_result['confidence']:.1%})")
                else:
                    st.warning(f"⚠️ Sentiment analysis failed: {sentiment_result.get('error', 'Unknown error')}")
                
                if emotion_result.get("success"):
                    primary = emotion_result["primary_emotion"]
                    st.success(f"✅ Primary emotion: {primary['label']} ({primary['score']:.1%})")
                else:
                    st.warning(f"⚠️ Emotion analysis failed: {emotion_result.get('error', 'Unknown error')}")
                
                # Generate reframe
                st.markdown("### ✨ Suggested Reframe")
                reframed = ai_coach.generate_reframe(message_input, context)
                st.info(reframed)
                
                # Copy box
                st.code(reframed, language=None)
        else:
            st.warning("Please enter a message to analyze.")

if __name__ == "__main__":
    main()
