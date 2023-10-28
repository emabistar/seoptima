import requests
from bs4 import BeautifulSoup
import spacy
from textblob import TextBlob
import nltk
from nltk.corpus import wordnet
from itertools import chain
from flask import Flask, render_template, request

app = Flask(__name__)

nltk.download('wordnet')

# Load the English language model for spaCy
nlp = spacy.load("en_core_web_sm")

# Function to fetch a web page's HTML content
def fetch_html(url):
   try:
       response = requests.get(url)
       return response.text
   except Exception as e:
       print(f"Error fetching page: {e}")
       return None

# Function to suggest additional keywords based on synonyms
def suggest_keywords(text):
   doc = nlp(text)
   keywords = [token.text for token in doc if token.is_alpha and not token.is_stop]

   suggested_keywords = set(keywords)  # Start with the original keywords

   for keyword in keywords:
       # Find synonyms for each keyword using WordNet
       synsets = wordnet.synsets(keyword)
       synonyms = set(chain.from_iterable([word.lemma_names() for word in synsets]))
       suggested_keywords.update(synonyms)

   return suggested_keywords

# Function to analyze SEO elements with spaCy
def analyze_seo(url):
   html = fetch_html(url)
   if html:
       soup = BeautifulSoup(html, 'html.parser')

       title_tag = soup.find('title')
       title_text = title_tag.text if title_tag else '',


       meta_description = soup.find('meta', attrs={'name': 'description'})
       meta_description_text = meta_description['content'] if meta_description else ''

       # Analyze the content
       sentiment = TextBlob(title_text + " " + meta_description_text )
       sentiment_polarity = sentiment.sentiment.polarity
       sentiment_subjectivity = sentiment.sentiment.subjectivity

       keywords = suggest_keywords(title_text + " " + meta_description_text )

       return title_text, meta_description_text, sentiment_polarity, sentiment_subjectivity, list(keywords)
   else:
       return None
# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        if url:
            # Fetch and analyze SEO content
            html = fetch_html(url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')

                title_tag = soup.find('title')
                title_text = title_tag.text if title_tag else ''

                meta_description = soup.find('meta', attrs={'name': 'description'})
                meta_description_text = meta_description['content'] if meta_description else ''

                # Analyze the content
                sentiment = TextBlob(title_text + " " + meta_description_text)
                sentiment_polarity = sentiment.sentiment.polarity
                sentiment_subjectivity = sentiment.sentiment.subjectivity

                keywords = suggest_keywords(title_text + " " + meta_description_text)

                return render_template('result.html', url=url, title=title_text, description=meta_description_text, polarity=sentiment_polarity, subjectivity=sentiment_subjectivity, keywords=keywords)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)