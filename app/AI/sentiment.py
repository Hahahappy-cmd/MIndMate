from textblob import TextBlob

def analyze_sentiment(text: str) -> dict:
    """Analyze sentiment of journal entry text"""
    analysis = TextBlob(text)
    sentiment_score = analysis.sentiment.polarity

    if sentiment_score > 0.1:
        label = "positive"
    elif sentiment_score < -0.1:
        label = "negative"
    else:
        label = "neutral"

    return {
        "sentiment_score": round(sentiment_score, 3),
        "sentiment_label": label
    }