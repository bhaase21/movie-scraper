#!/usr/bin/python
import time
from pymongo import MongoClient
import pprint

mongo_uri = 'mongodb+srv://admin:summer20@cluster0-mw6mt.mongodb.net/test?retryWrites=true&w=majority'

client = MongoClient(mongo_uri)

db = client.movies

def find_trailers(posts, index):
    if index == 'tv':
        release_date_field = 'latest_season_release_date'
    else:
        release_date_field = 'release_date_us'
    for r in posts:
            if ('trailer' in r.title.lower() or 'teaser' in r.title.lower()) and 'honest' not in r.title.lower() and 'recut' not in r.title.lower():
                if '-' in r.title or '|' in r.title or 'official' in r.title.lower():
                    print('step 1 ' + r.title)
                    if 'season' in r.title.lower():
                        print("Split on season")
                        r.title = r.title.lower().split('season')[0]
                    if '-' in r.title:
                        query = { "query": { "match": { "title": r.title.split(' - ')[0].strip() } } }
                    elif '|' in r.title:
                        query = { "query": { "match": { "title": r.title.split('|')[0].strip() } } }
                    else:
                        query = { "query": { "match": { "title": r.title.lower().split('offical')[0].strip() } } }
       
                    print("** Running query {}".format(query['query']['match']['title']))
                    run_query = db[index].find_one({'title': query['query']['match']['title']}) 

                    if run_query == None:
                        break

                    movie = run_query
                    title = movie["title"].split('–')[0] #.replace(':', '')
                    print("Looking for {} IN {}".format(title.replace('-',' ').lower(), r.title.lower()))

                    #if title.replace('-',' ').lower() in r.title.lower():
                    if title.lower() in r.title.lower():
                        print("found")
                        #print("derp")
                        #print(movie["_source"].get(release_date_field))
                        #if movie["_source"].get(release_date_field):
                        #    print("derp 2")
                        try: 
                            year = movie.get(release_date_field).split('-')[0]
                        except:
                            year = 2019 
                        if int(year) >= 2019 or not year:
                            if "youtu.be" in r.url or "youtube" in r.url:
                                if 'watch?v=' in r.url:
                                    key = r.url.split('=')[-1]
                                    exists = False
                                else: 
                                    key = r.url.split('/')[-1]
                                    exists = False
                            if movie.get("trailers"):
                                for trailer in movie["trailers"]:
                                    if trailer["key"] in r.url:
                                        exists = True
                            else:
                                movie.update({ "trailers": [] })
                            if not exists:
                                movie["trailers"].append({'key': key, 'name': r.title})
                                movie["latest_trailer_date"] = int(time.time())
                                print("Adding trailer to {} {}".format(title, key))
                                db[index].update_one({'id': movie['id']}, {'$set': { movie }})
                                #es.update(index=index, doc_type='document', id=movie["_source"]["id"], body={'doc': movie]})

                            else:
                                print("Trailer already exists")
