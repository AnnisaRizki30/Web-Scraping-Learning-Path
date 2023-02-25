import twint
import nest_asyncio

#=================== Tweets Scrape ======================#

nest_asyncio.apply()

c = twint.Config()
c.Store_csv = True
c.User_full = True
c.Search ='Proyek IKN'
c.Since = '2022-01-01 00:00:00'

c.Until = '2022-12-30 00:00:00'
c.Pandas = True
twint.run.Search(c)

df5 = twint.storage.panda.Tweets_df
print(df5)