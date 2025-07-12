import streamlit as st
from transformers import pipeline
import time
from typing import Dict, List

# AIMessageCoach class for sentiment analysis
class AIMessageCoach:
    def __init__(self):
        try:
            # Initialize sentiment analysis pipeline with a lightweight model
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased",  # Fallback model for stability
                device=-1  # Use CPU
            )
        except Exception as e:
            st.error(f"Failed to initialize sentiment analyzer: {e}")
            raise

    def analyze_message(self, text: str) -> Dict[str, float]:
        """Analyze the sentiment of a given text."""
        try:
            result = self.sentiment_analyzer(text)[0]
            return {"label": result["label"], "score": result["score"]}
        except Exception as e:
            st.error(f"Error analyzing message: {e}")
            return {"label": "ERROR", "score": 0.0}

# Cached function to create AIMessageCoach instance
@st.cache_resource
def get_ai_coach():
    return AIMessageCoach()

def main():
    # Initialize Streamlit app
    st.title("ThirdVoiceApp - Sentiment Analysis (Beta)")
    st.write("Enter a message to analyze its sentiment.")

    # Get AI coach instance
    try:
        ai_coach = get_ai_coach()
    except Exception as e:
        st.error(f"Failed to load AI coach: {e}")
        return

    # User input
    user_input = st.text_area("Your Message", "Type your message here...")

    if st.button("Analyze"):
        if user_input:
            with st.spinner("Analyzing..."):
                result = ai_coach.analyze_message(user_input)
                st.write(f"Sentiment: {result['label']}")
                st.write(f"Confidence Score: {result['score']:.2f}")
        else:
            st.warning("Please enter a message to analyze.")

if __name__ == "__main__":
    main()
