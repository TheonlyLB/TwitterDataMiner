"""
A bot must continuously watch for activity and react automatically

Stages of Development:
Find guides and download packages/software-Done
Obtain data from Twitter API-Done
Store the data from streaming into a DataFrame:
1. Convert JSON object to python dict
2. Convert python dict to DataFrame - Done
Store tweet stream into JSON file - Done
Preprocessing
Process data
Visualise data
Clean code
Segment code into files

Twitter App Authentication Information
Consumer API key: 6HWqZjS31wNUHTksYqVFQcI4G
Consumer API secret: dCz5NF3NJzuzbtDbBJJy7bsgtioM6ToUbjJyAjKGyIMizAnIuh
Access Token: 1205006074773831680-92CcAm3U2MjrGRMXNYkJaTl5qrbj7a
Access Token Secret: WcHAKOMityqMtKveHGDbVMkIi3RFNxQf87v3HHhP8AnKW
"""
# Widens Python console session so full output is seen. Only works if data is in DataFrame
import pandas as pd
desired_width = 10000
pd.set_option('display.width', desired_width)
# Widens dataframe column to display long strings
pd.options.display.max_colwidth = 9000

import tweepy
import json
import time
from preprocessor.api import clean, parse

# Store Authentication Information as variables
consumer_key = "6HWqZjS31wNUHTksYqVFQcI4G"
consumer_secret = "dCz5NF3NJzuzbtDbBJJy7bsgtioM6ToUbjJyAjKGyIMizAnIuh"
access_token = "1205006074773831680-92CcAm3U2MjrGRMXNYkJaTl5qrbj7a"
access_token_secret = "WcHAKOMityqMtKveHGDbVMkIi3RFNxQf87v3HHhP8AnKW"

# Authenticate your app to Twitter
# Creating the authentication object
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# Setting your access token and secret
auth.set_access_token(access_token, access_token_secret)

# Creating the API object while passing in auth information
# Additional arguments ensures you are notified if app exceeds rate limit
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# Set target information
handle = "nytimes"

# Invoke the API object's methods to call the Twitter API
# Functions
def create_tweet():
    api.update_status("Hello Tweepy")

def print_user_info():
    user = api.get_user(handle)

    print("User details:")
    print(user.name)
    print(user.description)
    print(user.location)

    print("Last 20 Followers:")
    for follower in user.followers():
        print(follower.name)

def print_user_newest():
    # Using the API object to get 20 newest tweets from your/others' timeline
    # my_timeline = api.home_timeline()
    # screen_name is the account handle. tweet_mode='extended' shows full text of the tweets
    target_timeline = api.user_timeline(screen_name = handle, count = 20, exclude_replies = True,
                                        include_rts = False, tweet_mode='extended')

    for tweet in target_timeline:
    # print the text stored inside the tweet object
        print ('{',tweet.extended_tweet['full_text'],'}\n\n')

def print_relevant_to_topic():
    # The search term you want to find
    query = "President Trump"
    # Language code (follows ISO 639-1 standards)
    language = "en"
    # No. of most recent tweets obtained
    count = 20

    # Search public tweets containing the query
    results = api.search(q=query, lang=language, count=count, tweet_mode='extended')

    for tweet in results:
        print ("{",tweet.user.screen_name,":\n",tweet.extended_tweet['full_text'],"}\n\n")

def print_geographic_trends():
    # Set place id. Place id is the WOEID found from: https://nations24.com/. WOEID of SG: 23424948
    place_id = 23424948
    trends_result = api.trends_place(place_id)
    # trends_result object is a list of dictionaries, containing another list of dictionaries
    for trend in trends_result[0]['trends']:
        print(trend['name'])

"""
Streaming allows you to watch for new tweets that match certain criteria. 
The stream object produces the stream by getting tweets that match some criteria. 
The stream listener processes tweets from the stream.
Streams do not terminate automatically. To do so, return False from the on_status method
If clients exceed a limited number of attempts to connect to the streaming API in a window of time, they will receive error 420. 
The amount of time a client has to wait after receiving error 420 will increase exponentially each time they make a failed attempt.
"""
def print_stream():
    # tweepy.StreamListener does not have appropriate methods, so we create our own class. on_status processes the stream
    class MyStreamListener(tweepy.StreamListener):
        def __init__(self, api, time_limit=1):
            # api object stored as class attribute
            self.api = api
            # api.me() obtains user's information, which is stored in a class attribute
            self.me = api.me()

            self.start_time = time.time()
            self.limit = time_limit

            super(tweepy.StreamListener, self).__init__()

        def on_data(self, tweet):
            def isolate_url():
                # Isolate URLs for tweets that have it
                parsed_text = parse(tweet_dict["text"])
                link = parsed_text.urls
                if link != None:
                    print(parsed_text.urls[0])

            if (time.time() - self.start_time) < self.limit:
                # Convert json object into python dictionary
                # tweet_dict is NOT a nested dict. The operations here are being repeated to show multiple dicts
                tweet_dict = json.loads(tweet)


                # try-except to check whether tweet streamed exceeds 140 chars. If it does, keyword full_text from
                # dictionary attribute extended_tweet of tweet class is used to get full text.
                try:
                    # Use tweet-preprocessor package to clean text of tweets
                    # Default removes MENTION, RESERVED, HASHTAG, URL, NUMBER, EMOJI, and SMILEY
                    cleaned_text = clean(tweet_dict.extended_tweet['full_text'])

                except AttributeError:
                    cleaned_text = clean(tweet_dict["text"])

                # Create json file, convert clean tweet text to strings, and write to file
                with open('tweet.json', "w",encoding="utf8") as f:
                    f.write(str(cleaned_text))
                # Read content of json file to str var
                with open('tweet.json', "r",encoding="utf8") as f:
                    tweet_str = f.read()
                # Append the text of each tweet(dictionary) to empty list
                tweet_list.append(tweet_str)

            else:
                # End stream
                return False

        def on_error(self, status):
            # Tweepy’s Stream Listener passes error codes to an on_error. Returning False in on_error disconnects the stream.
            # on_error returns False as default for all error codes
            print("Error detected")

    #Create stream listener
    tweets_listener = MyStreamListener(api, time_limit=2)
    #Create the stream object
    stream = tweepy.Stream(api.auth, tweets_listener)
    #Obtain and filter tweets from the stream. Track is a list of keywords. Follow is a list of user ID strings.
    #Tweets from Stream are in JSON format, and has to be converted to Python
    #Donald Trump's twitter ID: 25073877
    stream.filter(track=["Trump"], languages=["en"])

# Create blank list to contain tweet text
tweet_list=[]
print_stream()
# Convert the list to DataFrame and print the DataFrame
df = pd.DataFrame(tweet_list)
print(df)

"""
#if status object has 'retweeted status' attribute, flag it as a retweet
is_retweet = False
if hasattr(tweet, "retweeted_status"):
    is_retweet = True


"""