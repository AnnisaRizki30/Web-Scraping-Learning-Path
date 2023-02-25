from urllib.request import urlopen
from bs4 import BeautifulSoup
import json
import re

VERSION = '0.1.0'

RESPONSE = {
    'url': str,
    'title': str,
    'upload_date': str,
    'duration': str,
    'description': str,
    'genre': str,
    'views': int,
    'likes': int,
    'thumbnail_url': str,
    'channel_name': str,
    'channel_url': str,
    'subscribers': int,
    'is_paid': bool,
    'is_unlisted': bool,
    'is_family_friendly': bool,
}

def is_true(string):
    return string.lower() not in ['false', '0']

def remove_comma(string):
    return ''.join(string.split(','))

def make_soup(url):
    html = urlopen(url).read()
    return BeautifulSoup(html, 'html.parser')

def scrape_video_data(url):
    try:
        soup = make_soup(url)
        soup_itemprop = soup.find(id='watch7-content')
        
        video = RESPONSE
        if len(soup_itemprop.contents) > 1:
            video['url'] = url
            # Get data from tags having `itemprop` attribute
            for tag in soup_itemprop.find_all(itemprop=True, recursive=False):
                key = tag['itemprop']
                if key == 'name':
                    # Get video's title
                    video['title'] = tag['content']
                elif key == 'duration':
                    # Get video's duration
                    video['duration'] = tag['content']
                elif key == 'datePublished':
                    # Get video's upload date
                    video['upload_date'] = tag['content']
                elif key == 'genre':
                    # Get video's genre (category)
                    video['genre'] = tag['content']
                elif key == 'paid':
                    # Is the video paid?
                    video['is_paid'] = is_true(tag['content'])
                elif key == 'unlisted':
                    # Is the video unlisted?
                    video['is_unlisted'] = is_true(tag['content'])
                elif key == 'isFamilyFriendly':
                    # Is the video family friendly?
                    video['is_family_friendly'] = is_true(tag['content'])
                elif key == 'thumbnailUrl':
                    # Get video thumbnail URL
                    video['thumbnail_url'] = tag['href']
                elif key == 'interactionCount':
                    # Get video's views
                    video['views'] = int(tag['content'])
                    # Get video description
                elif key == 'description':
                    video['description'] = tag['content']

            # Get the video tags
            video["tags"] = ', '.join([ meta.attrs.get("content") for meta in soup.find_all("meta", {"property": "og:video:tag"}) ])

            data = re.search(r"var ytInitialData = ({.*?});", soup.prettify()).group(1)
            data_json = json.loads(data)
            videoPrimaryInfoRenderer = data_json['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer']
            videoSecondaryInfoRenderer = data_json['contents']['twoColumnWatchNextResults']['results']['results']['contents'][1]['videoSecondaryInfoRenderer']
            
            # Number of likes
            likes_label = videoPrimaryInfoRenderer['videoActions']['menuRenderer']['topLevelButtons'][0]['segmentedLikeDislikeButtonRenderer']['likeButton']['toggleButtonRenderer']['defaultText']['accessibility']['accessibilityData']['label'] # "No likes" or "###,### likes"
            likes_str = likes_label.split(' ')[0].replace(',','')
            video['likes'] = '0' if likes_str == 'No' else likes_str

            # Channel details
            channel_tag = soup.find("meta", itemprop="channelId")['content']
            # Channel name
            channel_name = soup.find("span", itemprop="author").next.next['content']
            # Channel URL
            channel_url = f"https://www.youtube.com/{channel_tag}"
            # Number of subscribers as str
            channel_subscribers = videoSecondaryInfoRenderer['owner']['videoOwnerRenderer']['subscriberCountText']['accessibility']['accessibilityData']['label']
            video['channel_name'] = channel_name
            video['channel_url'] = channel_url 
            video['subscribers'] = channel_subscribers    

            return RESPONSE
            
    except Exception as e:
        print('Error:', str(e))
    