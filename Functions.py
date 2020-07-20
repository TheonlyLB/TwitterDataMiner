# Invoke the API object's methods to call the Twitter API
def create_tweet():
    api.update_status("Hello Tweepy")

def print_user_info():
    user = api.get_user('nytimes')

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
Finish preprocessing of tweets after tweet-preprocessor. Stop words are words which are useless in natural language
processing, such as 'the'.
"""
from nltk.corpus import stopwords # Natural Language Toolkit
from nltk.tokenize import word_tokenize
import re
import string
def filter_tweets(tweet):
    """
    In re, the pattern is the regular expression to be matched. The string is searched to match the pattern
    at the beginning of string. Flags are modifiers specified using bitwise OR (|).
    Returns string
    """
    # Emoji patterns
    # re.compile converts a regex pattern into a regex object(which has various methods) so pattern can be
    # efficiently reused. The regex pattern is passed as a string.
    emoji_pattern = re.compile("["
                               u"\U0001F601-\U0001F64F"  # emoticons
                               u"\U00002702-\U000027B0"  # dingbats
                               u"\U0001F680-\U0001F6C5"  # transport & map symbols
                               u"\U000024C2-\U0001F251"  # enclosed chars and flags 
                               u"\U0001F300-\U0001F5FF"  # uncategorized
                               u"\U00002000-\U000021FF"
                               u"\U00002300-\U000023FF"
                               u"\U000025A0-\U000026FF"
                               u"\U00002900-\U0000297F"
                               u"\U00002B00-\U00002BFF"
                               u"\U00003000-\U0000303F"
                               u"\U00003200-\U000032FF"
                               u"\U0001F000-\U0001F02F"

                               "]+")
    # Converts array of english stopwords to an ordered sequence of distinct elements
    stop_words = set(stopwords.words('english'))
    # replace the colon symbol left after tweepy preprocessing
    tweet = re.sub(r':', '', tweet)
    tweet = re.sub(r'‚Ä¶', '', tweet)
    # replace consecutive non-ASCII characters with a space
    tweet = re.sub(r'[^\x00-\x7F]+', ' ', tweet)
    # remove emojis from tweet
    tweet = emoji_pattern.sub(r'', tweet)

    # Splits strings into tokens/words based on whitespace and punctuation, returns a list
    word_tokens = word_tokenize(tweet)
    # Create empty list
    filtered_tweet = []
    # Loop through tokens in tweet
    for w in word_tokens:
        # check tokens against stop words and punctuations
        if w not in stop_words and w not in string.punctuation:
            # append filtered text to list
            filtered_tweet.append(w)
    # convert list to string
    return ' '.join(filtered_tweet)