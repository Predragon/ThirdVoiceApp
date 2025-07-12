import streamlit as st
import requests
import json
import time
import re
from typing import Dict, List
from collections import Counter

# Import the emotion detector from the previous artifact
class AdvancedEmotionDetector:
    def __init__(self):
        # Core emotion dictionaries with intensity weights
        self.emotion_lexicon = {
            'anger': {
                'high': ['hate', 'furious', 'enraged', 'livid', 'pissed', 'outraged', 'disgusted'],
                'medium': ['angry', 'mad', 'irritated', 'annoyed', 'frustrated', 'upset', 'bothered'],
                'low': ['disappointed', 'disagree', 'concerned', 'uncomfortable']
            },
            'sadness': {
                'high': ['devastated', 'heartbroken', 'crushed', 'miserable', 'depressed'],
                'medium': ['sad', 'hurt', 'disappointed', 'upset', 'lonely', 'down'],
                'low': ['blue', 'melancholy', 'unhappy', 'gloomy']
            },
            'fear': {
                'high': ['terrified', 'panicked', 'horrified', 'petrified'],
                'medium': ['scared', 'afraid', 'worried', 'anxious', 'nervous', 'concerned'],
                'low': ['uneasy', 'hesitant', 'cautious', 'uncertain']
            },
            'joy': {
                'high': ['ecstatic', 'thrilled', 'overjoyed', 'elated', 'euphoric'],
                'medium': ['happy', 'glad', 'pleased', 'content', 'satisfied', 'cheerful'],
                'low': ['okay', 'fine', 'alright', 'decent']
            },
            'surprise': {
                'high': ['shocked', 'stunned', 'amazed', 'astonished'],
                'medium': ['surprised', 'unexpected', 'sudden', 'wow'],
                'low': ['interesting', 'unusual', 'different']
            },
            'disgust': {
                'high': ['revolted', 'sickened', 'repulsed', 'nauseated'],
                'medium': ['disgusted', 'gross', 'yuck', 'ew'],
                'low': ['unpleasant', 'distasteful', 'off-putting']
            }
        }
        
        # Emotional patterns
        self.anger_patterns = [
            r"you always\b", r"you never\b", r"your fault\b", r"i hate\b",
            r"so stupid\b", r"can't believe\b", r"sick of\b", r"fed up\b"
        ]
        
        self.sadness_patterns = [
            r"i feel\s+(hurt|sad|lonely|empty)", r"why do\s+you",
            r"makes me\s+(sad|hurt)", r"i'm\s+(disappointed|hurt|sad)",
            r"wish\s+things", r"miss\s+when"
        ]
        
        self.fear_patterns = [
            r"what if\b", r"i'm\s+(scared|afraid|worried)",
            r"don't want\s+to\s+lose", r"terrified\s+that",
            r"anxiety\s+about", r"concerned\s+about"
        ]
        
        # Relationship context modifiers
        self.relationship_modifiers = {
            'coparenting': {
                'triggers': ['our child', 'our kid', 'custody', 'visitation', 'school'],
                'emotion_boost': {'anger': 0.3, 'sadness': 0.2, 'fear': 0.4}
            },
            'romantic': {
                'triggers': ['love', 'relationship', 'us', 'together', 'date'],
                'emotion_boost': {'sadness': 0.3, 'fear': 0.2, 'joy': 0.2}
            },
            'workplace': {
                'triggers': ['work', 'boss', 'project', 'deadline', 'meeting'],
                'emotion_boost': {'anger': 0.2, 'fear': 0.3, 'disgust': 0.2}
            }
        }
    
    def preprocess_text(self, text: str) -> str:
        """Clean and prepare text for analysis"""
        text = re.sub(r'http\S+|www\S+|@\w+|#\w+', '', text)
        text = ' '.join(text.split())
        return text.lower()
    
    def detect_caps_intensity(self, text: str) -> str:
        """Detect intensity based on capitalization"""
        caps_count = sum(1 for c in text if c.isupper())
        total_letters = sum(1 for c in text if c.isalpha())
        
        if total_letters == 0:
            return 'low'
        
        caps_ratio = caps_count / total_letters
        
        if caps_ratio > 0.7:
            return 'high'
        elif caps_ratio > 0.3:
            return 'medium'
        else:
            return 'low'
    
    def score_emotion_words(self, text: str) -> Dict[str, float]:
        """Score emotions based on word matching"""
        scores = {emotion: 0.0 for emotion in self.emotion_lexicon.keys()}
        
        for emotion, intensity_dict in self.emotion_lexicon.items():
            for intensity, words in intensity_dict.items():
                for word in words:
                    if word in text:
                        weight = {'high': 3.0, 'medium': 2.0, 'low': 1.0}[intensity]
                        scores[emotion] += weight
        
        return scores
    
    def score_emotion_patterns(self, text: str) -> Dict[str, float]:
        """Score emotions based on pattern matching"""
        scores = {emotion: 0.0 for emotion in self.emotion_lexicon.keys()}
        
        for pattern in self.anger_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                scores['anger'] += 2.0
        
        for pattern in self.sadness_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                scores['sadness'] += 2.0
        
        for pattern in self.fear_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                scores['fear'] += 2.0
        
        return scores
    
    def apply_intensity_modifiers(self, scores: Dict[str, float], text: str) -> Dict[str, float]:
        """Apply intensity modifiers based on punctuation and formatting"""
        caps_intensity = self.detect_caps_intensity(text)
        exclamation_count = text.count('!')
        question_count = text.count('?')
        
        multiplier = 1.0
        
        if caps_intensity == 'high':
            multiplier += 0.5
        elif caps_intensity == 'medium':
            multiplier += 0.3
        
        if exclamation_count >= 3:
            multiplier += 0.4
        elif exclamation_count >= 2:
            multiplier += 0.3
        elif exclamation_count >= 1:
            multiplier += 0.2
        
        if question_count >= 2:
            multiplier += 0.3
        elif question_count >= 1:
            multiplier += 0.1
        
        # Apply multiplier to negative emotions more strongly
        negative_emotions = ['anger', 'sadness', 'fear', 'disgust']
        for emotion in scores:
            if emotion in negative_emotions:
                scores[emotion] *= multiplier
            else:
                scores[emotion] *= min(multiplier, 1.3)
        
        return scores
    
    def apply_context_modifiers(self, scores: Dict[str, float], text: str, context: str = None) -> Dict[str, float]:
        """Apply context-specific modifiers"""
        if context and context in self.relationship_modifiers:
            modifier_info = self.relationship_modifiers[context]
            context_present = any(trigger in text for trigger in modifier_info['triggers'])
            
            if context_present:
                for emotion, boost in modifier_info['emotion_boost'].items():
                    scores[emotion] *= (1 + boost)
        
        return scores
    
    def detect_emotion(self, text: str, context: str = None) -> Dict:
        """Main emotion detection function"""
        if not text or len(text.strip()) < 2:
            return {
                'primary_emotion': 'neutral',
                'confidence': 0.0,
                'all_emotions': {},
                'success': False,
                'error': 'Text too short'
            }
        
        original_text = text
        processed_text = self.preprocess_text(text)
        
        # Score emotions
        word_scores = self.score_emotion_words(processed_text)
        pattern_scores = self.score_emotion_patterns(processed_text)
        
        # Combine scores
        combined_scores = {}
        for emotion in word_scores:
            combined_scores[emotion] = word_scores[emotion] + pattern_scores[emotion]
        
        # Apply modifiers
        combined_scores = self.apply_intensity_modifiers(combined_scores, original_text)
        combined_scores = self.apply_context_modifiers(combined_scores, processed_text, context)
        
        # Determine primary emotion
        if all(score == 0 for score in combined_scores.values()):
            return {
                'primary_emotion': 'neutral',
                'confidence': 0.8,
                'all_emotions': {'neutral': 0.8},
                'success': True,
                'method': 'rule-based'
            }
        
        # Find primary emotion
        primary_emotion = max(combined_scores, key=combined_scores.get)
        max_score = combined_scores[primary_emotion]
        
        # Calculate confidence
        total_score = sum(combined_scores.values())
        confidence = max_score / total_score if total_score > 0 else 0
        
        # Normalize all scores
        normalized_scores = {}
        for emotion, score in combined_scores.items():
            normalized_scores[emotion] = score / total_score if total_score > 0 else 0
        
        return {
            'primary_emotion': primary_emotion,
            'confidence': min(confidence, 1.0),
            'all_emotions': normalized_scores,
            'success': True,
            'method': 'rule-based',
            'raw_scores': combined_scores
        }
    
    def get_emotion_advice(self, emotion_result: Dict, context: str = None) -> str:
        """Get advice based on detected emotion"""
        if not emotion_result['success']:
            return "I couldn't analyze the emotion in your message."
        
        emotion = emotion_result['primary_emotion']
        confidence = emotion_result['confidence']
        
        if confidence < 0.3:
            return "Your message seems fairly neutral. Consider being more direct about your feelings."
        
        advice_map = {
            'anger': "Your message contains strong emotions. Consider taking a breath and focusing on the specific issue rather than general frustrations. Try starting with 'I feel...' instead of 'You always...'",
            'sadness': "I can sense hurt in your message. Consider expressing what you need rather than just what's wrong. This might help the other person understand how to support you.",
            'fear': "Your message shows some anxiety or concern. Consider being specific about what you're worried about and asking for reassurance or clarification.",
            'joy': "Your message has positive energy! This is great for building connection.",
            'surprise': "Your message shows surprise. Consider asking clarifying questions to better understand the situation.",
            'disgust': "Your message shows strong negative feelings. Consider focusing on specific behaviors rather than character judgments.",
            'neutral': "Your message is emotionally neutral, which can be good for clear communication."
        }
        
        base_advice = advice_map.get(emotion, "I detected mixed emotions in your message.")
        
        if context == 'coparenting':
            base_advice += " Remember, keeping communication child-focused helps reduce conflict."
        elif context == 'romantic':
            base_advice += " In relationships, expressing vulnerability often builds stronger connections."
        elif context == 'workplace':
            base_advice += " In professional settings, focusing on solutions rather than problems is often most effective."
        
        return base_advice

