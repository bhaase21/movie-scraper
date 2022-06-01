#!/usr/bin/python
import json
import time
import argparse
import praw
from datetime import datetime
from rtscraper import * 
from reddit import (find_trailers)
from utils import (make_request, 
                   get_epoch_release, 
                   translate_genres, 
                   get_imdb_id,  
                   slugify) 

from pymongo import MongoClient
import pprint

pp = pprint.PrettyPrinter(indent=4)

mongo_uri = 'mongodb+srv://admin:summer20@cluster0-mw6mt.mongodb.net/test?retryWrites=true&w=majority'

client = MongoClient(mongo_uri)

db = client.movies

API_KEY = 'c4b64aac5d73d9ac3a465fead55b0b72'

REDDIT_KEY = 'bC7w3dr2cDYepQ'
REDDIT_SECRET = 'RZNOsZ_jKQyhI9Lg2AT3bWN8u6k'

reddit = praw.Reddit(client_id=REDDIT_KEY, \
                     client_secret=REDDIT_SECRET, \
                     user_agent='YOUR_APP_NAME', \
                     username='sirius76', \
                     password='!Summer20')

now = int(time.time()) 

def update_trending(record):
    #try:

    db['trending'].update_one({'id': record["id"]}, {"$set": record}, upsert=True).upserted_id
    #db['trending'].insert_one(record)
    #except:
    #    print("Error inserting into trending")
    #    print(record)

def clear_trending_collection():
    print("Clearing trending collection")
    result = db['trending'].drop()

def get_movie(id):
     print(db['movies'].find_one({"id": show.get("id")}))

def update_trailer_date(id, index, timestamp=int(time.time())):
    if not timestamp:
        timestamp = now

    print("updating trailer with timestamp {}".format(timestamp))
    db[index].update_one({'id': int(id)}, {'$set': { 'latest_trailer_date': timestamp }})

def update_trailer_key(id, key, index):
    movie = db[index].find_one({"id": int(id)})

    if not movie.get("trailers"):
        trailers = [ {'key': key} ]
    else:
        movie["trailers"][-1]["key"] = key
        trailers = movie["trailers"]

    db[index].update_one({'id': int(id)}, {'$set': { 'trailers': trailers }})
    update_trailer_date(id, index)

def delete_trailer_key(id, index='movies'):
    trailers = es.get(index=index, doc_type='document', id=id, ignore=[404])["_source"].get("trailers")
    del trailers[-1]
    es.update(index=index, doc_type='document', id=id, body={'doc': {'trailers': trailers, 'latest_trailer_date': 0}})

def delete_movie(id):
    try:
        es.delete(index="movies",doc_type="document",id=id)
    except:
        print("movie {} not found".format(id))

def get_start_end(days_back, days_forward):
    start_epoch = now - (86400*int(days_back))
    end_epoch = now + (86400*int(days_forward))
    start = time.strftime('%Y-%m-%d', time.localtime(start_epoch))
    end = time.strftime('%Y-%m-%d', time.localtime(end_epoch))
    return start,end

def save(movies):
    collection = db.movies
    for m in movies:
        movie_id = db['movies'].update_one({'id': m["id"]}, {"$set": m}, upsert=True).upserted_id
        if movie_id != None:
            print("New Movie Added: {}".format(m["title"]))   
    return

def save_tv(series):
    collection = db.tv
    tv_id = db['tv'].update_one({'id': series["id"]}, {"$set": series}, upsert=True).upserted_id
    if tv_id != None:
        print("New Series Added: {}".format(tv_id))
    return

def get_release_data(id):
  release_url = "/3/movie/"+str(id)+"/release_dates?api_key=c4b64aac5d73d9ac3a465fead55b0b72"
  release_info = make_request(release_url)
  release_data = None
  rating = 'NR' 

  if release_info.get("results"):
    network = None
    release_data = None
    release_date_us = None
    release_date_uk = None
    for r in release_info['results']:
      if r['iso_3166_1'] == 'US' or r['iso_3166_1'] == 'GB':
        country = r['iso_3166_1']
        for c in r['release_dates']:
          if c['type'] == 3 or c['type'] == 1:
            if country == 'US':
              release_date_us = c['release_date'].split('T')[0]
            else:
              release_date_uk = c['release_date'].split('T')[0]
          elif c['type'] == 6 and (release_date_us != None or release_date_uk != None):
            if country == 'US':
              release_date_us = c['release_date'].split('T')[0]
              network = c.get('network')
            else:
              release_date_uk = c['release_date'].split('T')[0]
              network = c.get('network')

          if c['certification'] != '':
            rating = c['certification']

      release_data = { 'release_date_uk': release_date_uk, 'release_date_us': release_date_us, 'rating': rating, 'release_date_epoch_us': get_epoch_release(release_date_us), 'release_date_epoch_uk': get_epoch_release(release_date_uk), 'network': network } 
      
  return release_data

