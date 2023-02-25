import pandas as pd
import numpy as np 
import datetime 
from tqdm import tqdm
import snscrape.modules.twitter as sntwitter


#=================== Tweets Scrape ======================#

query = "Proyek IKN"

date = 'since:2022-01-01 until:2023-02-08'

tweets = []

limit = 10000

for i, tweet in tqdm ( 
    enumerate(
        sntwitter.TwitterSearchScraper(f'{query + date} lang:id').get_items(),
    ),
    total = limit,
):
    if i > limit:
       break
    tweets.append([tweet.date, tweet.id, tweet.conversationId, tweet.rawContent, tweet.user.username, 
                   tweet.user.location, tweet.user.friendsCount, tweet.user.followersCount, 
                   tweet.user.statusesCount, tweet.lang, tweet.hashtags, tweet.replyCount, 
                   tweet.retweetCount, tweet.likeCount, tweet.quoteCount, tweet.mentionedUsers,
                   tweet.sourceLabel, tweet.coordinates
                   ])
 
df4 = pd.DataFrame(tweets, columns=['DateTime', 'Id', 'ConversationId', 'Text', 'Username', 'Location', 
                                    'FollowingCount', 'FollowersCount', 'StatusCount','Language',
                                    'Hashtags', 'RepliesCount', 'RetweetsCount', 'LikesCount',
                                    'QuotesCount', 'MentionedUsers', 'Source', 'Coordinates'])

print(df4)