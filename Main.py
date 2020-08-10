import itertools
import pandas as pd
from functions import filter_tweets, personal_classifier, TextBlob_Classifier, api
import tweepy
import json
import time
from preprocessor.api import clean
from matplotlib import pyplot as plt
from elasticsearch import Elasticsearch
from datetime import datetime
from nltk.corpus import stopwords
from string import punctuation

# Widens pandas display width so full output is seen.
desired_width = 5000
pd.set_option('display.width', desired_width)
# Prevents pandas from truncating long strings in display by increasing max col width
pd.options.display.max_colwidth = None

# Coordinates dictionary for countries
coordinates_dict = {'US': [-171.791110603, 18.91619, -66.96466, 71.3577635769],
                    'CA': [-140.99778, 41.6751050889, -52.6480987209, 83.23324],
                    'SG': [1.1304753, 1.4504753, 103.6920359, 104.0120359],
                    'MY': [100.085756871, 0.773131415201, 119.181903925, 6.92805288332],
                    'IN': [68.1766451354, 7.96553477623, 97.4025614766, 35.4940095078],
                    'GB': [-7.57216793459, 49.959999905, 1.68153079591, 58.6350001085],
                    'AU': [113.338953078, -43.6345972634, 153.569469029, -10.6681857235]}
coordinates_list = []

# create instance of elasticsearch
es = Elasticsearch(timeout=60)
# Checks for elasticsearch instance
if es.ping():
    print('Elasticsearch instance created')


