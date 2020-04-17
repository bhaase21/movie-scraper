import requests
import http
import json
import time
import re
from datetime import datetime
from unicodedata import normalize

#conn = http.client.HTTPSConnection("api.themoviedb.org")

API_KEY = 'c4b64aac5d73d9ac3a465fead55b0b72'

GENRES_TO_ID = {
    '28': 'Action',
    '12': 'Adventure',
    '16': 'Animation',
    '35': 'Comedy',
    '80': 'Crime',
    '99': 'Documentary',
    '18': 'Drama',
    '10751': 'Faimly',
    '14': 'Fantasy',
    '36': 'History',
    '27': 'Horror',
    '10402': 'Music',
    '9648': 'Mystery',
    '10749': 'Romance',
    '878': 'Science Fiction',
    '53': 'Thriller',
    '10752': 'War',
    '10770': 'TV Movie',
    '37': 'Western'
}

_punct_re = re.compile(r'[\t !"\#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

def slugify(text, id, delim='-'):
    """Generates an slightly worse ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word.decode("utf-8").replace(':', ''))

    slug = '{}_{}'.format(id, '-'.join(result))
    return slug

def make_request(url):
  payload = "{}"
  request = requests.get('https://api.themoviedb.org{}'.format(url))
  data = request.json() 

  return data

def translate_genres(genre_ids):
  genres = []
  for g in genre_ids:
    genres.append(GENRES_TO_ID[str(g)])

  if len(genres) < 1:
    genres.append('NA')
  return genres

def get_imdb_id(id):
  url = "/3/movie/"+str(id)+"?api_key=c4b64aac5d73d9ac3a465fead55b0b72"
  movie_detail = make_request(url)

  if movie_detail.get('imdb_id') == '':
    movie_detail['imdb_id'] = '0'
  return movie_detail.get('imdb_id'), movie_detail.get('runtime')

def get_epoch_release(release_date):
  epoch = 0
  try:
    epoch = int(time.mktime(time.strptime(release_date, "%Y-%m-%d")))
  except:
    epoch = 0 

  return epoch