def get_credits(id, source):
  directors = []
  writers = []
  producers = []
  cast = []
  if source == 'movies':
      credits_url = "/3/movie/"+str(id)+"/credits?api_key=c4b64aac5d73d9ac3a465fead55b0b72"
  else:
      credits_url = "/3/tv/{}/season/1/credits?api_key=c4b64aac5d73d9ac3a465fead55b0b72".format(id)

  credits_info = make_request(credits_url)

  if not credits_info.get("status_code"):

      for c in credits_info.get('crew'):
          if c['job'] == 'Director':
              directors.append(c['name'].lower())
          if c['department'] == 'Writing':
              writers.append(c['name'].lower())
          if c['job'] == 'Producer':
              producers.append(c['name'].lower())

      for c in credits_info.get('cast')[:30]:
          if c['profile_path'] == '':
              c['profile_path'] = 'NA'
          if c['character'] == '':
              c['character'] = 'NA'

          cast.append({'name':c['name'].lower(),'profile_path':c['profile_path'], 'character':c['character']})

      if len(writers) < 1:
          writers.append('NA')
      if len(directors) < 1:
          directors.append('NA')
      if len(producers) < 1:
          producers.append('NA')
      if len(cast) < 1:
          cast.append({'name':'NA'})

  return directors, writers, cast, producers

def sanitize(m):
  if m['popularity'] == '':
    m['popularity'] = '0'
  if m['overview'] == '':
    m['overview'] = 'NA'
  
  m["title"] = m["title"].encode('utf8')
  return m

def get_movie_by_id(id, nosave = False):
  now = int(time.time())
  url = "/3/movie/"+str(id)+"?api_key=c4b64aac5d73d9ac3a465fead55b0b72&language=en-US&region=US&append_to_response=videos"
  m = make_request(url)
  if not m.get("id"):
      return
  network = ''

  existing = db['movies'].find_one({"id": m.get("id")})

  trailers = []
  trailer_count = 0
  latest_trailer = 0
  if m.get("videos"): 
    for t in m["videos"]["results"]:
        if t["type"] == "Trailer" or t["type"] == "Teaser":
            trailer_count = trailer_count + 1
            trailers.append({'key': t["key"], 'name': t["name"] })

    if existing != None:
        if existing.get("trailers"):
            latest_trailer = existing.get("latest_trailer_date")
            if trailer_count > len(existing["trailers"]):
                latest_trailer = now 
  #              print("007**** New trailer found ****")
        elif trailer_count > 0:
  #          print('**** first trailer found ')
            latest_trailer = now

  release_data = get_release_data(id)
  if release_data:
      network = release_data.get('network')
   
  genres = []
  for g in m['genres']:
    genres.append(g['name'])

  #imdb_id, runtime = get_imdb_id(m['id'])
  m = sanitize(m) 
  (directors, writers, cast, producers) = get_credits(m['id'], 'movies') 
  rt_rating = 0
  rt_count = 0
  rt_aud_count = 0
  rt_aud_rating = 0
  mc_rating = 0
  mc_count = 0
  imdb_rating = 0
#  if release_date:
#    release_date_epoch = get_epoch_release(release_date)
  #try:
  #    rt_rating, rt_count, rt_aud_rating, rt_aud_count = get_rt_rating(m['title'], release_date.split('-')[0])
  #except:
  #    print("Error getting ratings\n")

  if m['imdb_id'] != 0:
      imdb_rating = get_imdb_rating(m['imdb_id'])

  if  m.get('homepage'):
      if 'netflix' in m.get('homepage'):
          network = 'Netflix'

  if not release_data:
      if m["release_date"]:
          release_data = { "release_date_us": m["release_date"], "release_date_epoch_us": get_epoch_release(m["release_date"]),
                           "release_date_uk": None, "release_date_epoch_uk": 0, "rating": 0 }
      else:
          release_data = { 'release_date_us': '2019-05-05', 'release_date_epoch_us': 0,
                           'release_date_uk': '2019-05-05', 'release_date_epoch_uk': 0 
                         }

  result = []
  record = {
    'id': m['id'],
    'imdb_id': m.get('imdb_id'),
    'tagline': m.get('tagline'),
    #'title_search': m['title'].lower(),
    'title': m['title'].decode("utf-8"),
    'overview': m['overview'],
    'release_date_us': release_data["release_date_us"],
    'release_date_epoch_us': release_data["release_date_epoch_us"],
    'release_date_gb': release_data["release_date_uk"],
    'release_date_epoch_uk': release_data["release_date_epoch_uk"],
    'budget': m.get('budget'),
    'rating': release_data.get("rating"),
    'poster_path': m['poster_path'],
    'backdrop_path': m['backdrop_path'],
    'vote_average': m['vote_average'],
    'vote_count': m['vote_count'],
    'directors': directors,
    'writers': writers,
    'cast': cast,
    'producers': producers,
    'genre_ids': genres,
    'runtime': m['runtime'],
    'rt_rating': float(rt_rating),
    'rt_count': int(rt_count),
    'rt_aud_count': rt_aud_count,
    'rt_aud_rating': rt_aud_rating,
#    'mc_rating': mc_rating,
#    'mc_count': mc_count,
    'imdb_rating': float(imdb_rating),
    'popularity': m['popularity'],
    'hashkey': 1,
    'slug': slugify(m['title'].decode("utf-8"), m['id'], '-'), 
    'network': network
  }

  #if len(trailers) > 0:
  #    print("*** latest trailer date {}".format(latest_trailer))
  #    record.update({ 'trailers': trailers})
  #    record.update({ 'latest_trailer_date': latest_trailer})

  result.append(record)

  if nosave == False:  
      save(result)
  else:
      return record