# tweepy.StreamListener does not have appropriate methods, so we create our own class.
class MyStreamListener(tweepy.StreamListener):
    # Initialises attributes of class
    def __init__(self, api, time_limit):
        # api object stored as class attribute
        super().__init__(api)
        self.api = api
        # api.me() obtains user's information, which is stored in a class attribute
        self.me = api.me()
        # Sets current system time as start time attr
        self.start_time = time.time()
        # Sets time limit as limit attr. Multiply by 60 since time.time() is measured in seconds
        self.limit = time_limit * 60
        self.tweet_dict = {}
        self.filtered_text = ''

    # Processes the stream
    def on_data(self, tweet):
        # By default returns True to continue stream.
        if time.time() - self.start_time < self.limit:
            # Convert json object from stream into python dictionary
            # tweet_dict is NOT a nested dict. The operations here are being repeated to show multiple dicts
            self.tweet_dict = json.loads(tweet)
            # If user gathers tweets by region, only get text of tweets with the desired country code
            if chosen_filter == '2':
                """
                for country_code in country_code_list:
                    # Feature only works when using Enterprise API
                    if self.tweet_dict['user']['derived']['locations']['country_code'] == country_code:
                        if "retweeted_status" in self.tweet_dict:
                            try:
                                tweet_text = self.tweet_dict["retweeted_status"]["extended_tweet"]["full_text"]
                            except KeyError:
                                tweet_text = self.tweet_dict["retweeted_status"]["text"]
                        else:
                            try:
                                tweet_text = self.tweet_dict["extended_tweet"]["full_text"]
                            except KeyError:
                                try:
                                    tweet_text = self.tweet_dict["text"]
                                # ends processing of tweet if no text is found
                                except:
                                    return True
                    else:
                        continue
                """
                counter = 0
                for search_word in search_list:
                    if "retweeted_status" in self.tweet_dict:
                        try:
                            if search_word in self.tweet_dict["retweeted_status"]["extended_tweet"]["full_text"]:
                                tweet_text = self.tweet_dict["retweeted_status"]["extended_tweet"]["full_text"]
                                break
                            else:
                                counter += 1
                                continue
                        except KeyError:
                            if search_word in self.tweet_dict["retweeted_status"]["text"]:
                                tweet_text = self.tweet_dict["retweeted_status"]["text"]
                                break
                            else:
                                counter += 1
                                continue
                    else:
                        try:
                            if search_word in self.tweet_dict["extended_tweet"]["full_text"]:
                                tweet_text = self.tweet_dict["extended_tweet"]["full_text"]
                                break
                            else:
                                counter += 1
                                continue
                        except KeyError:
                            try:
                                if search_word in self.tweet_dict["text"]:
                                    tweet_text = self.tweet_dict["text"]
                                    break
                                else:
                                    counter += 1
                                    continue
                            # ends processing of tweet if no text is found
                            except:
                                return True

                if counter == len(search_list):
                    return True

            else:
                # If tweet object has 'retweeted_status' key, it is a retweet.
                # try-except to check whether tweet streamed exceeds 140 chars.
                # hasattr cannot be used for dict or JSON. 'in' is used instead
                # Use keys to index tweet_dict. If not found, KeyError is produced. AttributeError for JSON object
                if "retweeted_status" in self.tweet_dict:
                    try:
                        tweet_text = self.tweet_dict["retweeted_status"]["extended_tweet"]["full_text"]
                    except KeyError:
                        tweet_text = self.tweet_dict["retweeted_status"]["text"]
                else:
                    try:
                        tweet_text = self.tweet_dict["extended_tweet"]["full_text"]
                    except KeyError:
                        try:
                            tweet_text = self.tweet_dict["text"]
                        except:
                            return True

            """
            NOT WORKING FOR UNKNOWN REASON
            Checks whether status object is from original creator.
            Remove:
            Replies to any Tweet created by the user.
            Retweets of any Tweet created by the user.
            Manual replies containing user account handle
            """
            if chosen_filter == '1':
                for handle in twitter_handle_list:
                    try:
                        if self.tweet_dict["in_reply_to_screen_name"] == handle:
                            #print('1')
                            return True
                        else:
                            try:
                                if self.tweet_dict["retweeted_status"]["user"]["screen_name"] == handle:
                                    #print('2')
                                    return True
                                else:
                                    try:
                                        if self.tweet_dict["quoted_status"]["user"]["screen_name"] == handle:
                                            #print('3')
                                            return True
                                        elif handle in tweet_text:
                                            #print('4')
                                            return True
                                        else:
                                            #print('5')
                                            #print(self.tweet_dict)
                                            pass
                                    except KeyError:
                                        if handle in tweet_text:
                                            #print('6')
                                            return True
                                        else:
                                            #print('7')
                                            #print(self.tweet_dict)
                                            pass
                            except KeyError:
                                try:
                                    if self.tweet_dict["quoted_status"]["user"]["screen_name"] == handle:
                                        #print('8')
                                        return True
                                    elif handle in tweet_text:
                                        #print('9')
                                        return True
                                    else:
                                        #print('10')
                                        #print(self.tweet_dict)
                                        pass
                                except KeyError:
                                    if handle in tweet_text:
                                        #print('11')
                                        return True
                                    else:
                                        #print('12')
                                        #print(self.tweet_dict)
                                        pass
                    except KeyError:
                        if self.tweet_dict["in_reply_to_screen_name"] == handle:
                            #print('13')
                            return True
                        else:
                            try:
                                if self.tweet_dict["retweeted_status"]["user"]["screen_name"] == handle:
                                    #print('14')
                                    return True
                                else:
                                    try:
                                        if self.tweet_dict["quoted_status"]["user"]["screen_name"] == handle:
                                            #print('15')
                                            return True
                                        elif handle in tweet_text:
                                            #print('16')
                                            return True
                                        else:
                                            #print('17')
                                            #print(self.tweet_dict)
                                            pass
                                    except KeyError:
                                        if handle in tweet_text:
                                            #print('18')
                                            return True
                                        else:
                                            #print('19')
                                            #print(self.tweet_dict)
                                            pass
                            except KeyError:
                                try:
                                    if self.tweet_dict["quoted_status"]["user"]["screen_name"] == handle:
                                        #print('20')
                                        return True
                                    elif handle in tweet_text:
                                        #print('21')
                                        return True
                                    else:
                                        #print('22')
                                        #print(self.tweet_dict)
                                        pass
                                except KeyError:
                                    if handle in tweet_text:
                                        #print('23')
                                        return True
                                    else:
                                        #print('24')
                                        #print(self.tweet_dict)
                                        pass

            # string.punctuation is a string of all punctuation symbols
            punc_list = punctuation.split(',')
            # Converts array of english stopwords to an ordered sequence of distinct elements
            # Shifted from filter_tweets to avoid initialising stop_words every loop
            stop_words = set(stopwords.words('english') + punc_list + ['AT_USER', 'URL'])
            # Use tweet-preprocessor package to clean text of tweets, returns string
            # Default removes MENTION, RESERVED, HASHTAG, URL, NUMBER, EMOJI, and SMILEY
            clean_text = clean(tweet_text)
            filtered_text = filter_tweets(clean_text, stop_words)
            # Append text of new tweet to file
            with open('tweet.json', "a", encoding="utf8") as f:
                f.write(filtered_text)
                f.write('\nTHIS IS A NEW TWEET\n')
            # Append time of tweet
            with open('tweet_date.json', "a", encoding="utf8") as f:
                f.write(self.tweet_dict['created_at'])
                f.write("\nTHIS IS A NEW TWEET\n")
            # Append author of tweet
            with open('tweet_author.json', "a", encoding="utf8") as f:
                f.write(self.tweet_dict['user']['screen_name'])
                f.write("\nTHIS IS A NEW TWEET\n")
            # Append str location name of tweet
            with open('tweet_locations.json', "a", encoding="utf8") as f:
                try:
                    f.write(self.tweet_dict['user']['location'])
                    f.write("\nTHIS IS A NEW TWEET\n")
                # TypeError expected for write() since 'location' is a nullable field in tweets
                except TypeError:
                    f.write('None')
                    f.write("\nTHIS IS A NEW TWEET\n")
                    pass
            # Append number of retweets
            with open('tweet_retweets.json', "a", encoding="utf8") as f:
                f.write(str(self.tweet_dict['retweet_count']))
                f.write("\nTHIS IS A NEW TWEET\n")
            # Append number of likes
            with open('tweet_favorites.json', "a", encoding="utf8") as f:
                f.write(str(self.tweet_dict['favorite_count']))
                f.write("\nTHIS IS A NEW TWEET\n")

            return True

        else:
            # End stream
            return False

    def on_error(self, status_code):
        # Tweepy’s Stream Listener only passes error codes from Twitter to on_error.
        # Returning False in on_error disconnects the stream.
        # on_error returns False as default for all error codes
        # Disconnect stream upon error 420 (exceeding rate limit). Otherwise, continue stream
        if status_code == 420:
            return False
        print(f"Error code while streaming {status_code}")
        return True


