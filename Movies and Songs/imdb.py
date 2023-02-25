import time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from lxml import etree
import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import numpy as np
from tqdm import tqdm
import random
from random import randint
import json
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
DRIVER_PATH = r"C:\Users\Annisa Rizki\Desktop\Annisa Lianda\Github Source\Web Scraping\Driver\chromedriver.exe"
chrome_service = Service(DRIVER_PATH)
chrome_options = Options()
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_argument(f'user-agent={USER_AGENT}')
browser = webdriver.Chrome(service=chrome_service, options=chrome_options)

pages = np.arange(1, 700, 50)

headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
           'referrer': 'https://google.com',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
           'Accept-Encoding': 'gzip, deflate, br',
           'Accept-Language': 'en-US,en;q=0.9',
           'Pragma': 'no-cache',
          }

titles = []
imdb_links = []
years = []
times = []
certificates = []
genres = []
imdb_ratings = []

for page in pages:
    page = requests.get('https://www.imdb.com/search/title/?release_date=2017-01-01,2023-02-21&user_rating=1.0,10.0&start=' + str(page) + '&ref_=adv_nxt', headers=headers)
    soup = BeautifulSoup(page.text, 'lxml')

    movie_div = soup.find_all('div', class_='lister-item mode-advanced')
    time.sleep(randint(2,10))
    
    for container in movie_div:
        name = container.h3.a.text
        titles.append(name)
        
        link =  container.h3.a["href"]
        get_url = '{0}{1}'.format('https://www.imdb.com', link)
        imdb_links.append(get_url)

        year = container.h3.find('span', class_='lister-item-year').text
        years.append(year)

        runtime = container.find('span', class_='runtime').text if container.p.find('span', class_='runtime') else ''
        times.append(runtime)

        certificate = container.find('span', class_='certificate').text if container.p.find('span', class_='certificate') else ''
        certificates.append(certificate)

        genre = container.find('span', class_='genre').text.strip().replace('\n', '') if container.p.find('span', class_='genre') else ''
        genres.append(genre)

        rating = float(container.strong.text)
        imdb_ratings.append(rating)

movies = pd.DataFrame({'Movie_Name':titles,
                       'Movie_Link':imdb_links,
                       'Year':years,
                       'Duration':times,
                       'Certificate':certificates,
                       'Genre':genres,
                       'Rating':imdb_ratings,
                      })

movies = movies.drop_duplicates(subset=['Movie_Name'], keep='first')
movies = movies.reset_index(drop = True)

movies_data = pd.DataFrame()

for i, url in enumerate(movies['Movie_Link']):
    res = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(res.text, 'lxml')
    soup_html = BeautifulSoup(res.text, "html.parser")
    dom = etree.HTML(str(soup_html))
    
    temp_dict = {}

    try: 
        movie_info_json = json.loads(soup.select_one('script[type="application/ld+json"]').text)
        
        try:
            image_link = movie_info_json['image']
            temp_dict['Movie_Image'] = image_link
        except AttributeError:
            image_link = ''
        
        try:
            trailer_link = movie_info_json['trailer']['embedUrl']
            temp_dict['Trailer_Link'] = trailer_link
        except KeyError:
            trailer_link = ''
        
        try:
            synopsis = movie_info_json['description']
            temp_dict['Synopsis'] = synopsis
        except KeyError:
            synopsis = ''

        try:
            date_published = movie_info_json['datePublished']
            try:
                temp_dict['Date_Published'] = date_published
            except AttributeError:
                date_published = ''
        except KeyError:
                pass

        try:
            keywords = movie_info_json['keywords']
            temp_dict['Keywords'] = keywords
        except KeyError:
            keywords = ''
        
        try:
            actors = movie_info_json['actor']
            for actor in actors:
                temp_dict['Actors'] = [actor['name'] for actor in actors] 
        except KeyError:
            actors = ''

        new_url = url.replace("?ref_=adv_li_tt", "")
        temp_dict['Movie_Link'] = new_url

        movies_data = movies_data.append(temp_dict, ignore_index=True)
        
    except:
        pass

full_movies_data = pd.merge(movies, movies_data, on="Movie_Link", how="left")

user_review_link = pd.DataFrame()

temp_dict = {}

for url in full_movies_data['Movie_Link']:
    try:
      res = requests.get(url=url, headers=headers)
      soup = BeautifulSoup(res.text, 'html.parser')
      review_link = url+soup.find('a', text = 'User reviews').get('href')
      temp_dict['User_Review_Links'] = review_link
      user_review_link = user_review_link.append(temp_dict, ignore_index=True)
    except AttributeError :
      review_link = ''

final_movies = pd.concat([full_movies_data, user_review_link], axis=1)
final_movies.dropna(subset=['Duration', 'Certificate', 'User_Review_Links'], inplace = True)
final_movies = final_movies.reset_index(drop = True)


user_rating_data = pd.DataFrame()


for url in final_movies['User_Review_Links'][:1]:
  browser.get(url)
  time.sleep(1)


  body = browser.find_element(By.CSS_SELECTOR, 'body')
  body.send_keys(Keys.PAGE_DOWN)
  time.sleep(1)
  body.send_keys(Keys.PAGE_DOWN)
  time.sleep(1)
  body.send_keys(Keys.PAGE_DOWN)

  sel = Selector(text = browser.page_source)
  
  temp_dict = {}

  # Store each url in 
  temp_dict['User_Review_Links'] = url

  count = np.arange(1, 50, 25)

  for i in tqdm(count):
      try:
          css_selector = 'load-more-trigger'
          browser.find_element(By.ID, css_selector).click()
      except:
          pass

      reviews = browser.find_elements(By.CSS_SELECTOR, 'div.review-container')

      for m in tqdm(reviews):
          try:
              sel2 = Selector(text = m.get_attribute('innerHTML'))
              try:
                  rating = sel2.css('.rating-other-user-rating span::text').extract_first()
                  temp_dict['Rating'] = rating
              except:
                  rating = np.NaN
              try:
                  review = sel2.css('.text.show-more__control::text').extract_first()
                  temp_dict['Review'] = review
              except:
                  review = np.NaN
              try:
                  review_date = sel2.css('.review-date::text').extract_first()
                  temp_dict['Review_Date'] = review_date
              except:
                  review_date = np.NaN    
              try:
                  author = sel2.css('.display-name-link a::text').extract_first()
                  temp_dict['Author'] = author
              except:
                  author = np.NaN    
              try:
                  review_title = sel2.css('a.title::text').extract_first()
                  temp_dict['Review_Title'] = review_title
              except:
                  review_title = np.NaN
              try:
                  review_url = sel2.css('a.title::attr(href)').extract_first()
                  get_url = '{0}{1}'.format('https://www.imdb.com', review_url)
                  temp_dict['Review_Url'] = get_url
              except:
                  review_url = np.NaN

              user_rating_data = user_rating_data.append(temp_dict, ignore_index=True)
        
          except Exception as e:
              print(e)

print(user_rating_data)