# Experimental code segments for future reuse

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

import re
from nltk.tokenize import word_tokenize
from string import punctuation
from nltk.corpus import stopwords


class PreProcessTweets:
    def __init__(self):
        self._stopwords = set(stopwords.words('english') + list(punctuation) + ['AT_USER', 'URL'])

    def processTweets(self, list_of_tweets):
        processedTweets = []
        for tweet in list_of_tweets:
            processedTweets.append((self._processTweet(tweet["text"]), tweet["label"]))
        return processedTweets

    def _processTweet(self, tweet):
        tweet = tweet.lower()  # convert text to lower-case
        tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet)  # remove URLs
        tweet = re.sub('@[^\s]+', 'AT_USER', tweet)  # remove usernames
        tweet = re.sub(r'#([^\s]+)', r'\1', tweet)  # remove the # in #hashtag
        tweet = word_tokenize(tweet)  # remove repeated characters (helloooooooo into hello)
        return [word for word in tweet if word not in self._stopwords]

def isolate_url():
    from preprocessor.api import parse
    # Isolate URLs for tweets that have it
    parsed_text = parse(tweet_dict["text"])
    link = parsed_text.urls
    if link != None:
        print(parsed_text.urls[0])

# Prints collective sentiment of Naive Bayes Classification
def overall_sentiment(NBResultLabels):
    # get the overall sentiment using the percentage of positive labels
    if (100 * NBResultLabels.count('positive') / len(NBResultLabels)) > 55:
        overall_sentiment = 'positive'
    elif 50 < (100 * NBResultLabels.count('positive') / len(NBResultLabels)) <= 55:
        overall_sentiment = 'slightly positive'
    elif 45 < (100 * NBResultLabels.count('positive') / len(NBResultLabels)) <= 50:
        overall_sentiment = 'slightly negative'
    elif (100 * NBResultLabels.count('positive') / len(NBResultLabels)) <= 45:
        overall_sentiment = 'negative'

    return overall_sentiment


"""
# Get user input on training model
chosen_model = input("Choose training model:\n(1) Tech Companies [Niek Sanders Dataset]\n"
                     "(2) General Tweets [Sentiment 140]\n(3) Airlines\n(4) Art/Museums [SMILE Dataset]")
while True:
    if chosen_model == '1':
        # 'r' prefix to convert to raw string, since \U starts a unicode seq
        corpus_csv = r'C:\Users\Lenovo\PycharmProjects\TwitterDataMiner\Training Models\Tech Dataset.csv'
        training_csv = r'C:\Users\Lenovo\PycharmProjects\TwitterDataMiner\tech_training.csv'
        break
    elif chosen_model == '2':
        corpus_csv = r'C:\Users\Lenovo\PycharmProjects\TwitterDataMiner\Training Models\Sentiment140dataset.csv'
        training_csv = r'C:\Users\Lenovo\PycharmProjects\TwitterDataMiner\general_training.csv'
        break
    elif chosen_model == '3':
        corpus_csv = r'C:\Users\Lenovo\PycharmProjects\TwitterDataMiner\Training Models\Airline_tweet_sentiment.csv'
        training_csv = r'C:\Users\Lenovo\PycharmProjects\TwitterDataMiner\airline_training.csv'
        break
    elif chosen_model == '4':
        corpus_csv = r'C:\Users\Lenovo\PycharmProjects\TwitterDataMiner\Training Models\TweetEmotionsData.csv'
        training_csv = r'C:\Users\Lenovo\PycharmProjects\TwitterDataMiner\emotions_training.csv'
        break
    else:
        print('Please enter valid input')
"""
import nltk
from functions import build_training_set, filter_tweets, personal_classifier
from preprocessor.api import clean

"""
Training Set is built in separate file since it requires significant processing time. Training set should be built
before release to users
"""

# MOVE THIS ELSEWHERE
while True:
    # Get user input on training model
    chosen_model = input("Choose training model:\n(1) Tech Companies [Niek Sanders Dataset]\n"
                         "(2) General Tweets [Sentiment 140]\n(3) Airlines\nModel: ")
    if chosen_model == '1':
        # 'r' prefix to convert to raw string, since \U starts a unicode seq
        corpus_csv = r'C:\Users\Lenovo\PycharmProjects\TwitterDataMiner\Training Models\Tech Dataset.csv'
        training_csv = r'C:\Users\Lenovo\PycharmProjects\TwitterDataMiner\tech_training.csv'
        break
    # Nums from 0-4
    elif chosen_model == '2':
        corpus_csv = r'C:\Users\Lenovo\PycharmProjects\TwitterDataMiner\Training Models\Sentiment140dataset.csv'
        training_csv = r'C:\Users\Lenovo\PycharmProjects\TwitterDataMiner\general_training.csv'
        break
    elif chosen_model == '3':
        corpus_csv = r'C:\Users\Lenovo\PycharmProjects\TwitterDataMiner\Training Models\Airline_tweet_sentiment.csv'
        training_csv = r'C:\Users\Lenovo\PycharmProjects\TwitterDataMiner\airline_training.csv'
        break
    else:
        print('Please enter valid input')

#  Builds tweet dicts containing text, topic, label, and id keys, stores it in csv file 'training.csv' and returns list.
training_list = build_training_set(chosen_model, corpus_csv, training_csv)

# Cleans text of each tweet and returns them to dict
clean_training_list = training_list
for tweet_dict in clean_training_list:
    clean_text = clean(tweet_dict['text'])
    filtered_text = filter_tweets(clean_text)
    tweet_dict['text'] = filtered_text