if __name__ == '__main__':
    # Get user input for search query, reject blank input, convert to list of keywords
    while True:
        search_str = input("Key word/phrase used in the tweets."
                           "Search for multiple key words/phrases by separating them with ',' :")
        if not search_str.isspace():
            search_list = search_str.split(',')
            break
        print('Please enter valid input')

    # Get user input for streaming period, reject blank/non digit input and 0 < input
    while True:
        stream_period = input("Gather tweets published in the next X minutes:")
        is_blank = stream_period.isspace()
        if not is_blank and stream_period.isdigit() and 0 < int(stream_period):
            stream_period = int(stream_period)
            break
        print('Please enter valid input. Input should be a positive integer')

    # User chooses whether to gather tweets by account or region
    while True:
        chosen_filter = input("Gather tweets from specific accounts(1), specific countries(2),"
                              "or from worldwide(3):")
        account_list = []
        if chosen_filter == '1':
            # Store user input in str to use as parameter of plt.pie
            twitter_handle_str = input("Enter account handles separated by ',':")
            twitter_handle_list = twitter_handle_str.split(',')
            # Use each handle to get user object from api, append each user's id_str to list
            for twitter_handle in twitter_handle_list:
                user = api.get_user(twitter_handle)
                account_list.append(user.id_str)
            # Store str in common var to use as parameter of plt.pie
            title_origin = twitter_handle_str

            break
        elif chosen_filter == '2':
            # Get user input for country code
            # Store user input in str to use as parameter of plt.pie
            country_code_str = input("Choose the countries by their country codes separated by ','\n"
                                     "[USA : US, Canada : CA, Singapore : SG, Malaysia : MY\n"
                                     "India : IN, UK: GB, Australia : AU]:")
            country_code_list = country_code_str.split(',')
            # Store str in common var to use as parameter of plt.pie
            title_origin = country_code_str

            [coordinates_list.extend(coordinates_dict[country_code]) for country_code in country_code_list]
            break
        elif chosen_filter == '3':
            title_origin = 'around the world'
            break
        else:
            print("Please enter valid input")
            pass

    # Clear json files used to store tweet information
    open('tweet.json', 'w', encoding="utf8").close()
    open('tweet_date.json', 'w', encoding="utf8").close()
    open('tweet_author.json', 'w', encoding="utf8").close()
    open('tweet_locations.json', 'w', encoding="utf8").close()
    open('tweet_retweets.json', 'w', encoding="utf8").close()
    open('tweet_favorites.json', 'w', encoding="utf8").close()
    #try:
    # Create MyStreamListener class object and pass in input for attributes (Set time limit of stream)
    tweets_listener = MyStreamListener(api, time_limit=stream_period)
    stream = tweepy.Stream(api.auth, tweets_listener)
    # Obtain and filter tweets from the stream.
    # Track is a list of keywords. Follow is a list of user ID strings.

    # For each user specified in follow, the stream will contain:
    # Tweets created by the user.
    # Tweets which are retweeted by the user.
    # Replies to any Tweet created by the user.
    # Retweets of any Tweet created by the user.
    # Manual replies, created without pressing a reply button (e.g. “@twitterapi I agree”).

    # The stream will not contain:
    # Tweets mentioning the user (e.g. “Hello @twitterapi!”).
    # Manual Retweets created without pressing a Retweet button (e.g. “RT @twitterapi The API is great”).
    # Tweets by protected users.

    # Locations is a list of longitude,latitude pairs. It does not filter together with other parameters:
    # track=twitter & locations=X,Y match Tweets containing 'Twitter' OR from the location

    # Starts streaming
    if chosen_filter == '2':
        stream.filter(locations=coordinates_list, languages=["en"])
    else:
        stream.filter(track=search_list, follow=account_list, languages=["en"])
    #except Exception as e:
        # IncompleteRead Error can occur if the streaming filter that's chosen is too broad, causing you to
        # receive streams at a faster rate than you can accept.
        #print(e)


    """
    Use of Naive Bayes Analyzer breaks the stream. Hence, all tweets in specified time period are stored in JSON file
    for processing after streaming.
    """
    # Read content of json file to str var
    with open('tweet.json', "r", encoding="utf8") as f:
        tweet_str = f.read()
    # Convert str var to list for iteration
    tweet_list = tweet_str.split("\nTHIS IS A NEW TWEET\n")

    with open('tweet_date.json', "r", encoding="utf8") as f:
        tweetdate_str = f.read()
    tweetdate_list = tweetdate_str.split("\nTHIS IS A NEW TWEET\n")

    with open('tweet_author.json', "r", encoding="utf8") as f:
        tweetauthor_str = f.read()
    tweetauthor_list = tweetauthor_str.split("\nTHIS IS A NEW TWEET\n")

    with open('tweet_locations.json', "r", encoding="utf8") as f:
        tweetloc_str = f.read()
    tweetloc_list = tweetloc_str.split("\nTHIS IS A NEW TWEET\n")

    with open('tweet_retweets.json', "r", encoding="utf8") as f:
        tweetrt_str = f.read()
    tweetrt_list = tweetrt_str.split("\nTHIS IS A NEW TWEET\n")

    with open('tweet_favorites.json', "r", encoding="utf8") as f:
        tweetfav_str = f.read()

    tweetfav_list = tweetfav_str.split("\nTHIS IS A NEW TWEET\n")

    # Get user input for method
    while True:
        try:
            chosen_method = input("Choose TextBlob(1) or your personal Naive Bayes Classifier (2):")
            # Choose method
            if chosen_method == '1':
                # Create instance of class
                tb_class = TextBlob_Classifier()
                # Return user input for chosen analyzer and its instance
                chosen_analyzer, analyzer, analyzer_str = tb_class.get_input()
                sentiment_list = tb_class.analyze_sentiment(tweet_list, chosen_analyzer, analyzer)

                stripped_dict = {}
                count = 0
                # Forms dict with text as keys and sentiment as values
                while count <= (len(tweet_list) - 1):
                    stripped_dict[tweet_list[count]] = sentiment_list[count]
                    count += 1
                # Converting into list of tuple
                ts_tuple_list = [(t, s) for t, s in stripped_dict.items()]

                tsdlist_list = []
                # itertools.zip_longest forms seq of tuples w/ length of the longer list,
                # each containing element from each list. Takes third argument of fill value,
                # used after shorter list is iterated through
                for tuple in list(itertools.zip_longest(ts_tuple_list, tweetdate_list)):
                    try:
                        # Convert ts tuple to list
                        tsd_list = list(tuple[0])
                        # Append date
                        tsd_list.append(tuple[1])
                        tsdlist_list.append(tsd_list)
                    except TypeError:
                        continue

                for tsd_list, author in zip(tsdlist_list[:], tweetauthor_list[:]):
                    try:
                        tsd_list.append(author)
                    except TypeError:
                        continue
                tsdalist_list = tsdlist_list
                for tsda_list, loc in zip(tsdalist_list[:], tweetloc_list[:]):
                    try:
                        tsda_list.append(loc)
                    except TypeError:
                        continue
                tsdallist_list = tsdalist_list
                for tsdal_list, rt in zip(tsdallist_list[:], tweetrt_list[:]):
                    try:
                        tsdal_list.append(rt)
                    except TypeError:
                        continue
                tsdalrlist_list = tsdallist_list
                for tsdalr_list, fav in zip(tsdalrlist_list[:], tweetfav_list[:]):
                    try:
                        tsdalr_list.append(fav)
                    except TypeError:
                        continue

                tsdalrflist_list = tsdalrlist_list
                # Store chosen analyzer name in common var to use as parameter of plt.pie
                title_method = f'TextBlob {analyzer_str}'

                break
            elif chosen_method == '2':
                sentiment_list = []
                # Create instance of class
                personal = personal_classifier()
                # Get user input on model
                chosen_model, chosen_classifier = personal.train_classifier()
                # Run the Classifier
                # For the text of each tweet, apply extract_features().
                # Then, label each tweet positive or negative and store labels in list
                for tweet in tweet_list:
                    sentiment_list.append(chosen_classifier.classify(personal.extract_test_features(tweet_list,
                                                                                                    chosen_model)))
                stripped_dict = {}
                count = 0
                while count <= (len(tweet_list) - 1):
                    stripped_dict[tweet_list[count]] = sentiment_list[count]
                    count += 1
                # Converting into list of tuple
                ts_tuple_list = [(t, s) for t, s in stripped_dict.items()]

                tsdlist_list = []
                for tuple in list(itertools.zip_longest(ts_tuple_list, tweetdate_list)):
                    try:
                        tsd_list = list(tuple[0])
                        if tuple[1]:
                            tsd_list.append(tuple[1])
                        else:
                            tsd_list.append('None')
                        tsdlist_list.append(tsd_list)
                    except TypeError:
                        continue
                for tsd_list, author in zip(tsdlist_list[:], tweetauthor_list[:]):
                    try:
                        tsd_list.append(author)
                    except TypeError:
                        continue
                tsdalist_list = tsdlist_list

                for tsda_list, loc in zip(tsdalist_list[:], tweetloc_list[:]):
                    try:
                        tsda_list.append(loc)
                    except TypeError:
                        continue
                tsdallist_list = tsdalist_list
                for tsdal_list, rt in zip(tsdallist_list[:], tweetrt_list[:]):
                    try:
                        tsdal_list.append(rt)
                    except TypeError:
                        continue
                tsdalrlist_list = tsdallist_list
                for tsdalr_list, fav in zip(tsdalrlist_list[:], tweetfav_list[:]):
                    try:
                        tsdalr_list.append(fav)
                    except TypeError:
                        continue

                tsdalrflist_list = tsdalrlist_list

                title_method = 'personal Naive Bayes classifier'
                break
            else:
                print("Please enter valid input")
        except Exception as e:
            print(e)
            break

    # Convert the sentiment list to DataFrame and print the DataFrame
    if not sentiment_list:
        print("No tweets with this keyword in the specified time")
    else:
        df = pd.DataFrame(sentiment_list)

    # Visualise using Matplotlib
    fig, ax = plt.subplots()
    # Set equal aspect to ensure round pie
    ax.set(aspect="equal", title=f"Sentiment Analysis of Tweets containing '{search_str}'\n"
                                 f"from {title_origin} in the next {stream_period} minutes\n" 
                                 f"using {title_method}")
    if chosen_method == '1':
        # Exclude wedge and label of sentiment if there are no tweets with the sentiment collected
        if sentiment_list.count('pos') == 0:
            wedge_size = [(sentiment_list.count('neg') / len(sentiment_list)) * 100,
                          (sentiment_list.count('neu') / len(sentiment_list)) * 100]
            label_list = ['neg', 'neu']
        elif sentiment_list.count('neg') == 0:
            wedge_size = [(sentiment_list.count('pos') / len(sentiment_list)) * 100,
                          (sentiment_list.count('neu') / len(sentiment_list)) * 100]
            label_list = ['pos', 'neu']
        elif sentiment_list.count('neu') == 0:
            wedge_size = [(sentiment_list.count('pos') / len(sentiment_list)) * 100,
                          (sentiment_list.count('neg') / len(sentiment_list)) * 100]
            label_list = ['pos', 'neg']
        elif sentiment_list.count('pos') == 0 and sentiment_list.count('neg') == 0:
            wedge_size = [(sentiment_list.count('neu') / len(sentiment_list)) * 100]
            label_list = ['neu']
        elif sentiment_list.count('pos') == 0 and sentiment_list.count('neu') == 0:
            wedge_size = [(sentiment_list.count('neg') / len(sentiment_list)) * 100]
            label_list = ['neg']
        elif sentiment_list.count('neg') == 0 and sentiment_list.count('neu') == 0:
            wedge_size = [(sentiment_list.count('pos') / len(sentiment_list)) * 100]
            label_list = ['pos']
        else:
            label_list = ['pos', 'neg', 'neu']
            wedge_size = [(sentiment_list.count('pos') / len(sentiment_list)) * 100,
                          (sentiment_list.count('neg') / len(sentiment_list)) * 100,
                          (sentiment_list.count('neu') / len(sentiment_list)) * 100]

    elif chosen_method == '2':
        if sentiment_list.count('positive') == 0:
            wedge_size = [(sentiment_list.count('negative') / len(sentiment_list)) * 100,
                          (sentiment_list.count('neutral') / len(sentiment_list)) * 100]
            label_list = ['negative', 'neutral']
        elif sentiment_list.count('negative') == 0:
            wedge_size = [(sentiment_list.count('positive') / len(sentiment_list)) * 100,
                          (sentiment_list.count('neutral') / len(sentiment_list)) * 100]
            label_list = ['positive', 'neutral']
        elif sentiment_list.count('neutral') == 0:
            wedge_size = [(sentiment_list.count('positive') / len(sentiment_list)) * 100,
                          (sentiment_list.count('negative') / len(sentiment_list)) * 100]
            label_list = ['positive', 'negative']
        elif sentiment_list.count('positive') == 0 and sentiment_list.count('negative') == 0:
            wedge_size = [(sentiment_list.count('neutral') / len(sentiment_list)) * 100]
            label_list = ['neutral']
        elif sentiment_list.count('positive') == 0 and sentiment_list.count('neutral') == 0:
            wedge_size = [(sentiment_list.count('negative') / len(sentiment_list)) * 100]
            label_list = ['negative']
        elif sentiment_list.count('negative') == 0 and sentiment_list.count('neutral') == 0:
            wedge_size = [(sentiment_list.count('positive') / len(sentiment_list)) * 100]
            label_list = ['positive']
        else:
            label_list = ['positive', 'negative', 'neutral']
            wedge_size = [(sentiment_list.count('positive') / len(sentiment_list)) * 100,
                          (sentiment_list.count('negative') / len(sentiment_list)) * 100,
                          (sentiment_list.count('neutral') / len(sentiment_list)) * 100]
    # autopct sets the d.p. of the percentage
    plt.pie(x=wedge_size, labels=label_list, autopct='%1.2f%%')
    plt.show()

    # Print instructions for using elasticsearch/kibana to visualise results
    # Only displays after plt.pie figure window is closed
    print(r"To access elasticsearch webpage, keep elasticsearch\bin\elasticsearch.bat running.", "\n"
          "Webpage url: http://localhost:9200/{index}/_search")

    while True:
        response = input("Have you done the above steps?(Y/N):")
        if response == 'Y':
            #try:
            # Create a doc in elasticsearch for each sentiment/tweet to be easily searched
            count = 0
            for list in tsdalrflist_list:
                try:
                    # No text,date,author, loc, retweet, fav from personal classifier
                    es.index(index="tweets-zon", id=count,
                             body={"author": list[3],
                                   # strptime to convert datestring to datetime object, format specified is compulsory
                                   "date": datetime.strptime(list[2],
                                                             '%a %b %d %H:%M:%S %z %Y'),
                                   "message": list[0],
                                   "sentiment": list[1],
                                   # Str, not coordinates
                                   "location": list[4],
                                   "retweets": list[5],
                                   "likes": list[6]
                                   })
                    count += 1
                # catch ValueError raised when no date of tweet provided
                except ValueError:
                    es.index(index="tweets-zon", id=count,
                             body={"author": list[3],
                                   "message": list[0],
                                   "sentiment": list[1],
                                   # Str, not coordinates
                                   "location": list[4],
                                   "retweets": list[5],
                                   "likes": list[6]
                                   })
                    count += 1
            break
            #except Exception as e:
                #print(e)
                #continue
        else:
            print("Please enter appropriate response when you've completed the steps above")
            continue
    print("Visualise using Kibana:\nOpen config/kibana.yml in text editor.\n"
          "Set elasticsearch.hosts to elasticsearch page url.\n"
          r"Run bin\kibana.bat. Go to http://localhost:5601"
          '\nGo to Stack Management and create index pattern using the index created\n'
          'Create pie chart under Visualise and create fields by adding buckets.')