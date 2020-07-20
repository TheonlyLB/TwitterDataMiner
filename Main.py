import pandas as pd
# import twitter keys and tokens
from config import *
from Functions import filter_tweets
import tweepy # twitter api package
import json
import time
from preprocessor.api import clean, parse
from textblob import TextBlob
from elasticsearch import Elasticsearch

# Widens pandas display width so full output is seen.
desired_width = 5000
pd.set_option('display.width', desired_width)
# Prevents pandas from truncating long strings in display by increasing max col width
pd.options.display.max_colwidth = None

# Authenticate your app to Twitter
# Creating the authentication object
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# Setting your access token and secret
auth.set_access_token(access_token, access_token_secret)

# Creating the API object while passing in auth information
# Additional arguments ensures you are notified if app exceeds rate limit
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# create instance of elasticsearch
es = Elasticsearch()

# tweepy.StreamListener does not have appropriate methods, so we create our own class. on_status processes the stream
class MyStreamListener(tweepy.StreamListener):
    # Initialises attributes of the objects in a class
    def __init__(self, api, time_limit):
        # api object stored as class attribute
        self.api = api
        # api.me() obtains user's information, which is stored in a class attribute
        self.me = api.me()
        # Sets current system time as start time attr
        self.start_time = time.time()
        # Sets time limit as limit attr
        self.limit = time_limit

        # Test whether needed
        super(tweepy.StreamListener, self).__init__()
    # Methods of the class
    # Method for tweet processing
    def on_data(self, tweet):
        def isolate_url():
            # Isolate URLs for tweets that have it
            parsed_text = parse(tweet_dict["text"])
            link = parsed_text.urls
            if link != None:
                print(parsed_text.urls[0])

        if(time.time() - self.start_time < self.limit):
            # Convert json object from stream into python dictionary
            # tweet_dict is NOT a nested dict. The operations here are being repeated to show multiple dicts
            tweet_dict = json.loads(tweet)
            # If tweet object has 'retweeted_status' attribute, access full text under retweeted_status attr
            # try-except to check whether tweet streamed exceeds 140 chars.
            if hasattr(tweet_dict, "retweeted_status"):
                 # Use tweet-preprocessor package to clean text of tweets, returns string
                 # Default removes MENTION, RESERVED, HASHTAG, URL, NUMBER, EMOJI, and SMILEY
                try:
                    cleaned_text = clean(tweet_dict.retweeted_status.extended_tweet["full_text"])
                except AttributeError:
                    cleaned_text = clean(tweet_dict.retweeted_status["text"])
            else:
                try:
                    cleaned_text = clean(tweet_dict.extended_tweet["full_text"])
                except AttributeError:
                    #Sometimes gives key error for text
                    try:
                        cleaned_text = clean(tweet_dict["text"])
                    except:
                        cleaned_text = 'None'
            filtered_text = filter_tweets(cleaned_text)
            # Create TextBlob object which has sentiment attr.
            textblob_text = TextBlob(filtered_text)
            # Sentiment attr in turn has attr polarity[-1.0, 1.0] and subjectivity[0.0, 1.0]
            # Determine if sentiment is positive, negative, or neutral
            if textblob_text.sentiment.polarity < 0:
                sentiment = "negative"
            elif textblob_text.sentiment.polarity == 0:
                sentiment = "neutral"
            else:
                sentiment = "positive"

            # add text and sentiment info to elasticsearch
            es.index(index="sentiment",
                     doc_type="test-type",
                     body={"message": filtered_text,
                           "polarity": textblob_text.sentiment.polarity,
                           "subjectivity": textblob_text.sentiment.subjectivity,
                           "sentiment": sentiment})
            """
            # Create json file, convert clean tweet text to strings, and write to file
            with open('tweet.json', "w",encoding="utf8") as f:
                f.write(str(filtered_text))
            # Read content of json file to str var
            with open('tweet.json', "r",encoding="utf8") as f:
                tweet_str = f.read()
             # Append the text of each tweet(dictionary) to empty list
            tweet_list.append(tweet_str)
            """
            return True

        else:
            # End stream
             return False

    def on_error(self, status):
        # Tweepy’s Stream Listener passes error codes to an on_error. Returning False in on_error disconnects the stream.
        # on_error returns False as default for all error codes
        print("Error detected")


if __name__ == '__main__':
    # Create blank list to contain tweet text
    tweet_list = []
    # Create MyStreamListener class object and pass in input for attributes (Set time limit of stream)
    tweets_listener = MyStreamListener(api, time_limit=1)
    # Create the stream object
    stream = tweepy.Stream(api.auth, tweets_listener)
    # Obtain and filter tweets from the stream. Track is a list of keywords. Follow is a list of user ID strings.
    """
    If error message "No connection could be made because the target machine actively refused it" appears, the server 
    has a full backlog.
    """
    # Donald Trump's twitter ID: 25073877
    stream.filter(track=["obama"], languages=["en"])
    """
    # Convert the list to DataFrame and print the DataFrame
    df = pd.DataFrame(tweet_list)
    print(df)
    """

"""


"""