def get_trending():
    clear_trending_collection()
    #url = "/3/movie/popular?api_key=c4b64aac5d73d9ac3a465fead55b0b72"
    url = "/3/trending/all/day?api_key=c4b64aac5d73d9ac3a465fead55b0b72"
    results = make_request(url)
  
    total_pages = results['total_pages']
    for x in range(1, 3): 
        results = make_request(url + "&page=" + str(x))
        for m in results['results']:
            result = get_movie_by_id(m['id'], True)
            if result:
                update_trending(result)
            else:
                print("Error with {}".format(result))
    
def get_recent(days_back, days_forward):
    start, end = get_start_end(days_back, days_forward)
    url = "/3/discover/movie?api_key=c4b64aac5d73d9ac3a465fead55b0b72&language=en-US&region=US&sort_by=popularity.desc&include_adult=false&include_video=false&primary_release_date.gte="+start+"&primary_release_date.lte="+end #+"&with_release_type=3"

    results = make_request(url)
    total_pages = results['total_pages']
    for x in range(1, total_pages):
        popular = make_request(url + "&page=" + str(x))

        for p in popular.get('results'):
            if p['popularity'] > 100:
              get_movie_by_id(p['id'])
            time.sleep(1.0)

def import_from_tmdb_export(file_name, index):
  data=[]
  count = 0
  with open(file_name) as f:
    for line in f:
        count = count + 1
        if count >= index:
          data.append(json.loads(line))
  count = index 
  for l in data:
    count = count + 1
    if l["adult"] == False:
      try:
          get_movie_by_id(l["id"])
      except:
          next 
      time.sleep(1.4)

def import_tv_show(id):
    url = "/3/tv/"+str(id)+"?api_key=c4b64aac5d73d9ac3a465fead55b0b72&append_to_response=videos"
    show = make_request(url)
    if show.get("id") == None:
      print("id NOne, returning")
      return

    name = show['name']
    backdrop_path = show['backdrop_path']
    poster_path = show['poster_path']
    popularity = show['popularity']
    seasons = len(show['seasons'])
    overview = show['overview']
    latest_season = show['seasons'][-1]
    latest_season_release_date = latest_season['air_date']
    number_of_episodes = show['number_of_episodes']
    last_air_date = show['last_air_date']
    slug = slugify(name, show["id"], '-')
    network = ''
    created_by = ''

    (directors, writers, cast, producers) = get_credits(show['id'], 'tv')

    if len(show['created_by']) > 0:
        created_by = show['created_by'][0]['name']

    if "Amazon" in show.get('networks'):
        network = 'Amazon'

    elif 'netflix' in show.get('homepage') or 'Netflix' in show.get('networks'):
        network = 'Netflix'
    
    elif len(show['networks']) > 0:
        network = show['networks'][0]['name']

    tmdb_vote_count = show['vote_count']
    tmdb_vote_average = show['vote_average']
    first_air_date = show['first_air_date']

    genres = []
    for g in show['genres']:
        genres.append(g['name'])

    rt_rating = 0
    rt_count = 0
    rt_aud_count = 0
    rt_aud_rating = 0
    imdb_id = 0
    if latest_season_release_date != '':
        try:
            latest_season_release_date_epoch = get_epoch_release(latest_season_release_date)
        except:
            latest_season_release_date_epoch = 0
        try:
            rt_rating, rt_count, rt_aud_rating, rt_aud_count = get_rt_rating_tv(name)
        except:
            print()

        if imdb_id != 0:
            imdb_rating = get_imdb_rating(imdb_id)
    else:
        latest_season_release_date_epoch = 0

    existing = db['tv'].find_one({"id": show.get("id")})

    trailers = []
    trailer_count = 0
    latest_trailer = 0
    if show.get("videos"):
      for t in show["videos"]["results"]:
          if t["type"] == "Trailer" or t["type"] == "Teaser":
              trailer_count = trailer_count + 1
              trailers.append({'key': t["key"], 'name': t["name"] })

      if existing != None:
          if existing.get("trailers"):
              latest_trailer = existing.get("latest_trailer_date")
              if trailer_count > len(existing["trailers"]):
                  latest_trailer = now
                  print("**** New trailer found ****")
          elif trailer_count > 0:
              print('**** first trailer found ')
              latest_trailer = now

    latest_trailer_date = 0
    series = {
              'id': show['id'],
              'type': 'tv',
              'title': name,
              'backdrop_path': backdrop_path,
              'poster_path': poster_path,
              'network': network,
              #'trailers': trailers,
              #'latest_trailer_date': latest_trailer,
              'latest_season_release_date': latest_season_release_date,
              'latest_season_release_date_epoch': latest_season_release_date_epoch,
              'number_of_episodes': number_of_episodes,
              'last_air_date': last_air_date,
              'created_by': created_by,
              'popularity': popularity,
              'rt_rating': float(rt_rating),
              'rt_count': int(rt_count),
              'tmdb_vote_count': tmdb_vote_count,
              'tmdb_vote_average': tmdb_vote_average,
              'genres': genres,
              'overview': '',
              'over_view': overview,
              'cast': cast, 
              'slug': slug,
              'seasons': seasons
    }    

    save_tv(series)
    
