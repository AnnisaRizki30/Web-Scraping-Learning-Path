import configparser
import tweepy
import csv
import pandas as pd
import numpy as np
import logging, time

config = configparser.ConfigParser()
config.read(r"C:\Users\Annisa Rizki\Desktop\Annisa Lianda\Github Source\Web Scraping\Social Media\Twitter Dev API\config.ini")

api_key = config['twitter']['api_key']
api_key_secret = config['twitter']['api_key_secret']
access_token = config['twitter']['access_token']
access_token_secret = config['twitter']['access_token_secret']

auth = tweepy.OAuthHandler(api_key, api_key_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

def tweet_scraper(query, lang="en", tweet_mode="extended", tweet_limit=1000):
    """
    This function takes Tweepy search_tweets parameters as arguments and returns a Pandas
    dataframe containing tweet data.

    :param query: a keyword search phrase (string)
    :param lang: limit results by language (default: English)
    :param tweet_mode: choose whether to extend tweets to full 280 characters.
    :param tweet_limit: the maximum number of tweets to return (default: 1000).
    """

    # First, let's create a dictionary that will store our tweet data. We
    # are using a dictionary because we can easily generate a Pandas dataframe
    # from the dictionary keys.
    #
    # The dictionary will be formatted so that its keys are parameters associated with
    # each tweet and its values are lists to which we will append results for each tweet:

    data = {
        "user_id": [], 
        "screen_name": [],
        "name": [],
        "verified": [],
        "followers_count": [],
        "followings_count": [],
        "tweets_count": [],
        "coordinates": [],
        "id": [],
        "created_at": [],
        "full_text": [],
        "retweet_count": [],
        "favorite_count": [],
        "hashtags": [],
        "user_mentions": [],
        "in_reply_to_user_id": [],
        "in_reply_to_screen_name": [],
        "is_quote_status": [],
        "is_retweet": [], # We will have to build this parameter ourselves; see below
        "retweet_og_id": [], # The ID of the original retweeted tweet
        "retweet_og_author_id": [], # The original author ID of a retweeted tweet
        "retweet_og_author_screen_name": [], # The original author screen name of a retweeted tweet
        "retweet_og_author_name": [], # The original author's name of a retweeted tweet
        "retweet_og_date": [], # The date of the original tweet
        "retweet_og_full_text": [], # OG full text of the retweet
        "retweet_og_retweet_count": [], # OG retweet count
        "retweet_og_favorite_count": [] # OG favorite count
    }

    # Search the tweets as we've already done, but this time, plug in the paremeter values
    # From the function arguments:

    for tweet in tweepy.Cursor(api.search_tweets, q=query, lang="id", tweet_mode=tweet_mode).items(tweet_limit):
        """
        We need to start with user level variables, meaning we are going to iterate
        through the user dictionary. We can do this easily! Then, we are going to
        append the data to the list in our data dictionary. Let's see how it's
        done:
        """

        # User ID:
        data["user_id"].append(tweet.user.id)
        # Screen name:
        data["screen_name"].append(tweet.user.screen_name)
        # Name:
        data["name"].append(tweet.user.name)
        # Verified status:
        data["verified"].append(tweet.user.verified)
        # Followers Count:
        data["followers_count"].append(tweet.user.followers_count)
        # Following Count:
        data["followings_count"].append(tweet.user.friends_count)
        # Tweets Count:
        data["tweets_count"].append(tweet.user.statuses_count)
        # Coordinates:
        data["coordinates"].append(tweet.coordinates)

        """
        Great! Now let's grab the tweet level data:
        """

        # Tweet ID:
        data["id"].append(tweet.id)
        # Date:
        data["created_at"].append(tweet.created_at)
        # Full text of tweet:
        data["full_text"].append(tweet.full_text)
        # Get retweet count:
        data["retweet_count"].append(tweet.retweet_count)
        # Get favorite count:
        data["favorite_count"].append(tweet.favorite_count)
        
        # NOTE: to get hashtags & user mentions, we need to iterate through
        # the entities sub dictionary. Then, we need to iterate through
        # the hashtag sub dictionary. It sounds bad, but it's not! 
        # We will save the hashtags to a list and append the list
        # to our data dictionary:

        hashtags = []
        # Try to get hashtags; if there is an error, then there are no hashtags
        # and we can pass:
        try:
            for hashtag in tweet.entities["hashtags"]:
                hashtags.append(hashtag["text"])
        except Exception:
            pass
        
        # Now append the hashtag list to our dataset! If there are no
        # hashtags, just set it equal to NaN:
        if len(hashtags) == 0:
            data["hashtags"].append(np.nan)
        else:
            data["hashtags"].append(hashtags)

        # We do the same thing for user mentions:
        mentions = []
        try:
            for mention in tweet.entities["user_mentions"]:
                mentions.append(mention["screen_name"])
        except Exception:
            pass
        

        if len(mentions) == 0:
            data["user_mentions"].append(np.nan)
        else:
            data["user_mentions"].append(mentions)

        # In reply to user id:
        data["in_reply_to_user_id"].append(tweet.in_reply_to_user_id)
        # In reply to user screen name:
        data["in_reply_to_screen_name"].append(tweet.in_reply_to_screen_name)
        # Check if quote status:
        data["is_quote_status"].append(tweet.is_quote_status)

        # We need to check if a tweet is a retweet ourselves. We can do this by checking
        # If the retweeted_status key is present in the JSON:
        if "retweeted_status" in tweet._json.keys():
            # Then it is a retweet:
            data["is_retweet"].append(True)
            # Get OG tweet id:
            data["retweet_og_id"].append(tweet.retweeted_status.id)
            # Get OG author ID:
            data["retweet_og_author_id"].append(tweet.retweeted_status.user.id)
            # Get OG author screen name:
            data["retweet_og_author_screen_name"].append(tweet.retweeted_status.user.screen_name)
            # Get OG author name:
            data["retweet_og_author_name"].append(tweet.retweeted_status.user.name)
            # Get date of OG tweet:
            data["retweet_og_date"].append(tweet.retweeted_status.created_at)
            # Get OG full text:
            data["retweet_og_full_text"].append(tweet.retweeted_status.full_text)
            # Get OG retweet count:
            data["retweet_og_retweet_count"].append(tweet.retweeted_status.retweet_count)
            # Get OG favorite count:
            data["retweet_og_favorite_count"].append(tweet.retweeted_status.favorite_count)
        else:
            # Set is_retweet to false and all other values to np.nan:
            data["is_retweet"].append(False)
            data["retweet_og_id"].append(np.nan)
            data["retweet_og_author_id"].append(np.nan)
            data["retweet_og_author_screen_name"].append(np.nan)
            data["retweet_og_author_name"].append(np.nan)
            data["retweet_og_date"].append(np.nan)
            data["retweet_og_full_text"].append(np.nan)
            data["retweet_og_retweet_count"].append(np.nan)
            data["retweet_og_favorite_count"].append(np.nan)
    
    df = pd.DataFrame(data)
    return df


query = "Covid Indonesia"
tweet_mode = "extended"
tweet_limit = 10000

df = tweet_scraper(query=query, lang='id', tweet_mode=tweet_mode, tweet_limit=tweet_limit)


query = "proyek IKN"
tweet_mode = "extended"
tweet_limit = 10000

df1 = tweet_scraper(query=query, lang='id', tweet_mode=tweet_mode, tweet_limit=tweet_limit)


query = "@jokowi -filter:retweets"
tweet_mode = "extended"
tweet_limit = 10000

df2 = tweet_scraper(query=query, lang='id', tweet_mode=tweet_mode, tweet_limit=tweet_limit)
print(df2)