"""
Classifier is built in separate file since it requires significant processing time. Classifier should be trained
before release to users
"""

"""

# create instance of class
personal = personal_classifier()

word_features = personal.build_vocabulary(clean_training_list)


# Applies extract_features() to preprocessedTrainingData
training_features = nltk.classify.apply_features(personal.extract_features, clean_training_list)


# CAUSING REPETITION
# Train the classifier
nbayes_classifier = nltk.NaiveBayesClassifier.train(training_features)
"""

"""
model_training_dict = {'tech': [tech_dataset, tech_training], 'sentiment140': [sentiment140_dataset, sentiment140_training],
                       'airline': [airline_dataset, airline_training]}

try:
    #  Builds tweet dicts containing label and keys, stores it in csv file and returns list.
    training_lists = list(build_training_set(model_training_dict))
except Exception as e:
    print(e)


# create instance of class
personal = personal_classifier()

# Try-except inside while loop to restart code segments with long processing time to handle random errors during
# connection with API.

try:
    vocab_list = []
    features_list = []
    # Cleans text of each tweet and returns them to dict
    for training_list in training_lists[:]:
        # If you need to modify the sequence you are iterating over while inside the loop, make a copy by slicing
        for tweet_dict in training_list[:]:
            clean_text = clean(tweet_dict['text'])
            filtered_text = filter_tweets(clean_text, stop_words)
            tweet_dict['text'] = filtered_text

        # Build vocabulary using cleaned training lists
        vocab_list.append(personal.build_vocabulary(training_list))

        # Applies extract_features() to preprocessedTrainingData
        features_list.append(nltk.classify.apply_features(personal.extract_features, training_list))
except Exception as e:
    print(e)

try:
    classifier_list = []
    for features in features_list:

        nltk.NaiveBayesClassifier.train causes repetition of buildtechtrainingset.py bc train is recursive.   
        sys.setrecursionlimit(2000) can be used to change default recursion limit of 1000, but this is discouraged.
        Instead, RecursionError from exceeded max recursion depth should be resolved by changing the recursive code to
        an iterative one, or by reducing the code in the recursive segment

        # Train the classifiers
        nbayes_classifier = nltk.NaiveBayesClassifier.train(features)
        classifier_list.append(nbayes_classifier)
except Exception as e:
    print(e)

"""

"""
    # Build Tech Training Set
    # Read excel file into dataframe for iteration of list when index is used in iterated code
    # "engine='python'" to fix encoding issue
    corpus_df = pd.read_excel(corpus, header=None)
    for index, row in corpus_df.iterrows():
        dict = {"tweet_id": row[1], "label": row[0]}
        # Forms list of dicts
        corpus_list.append(dict)

    rate_limit = 180
    sleep_time = 900 / rate_limit

    for tweet_dict in corpus_list:
        count = 0
        while True:
            try:
                # Get status object from twitter API using tweet id
                status = api.get_status(tweet_dict["tweet_id"])
                # The Status object of tweepy itself is not JSON serializable,
                # but it has a _json property which contains JSON serializable response data
                # Convert Status object to JSON str
                json_str = json.dumps(status._json)
                # Convert JSON str to python dict
                temp_tweet_dict = json.loads(json_str)
                # If tweet object has 'retweeted_status' key, it is a retweet.
                # try-except to check whether tweet streamed exceeds 140 chars.
                # hasattr cannot be used for dict or JSON. 'in' is used instead
                # Use keys to index tweet_dict. If not found, KeyError is produced
                # Access full text of tweet
                if "retweeted_status" in temp_tweet_dict:
                    try:
                        tweet_text = temp_tweet_dict["retweeted_status"]["extended_tweet"]["full_text"]
                    except KeyError:
                        tweet_text = temp_tweet_dict["retweeted_status"]["text"]
                else:
                    try:
                        tweet_text = temp_tweet_dict["extended_tweet"]["full_text"]
                    except KeyError:
                        tweet_text = temp_tweet_dict["text"]
                # Store full text under text key of each tweet
                tweet_dict["text"] = tweet_text
                # Form list of tweet dicts with text, label, and id keys
                training_list.append(tweet_dict)
                count += 1
                print(count)
                time.sleep(sleep_time)
                # Break for next tweet
                break

            except tweepy.error.TweepError as e:
                corpus_list.remove(tweet_dict)
                time.sleep(sleep_time)
                print(e)
                break

        # Write text to corpus excel file
        corpus_df = pd.DataFrame(training_list)
        writer = pd.ExcelWriter(corpus, engine='xlsxwriter')
        corpus_df.to_excel(writer, encoding="ISO-8859-1", index=False)
        writer.save()
    """
    # Write tweet dicts from training_list to the empty CSV file
    """
    Python 2:
    Use "wb" when writing output using the csv module on Windows, because the csv module write out line-ends as \r\n
    On Windows, Python will add '\r' every time you write '\n' in 'w' mode, resulting in \r\r\n line-endings

    Python 3:
    Specify encoding = '"ISO-8859-1"' to write files with special chars like unicode. The file must be opened with
    newline='' for both reading/writing. This is a bug with Python 3.
    """
    """
    with open(training_set, 'w', newline='', encoding="ISO-8859-1") as csv_file:
        # Pass the file, not the filename to csv.writer
        line_writer = csv.writer(csv_file, delimiter=',', quotechar="\"")
        for tweet_dict in training_list:
            try:
                line_writer.writerow([tweet_dict["label"], tweet_dict["text"]])

            except Exception as e:
                print(e)
    return training_list
    """