import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()

api_key= os.getenv('NEWS_API_KEY')
url = f'https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}'

response = requests.get(url)
data = response.json()

# Print one article nicely formatted
print(json.dumps(data['articles'][0], indent=2))