def get_tv_popular():
    results = make_request('/3/tv/popular?sort_by=popularity.desc&api_key=c4b64aac5d73d9ac3a465fead55b0b72&sort_by=release_date.desc')

    total_pages = results['total_pages']
    for x in range(1, total_pages):
        popular = make_request('/3/tv/popular?sort_by=popularity.desc&api_key=c4b64aac5d73d9ac3a465fead55b0b72' + "&page=" + str(x))

        for p in popular.get('results'):
            import_tv_show(p['id'])
            time.sleep(1.5)

def get_movie_popular():
    results = make_request('/3/movie/popular?sort_by=popularity.desc&api_key=c4b64aac5d73d9ac3a465fead55b0b72&region=US&include_adult=false&language=en-US')

    total_pages = results['total_pages']
    for x in range(1, total_pages):
        popular = make_request('/3/movie/popular?sort_by=popularity.desc&api_key=c4b64aac5d73d9ac3a465fead55b0b72&region=US&include_adult=false&language=en-US' + "&page=" + str(x))

        for p in popular.get('results'):
            get_movie_by_id(p['id'])
            time.sleep(1.0)

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="""TMDB scraper""")
    p.add_argument("--update")
    p.add_argument("--movieid")
    p.add_argument("--recent")
    p.add_argument("--trailer")
    p.add_argument("--trailerdate")
    p.add_argument("--tvtrailerdate")
    p.add_argument("--fetch")
    p.add_argument("--delete")
    p.add_argument("--tvpopular")
    p.add_argument("--tv")
    p.add_argument("--tvid")
    p.add_argument("--daysback", default=30)
    p.add_argument("--daysforward", default=30)
    p.add_argument("--trailerfind")
    p.add_argument("--updatetrailerkey")
    p.add_argument("--deletetrailerkey")
    p.add_argument("--trending")
 

    a = p.parse_args()

    if a.tvpopular:
        print("Running: Get Popular")
        get_tv_popular()

    if a.tvid:
        import_tv_show(a.tvid) 

    if a.tvid and a.trailerdate:
        update_trailer_date(a.tvid, 'tv', a.trailerdate)
 
    if a.recent:
        print("Running: Get Recent {} / {}".format(a.daysback, a.daysforward))
        get_recent(a.daysback, a.daysforward)
        print("End Running: Get Recent")

    elif a.update and a.movieid:
        get_movie_by_id(a.movieid)

    elif a.trailerdate and a.movieid:
        update_trailer_date(a.movieid, 'movies', a.trailerdate)

    if a.delete and a.movieid:
        delete_movie(a.movieid)

    if a.fetch and a.movieid:
        get_movie(a.movieid)

    if a.movieid and a.updatetrailerkey:
        update_trailer_key(a.movieid, a.updatetrailerkey, 'movies')

    if a.tvid and a.updatetrailerkey:
        update_trailer_key(a.tvid, a.updatetrailerkey, 'tv')

    if a.movieid and a.deletetrailerkey:
        delete_trailer_key(a.movieid)

    if a.trending:
        print("Running: Get Trending.....")
        get_trending()
        print("Get Trending Ended")

    if a.trailerfind:
        print("Checking /r/movies")
        subreddit = reddit.subreddit('movies')
        find_trailers(subreddit.new(), 'movies')

        print("Checking /r/television")
        subreddit = reddit.subreddit('television')
        find_trailers(subreddit.new(), 'tv')