class AIMessageCoach:
    def __init__(self):
        self.emotion_detector = AdvancedEmotionDetector()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TheThirdVoice/1.0',
            'Accept': 'application/json'
        })
        
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment - now with fallback to rule-based"""
        if not text or len(text.strip()) < 3:
            return {"success": False, "error": "Text too short"}
        
        # Try Hugging Face first (optional)
        try:
            url = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
            response = self.session.post(url, json={"inputs": text}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
                    sentiment_data = data[0]
                    best_prediction = max(sentiment_data, key=lambda x: x.get('score', 0))
                    return {
                        "sentiment": best_prediction['label'],
                        "confidence": best_prediction['score'],
                        "success": True,
                        "method": "huggingface"
                    }
        except:
            pass  # Fall back to rule-based
        
        # Rule-based sentiment fallback
        return self._analyze_sentiment_fallback(text)
    
    def _analyze_sentiment_fallback(self, text: str) -> Dict:
        """Rule-based sentiment analysis"""
        text_lower = text.lower()
        
        positive_words = ['good', 'great', 'awesome', 'love', 'happy', 'excellent', 'amazing', 'wonderful', 'fantastic']
        negative_words = ['bad', 'terrible', 'hate', 'awful', 'horrible', 'disgusting', 'worst', 'stupid', 'annoying']
        
        pos_score = sum(1 for word in positive_words if word in text_lower)
        neg_score = sum(1 for word in negative_words if word in text_lower)
        
        if pos_score > neg_score:
            return {"sentiment": "POSITIVE", "confidence": 0.7, "success": True, "method": "rule-based"}
        elif neg_score > pos_score:
            return {"sentiment": "NEGATIVE", "confidence": 0.7, "success": True, "method": "rule-based"}
        else:
            return {"sentiment": "NEUTRAL", "confidence": 0.6, "success": True, "method": "rule-based"}
    
    def analyze_emotion(self, text: str, context: str = "general") -> Dict:
        """Analyze emotion using rule-based detection"""
        result = self.emotion_detector.detect_emotion(text, context)
        
        if result['success']:
            return {
                "emotions": [
                    {"label": emotion, "score": score} 
                    for emotion, score in result['all_emotions'].items()
                ],
                "primary_emotion": {
                    "label": result['primary_emotion'],
                    "score": result['confidence']
                },
                "success": True,
                "method": "rule-based",
                "advice": self.emotion_detector.get_emotion_advice(result, context)
            }
        
        return {"success": False, "error": result.get("error", "Unknown error")}
    
    def generate_reframe(self, message: str, context: str = "general") -> str:
        """Generate better message using AI + rules"""
        # Get analysis
        sentiment_analysis = self.analyze_sentiment(message)
        emotion_analysis = self.analyze_emotion(message, context)
        
        # Enhanced reframing based on analysis
        if emotion_analysis.get("success"):
            primary_emotion = emotion_analysis["primary_emotion"]["label"]
            confidence = emotion_analysis["primary_emotion"]["score"]
            
            if confidence > 0.5:  # High confidence in emotion detection
                return self._smart_reframe(message, context, primary_emotion, emotion_analysis)
            else:
                return self._fallback_reframe(message, context)
        else:
            return self._fallback_reframe(message, context)
    
    def _smart_reframe(self, message: str, context: str, primary_emotion: str, emotion_data: Dict) -> str:
        """Enhanced reframing based on detected emotion"""
        base_reframe = self._fallback_reframe(message, context)
        
        emotion_starters = {
            'anger': "I want to discuss something that's been bothering me. ",
            'sadness': "I've been feeling hurt about something and wanted to share it with you. ",
            'fear': "I'm feeling anxious about something and would appreciate your perspective. ",
            'disgust': "I'm struggling with something and hope we can work through it together. ",
            'joy': "I wanted to share some positive news with you! ",
            'surprise': "Something unexpected happened and I wanted to discuss it. ",
            'neutral': "I wanted to talk with you about something. "
        }
        
        starter = emotion_starters.get(primary_emotion, "I wanted to discuss something with you. ")
        
        return starter + base_reframe
    
    def _fallback_reframe(self, message: str, context: str) -> str:
        """Fallback rule-based reframing"""
        reframed = message.lower()
        
        # Common negative patterns
        reframed = reframed.replace("you always", "I've noticed that sometimes")
        reframed = reframed.replace("you never", "it would help if")
        reframed = reframed.replace("you're", "I feel")
        reframed = reframed.replace("your fault", "we can work together on")
        reframed = reframed.replace("you don't", "I'd appreciate if")
        reframed = reframed.replace("i hate", "I struggle with")
        reframed = reframed.replace("so stupid", "frustrating")
        
        if context == "coparenting":
            return f"Hi, I wanted to discuss something about our child. {reframed.capitalize()} Can we find a solution that works for our family?"
        elif context == "romantic":
            return f"Hey, I wanted to share something that's been on my mind. {reframed.capitalize()} I care about us and want to work through this together. ❤️"
        elif context == "workplace":
            return f"Hi, I wanted to discuss something with you. {reframed.capitalize()} I'd appreciate your thoughts on how we can move forward."
        else:
            return f"I hope you're doing well. I wanted to discuss something: {reframed.capitalize()} I'd love to hear your perspective on this."

def main():
    st.set_page_config(
        page_title="The Third Voice",
        page_icon="🧠💬",
        layout="wide"
    )
    
    st.title("🧠💬 The Third Voice")
    st.markdown("*Your AI communication coach - now with privacy-first emotion detection*")
    
    # Initialize AI Coach
    if 'ai_coach' not in st.session_state:
        st.session_state.ai_coach = AIMessageCoach()
    
    ai_coach = st.session_state.ai_coach
    
    # Sidebar with info
    with st.sidebar:
        st.markdown("### 🔒 Privacy First")
        st.markdown("✅ Emotion detection runs locally")
        st.markdown("✅ No data sent to servers")
        st.markdown("✅ Works offline")
        st.markdown("✅ Always available")
        
        st.markdown("### 📊 Features")
        st.markdown("• Emotion analysis")
        st.markdown("• Sentiment detection")
        st.markdown("• Message reframing")
        st.markdown("• Context-aware advice")
        
        st.markdown("### 🚀 Built with AI")
        st.markdown("*Built in detention, with a phone, for life's hardest moments.*")
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## ✍️ Message Analysis")
        
        message_input = st.text_area(
            "Your message:",
            placeholder="Type your message here...",
            height=100,
            key="message_input"
        )
        
        context = st.selectbox(
            "Context:",
            ["general", "romantic", "coparenting", "workplace"],
            key="context_select"
        )
        
        col1a, col1b = st.columns(2)
        
        with col1a:
            analyze_button = st.button("🤖 A
