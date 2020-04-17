import requests
import re
def get_rt_rating(title, year):
  rating = 0
  count = 0
  aud_score = 0
  aud_count = 0
  title = title.replace(" ", "_")
  title = title.replace(":", "")
  title = title.replace(",", "")
  title = title.replace("'", "")
  title = title.replace(".", "")
  try:
      page = requests.get("https://www.rottentomatoes.com/m/"+title+"_"+year)
  except:
      return 0, 0

  if str(page).find("[404]") != -1:
    page = requests.get("https://www.rottentomatoes.com/m/"+title)

  if str(page).find("[200]") != -1:
    m = re.search('ratingValue":(.+?),', str(page.content))
    if m != None:
      rating = m.group(1)
    m = re.search('reviewCount":(.+?),', str(page.content))
    if m != None:
      count = m.group(1)
    aud_score_step1 = re.search('audience-score meter(.*?)</span>', str(page.content))
    try:
        aud_score_step2 = re.search('style="vertical-align:top">(.*?)%', str(aud_score_step1.group(1)))
    except:
        aud_score_step2 = 0

    if aud_score_step2:
        aud_score = aud_score_step2.group(1)
        aud_count_step1 = re.search('>User Ratings:</span>(.*?)</div>', str(page.content))

        if aud_count_step1:
            aud_count = int(aud_count_step1.group(1)[2:].replace(',', ''))
                            
  count = count.replace('}','') 
  print("** rating: {}".format(rating))    

  if count == 'null':
      count = 0
  if rating == 'null':
      rating = 0

  return rating, count, aud_score, aud_count

def get_rt_rating_tv(title):
  rating = 0
  count = 0
  year = 0
  title = title.replace(" ", "_")
  title = title.replace(":", "")
  title = title.replace(",", "")
  title = title.replace("'", "")
  title = title.replace(".", "")
  try:
      page = requests.get("https://www.rottentomatoes.com/tv/"+title)
  except:
      return 0, 0
  if str(page).find("[404]") != -1:
    page = requests.get("https://www.rottentomatoes.com/tv/"+title+"_"+str(year))

  if str(page).find("[200]") != -1:
    m = re.search('ratingValue":(.+?),', str(page.content))
    if m != None:
      rating = m.group(1)[:-1]
    m = re.search('reviewCount":(.+?),', str(page.content))
    if m != None:
      count = m.group(1)
  return rating, count

def get_imdb_rating(id):
  _rating = 0
  rating = 0
  count = 0
  headers = {'User-Agent': 'UserAgentString'}
  url = "http://www.imdb.com/title/"+str(id)
  page = requests.get(url, headers=headers)
  m = re.search('<span itemprop="ratingValue">(.+?)</span>', str(page.content))
  if m != None:
      rating = m.group(1)
#      _rating = re.search('<span>(.+?)</span>', str(m.group(0)))
#  if _rating != None:
#    rating = _rating.group(1)
  print("IMDB Rating {}".format(rating))
  return rating

def get_metacritic_rating(title, year):
    headers = {'User-Agent': 'UserAgentString'}
    rating = 0
    count = 0
    url = "http://www.metacritic.com/movie/"
    title = title.replace(" ", "-")
    title = title.replace(":", "")
    title = title.replace(",", "")
    title = title.replace("'", "")
    title = title.replace(".", "")

    url = "http://www.metacritic.com/movie/{}".format(title.lower())
    page = requests.get(url, headers=headers)
    if str(page).find("[200]") != -1:
        m = re.search('etascore_w larger movie(.+?)</span>', str(page.content))
        try:
            rating = int(m.group(1).split('>')[1])
            m = re.search('based on (.*?) Critics',  str(page.content))
            count = int(m.group(1))  
        except:
           rating = 0
           count = 0
        return rating, count


