import time
import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import InvalidArgumentException
import pandas as pd
import youtube_metadata

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
DRIVER_PATH = r"C:\Users\Annisa Rizki\Desktop\Annisa Lianda\Github Source\Web Scraping\Driver\chromedriver.exe"
chrome_service = Service(DRIVER_PATH)
chrome_options = Options()
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_argument(f'user-agent={USER_AGENT}')
browser = webdriver.Chrome(service=chrome_service, options=chrome_options)

url = "https://www.youtube.com/@RaymondChins/videos"
browser.get(url)

time.sleep(3)

item = []
SCROLL_PAUSE_TIME = 1
last_height = browser.execute_script("return document.documentElement.scrollHeight")

item_count = 1000

while item_count > len(item):
    browser.execute_script("window.scrollTo(0,document.documentElement.scrollHeight);")
    time.sleep(SCROLL_PAUSE_TIME)
    new_height = browser.execute_script("return document.documentElement.scrollHeight")

    if new_height == last_height:
        break
    last_height = new_height


contents = []

try:
    for e in WebDriverWait(browser, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div#details'))):
        vurl = e.find_element(By.CSS_SELECTOR,'a#video-title-link').get_attribute('href')
        for url in vurl:
            result = youtube_metadata.scrape_video_data(url)
            print(result)
except:
    pass

browser.close()