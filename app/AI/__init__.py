# Make ai directory a Python package
from .sentiment import analyze_sentiment, analyze_sentiment_advanced, analyze_emotion_trends
from .summarizer import generate_weekly_summary

__all__ = [
    "analyze_sentiment", 
    "analyze_sentiment_advanced", 
    "analyze_emotion_trends",
    "generate_weekly_summary"
]