import requests
import os
import nltk
import yfinance as yf
from nltk.sentiment import SentimentIntensityAnalyzer
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")

if api_key is None:
    raise ValueError("Api key is missing. Ad it to .env.")

print("Api key loaded successfully")

try:
    nltk.data.find("sentiment/vader_lexicon.zip")
    print(nltk.data.find("sentiment/vader_lexicon.zip"))
except LookupError:
    nltk.download("vader_lexicon")


URL = f"https://newsapi.org/v2/everything?q=stocks&language=en&apiKey={api_key}"


ticker_symbol = "SPG"

stock = yf.Ticker(ticker_symbol)

print(stock.info["sector"])

print(stock.info)

response = requests.get(URL)
raw_news_data = response.json()
sentiment = SentimentIntensityAnalyzer()
print("this is all news \n", raw_news_data)


def news_fetch(news_data):
    for article in news_data["articles"][:5]:
        title = article["title"]
        url = article["url"]
        sentiment_value = sentiment.polarity_scores(title)

        message_date = article["publishedAt"]
        message_date_ymd = datetime.strptime(message_date, "%Y-%m-%dT%H:%M:%SZ").date()

        print(f"News title: {title}")
        print(f"URL: {url}")
        print(f"Date: {message_date_ymd}")
        print(f"Sentiment value compounded: {sentiment_value["compound"]}")
        print("-" * 50)


# news_fetch(raw_news_data)
