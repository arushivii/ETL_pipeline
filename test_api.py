import requests
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('NEWS_API_KEY')
url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}'

response = requests.get(url)
data = response.json()

print(f"Status: {data['status']}")
print(f"Total articles: {data['totalResults']}")
print(f"First article title: {data['articles'][0]['title']}")