# Invoke the API object's methods to call the Twitter API
import tweepy, nltk
import pandas as pd
from config import consumer_key, consumer_secret, access_token, access_token_secret

# Authenticate your app to Twitter
# Creating the authentication object
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# Setting your access token and secret
auth.set_access_token(access_token, access_token_secret)

# Creating the API object while passing in auth information
# Additional arguments ensures you are notified if app exceeds rate limit (180 tweets/15min)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, timeout=300)
"""
Finish preprocessing of tweets after tweet-preprocessor. Stop words are words which are useless in natural language
processing, such as 'the'.
"""


def filter_tweets(tweet, stop_words):
    """
    In re, the pattern is the regular expression to be matched. The string is searched to match the pattern
    at the beginning of string. Flags are modifiers specified using bitwise OR (|).
    Returns string
    """

    from nltk.tokenize import word_tokenize
    import re
    from string import punctuation
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
    tweet = tweet.lower()  # convert text to lower-case
    # replace the colon symbol left after tweepy preprocessing
    tweet = re.sub(r':', '', tweet)
    tweet = re.sub(r'‚Ä¶', '', tweet)
    # replace consecutive non-ASCII characters with a space
    tweet = re.sub(r'[^\x00-\x7F]+', ' ', tweet)
    # remove emojis from tweet
    tweet = emoji_pattern.sub(r'', tweet)

    # Splits strings into tokens/words based on whitespace and punctuation, returns a list
    # removes repeated characters (helloooooooo into hello)
    word_tokens = word_tokenize(tweet)
    # Create empty list
    filtered_tweet = []
    # Loop through tokens in tweet
    for w in word_tokens:
        # check tokens against stop words and punctuations
        if w not in stop_words and w not in punctuation:
            # append filtered text to list
            filtered_tweet.append(w)
    # convert list to string
    return ' '.join(filtered_tweet)


# Class to allow for multiple return values

class TextBlob_Classifier:
    # Convert method to static method so it does not require 'self argument', only applicable for methods that do
    # not use self in code.
    @staticmethod
    def get_input():
        from textblob.sentiments import NaiveBayesAnalyzer, PatternAnalyzer
        # Get user input for analyzer
        while True:
            chosen_analyzer = input("Please enter 1 for NaiveBayes Analyzer or 2 for Pattern Analyzer:")
            # Choose and train Analyzer
            if chosen_analyzer == '1':
                analyzer = NaiveBayesAnalyzer()
                # Store option in common var for parameter of plt.pie
                analyzer_str = 'NaiveBayesAnalyzer()'
                break
            elif chosen_analyzer == '2':
                analyzer = PatternAnalyzer()
                analyzer_str = 'PatternAnalyzer()'
                break
            else:
                print("Please enter valid input")

        return chosen_analyzer, analyzer, analyzer_str

    @staticmethod
    def analyze_sentiment(tweet_list, chosen_analyzer, analyzer):
        from textblob import Blobber

        # Create blank list to contain tweet text
        sentiment_list = []
        sentiment_analyzer = Blobber(analyzer=analyzer)
        # For each tweet, analyse the sentiment and append the result to a list
        for tweet in tweet_list:
            Sentiment = sentiment_analyzer(tweet)
            # If NaiveBayes, sentiment is available as a str (pos/neg)
            if chosen_analyzer == '1':
                sentiment_list.append(Sentiment.sentiment.classification)
            else:
                # If Pattern, sentiment attr in turn has attr polarity[-1.0, 1.0] and subjectivity[0.0, 1.0]
                # Determine if sentiment is positive, negative, or neutral
                if Sentiment.sentiment.polarity < 0:
                    sentiment = "neg"
                elif Sentiment.sentiment.polarity == 0:
                    sentiment = "neu"
                else:
                    sentiment = "pos"
                sentiment_list.append(sentiment)

        return sentiment_list


# Builds Training Set of tweets about tech companies (Apple, Google, Microsoft)
def build_tech_training_set(corpus, training_set):
    training_list = []
    # Build Tech Training Set
    corpus_df = pd.read_excel(corpus, header=None, encoding="ISO-8859-1")
    for index, row in corpus_df.iterrows():
        dict = {"text": row[2], "label": row[0]}
        # Forms list of dicts
        training_list.append(dict)

    # Write text to corpus excel file
    training_df = pd.DataFrame(training_list)
    writer = pd.ExcelWriter(training_set, engine='xlsxwriter')
    training_df.to_excel(writer, encoding="ISO-8859-1", index=False)
    writer.save()
    return training_list


def build_sentiment140_training_set(corpus, training_set):
    training_list = []
    # Build Sentiment 140 Training Set
    # Convert number labels in Sentiment140 to positive/neutral/negative
    # You should not write to the file you are reading from
    corpus_df = pd.read_excel(corpus, header=None, encoding="ISO-8859-1")
    for index, row in corpus_df.iterrows():
        dict = {"text": row[2], "label": row[0]}
        if dict['label'] == '3' or dict['label'] == '4':
            dict['label'] = 'positive'
        elif dict['label'] == '2':
            dict['label'] = 'neutral'
        else:
            dict['label'] = 'negative'
        # Forms list of dicts
        training_list.append(dict)

    # Write text to training excel file
    training_df = pd.DataFrame(training_list[0:1048576])
    writer = pd.ExcelWriter(training_set, engine='xlsxwriter')
    training_df.to_excel(writer, encoding="ISO-8859-1", index=False)

    writer.save()
    return training_list


def build_airline_training_set(corpus, training_set):
    training_list = []
    # Build Airline Training Set
    corpus_df = pd.read_excel(corpus, header=None, encoding="ISO-8859-1")
    for index, row in corpus_df.iterrows():
        dict = {"text": row[2], "label": row[0]}
        # Forms list of dicts
        training_list.append(dict)

    # Write text to corpus excel file
    training_df = pd.DataFrame(training_list)
    writer = pd.ExcelWriter(training_set, engine='xlsxwriter')
    training_df.to_excel(writer, encoding="ISO-8859-1", index=False)
    writer.save()
    return training_list


class personal_classifier:
    @staticmethod
    def train_classifier():
        # Postpone imports until you need it to prevent circular import error
        from buildtechtrainingset import tech_tuple_list
        from buildSentiment140trainingset import sentiment140_tuple_list
        from buildairlinetrainingset import airline_tuple_list
        personal = personal_classifier()
        while True:
            try:
                # Get user input on training model
                chosen_model = input("Choose training model:\n(1) Tech Companies [Niek Sanders Dataset]\n"
                                     "(2) General Tweets [Sentiment 140]\n(3) Airlines\nModel: ")

                if chosen_model == '1':
                    # Applies extract_features() to preprocessedTrainingData
                    chosen_features = nltk.classify.apply_features(personal.extract_tech_features, tech_tuple_list,
                                                                   labeled=True)
                    break
                elif chosen_model == '2':
                    chosen_features = nltk.classify.apply_features(personal.extract_sentiment140_features,
                                                                   sentiment140_tuple_list, labeled=True)
                    break
                elif chosen_model == '3':
                    # returns LazyMap object(list of (text, label) tuples) if labeled = True
                    chosen_features = nltk.classify.apply_features(personal.extract_airline_features, airline_tuple_list,
                                                                   labeled=True)
                    break
                else:
                    print('Please enter valid input')
            except Exception as e:
                print(e)
                break
        # Train the classifiers
        # Only accepts list of tuples (text, label)
        chosen_classifier = nltk.NaiveBayesClassifier.train(chosen_features)
        return chosen_model, chosen_classifier

    # Build NLP Vocab
    @staticmethod
    def build_vocabulary(preprocessed_training_data):
        from nltk import word_tokenize
        all_words = []

        # Create list of all words in Training Set
        for dict in preprocessed_training_data:
            all_words.extend(word_tokenize(dict['text'].lower()))

        # Create dict of distinct words, with its frequency in Training Set as values
        word_dict = nltk.FreqDist(all_words)

        # Store each distinct word as a list
        word_features = word_dict.keys()
        return word_features

    @staticmethod
    def extract_tech_features(preprocessed_training_data):
        from buildtechtrainingset import tech_words
        features_dict = {}
        # preprocessed_training_data is text of each tweet
        # Converts tweet to an ordered sequence of distinct elements
        tweet_words = set(preprocessed_training_data.split())

        # Check if word in features is in the tweet
        # Creates dictionary where keys are all words in features
        # and values are True/False for their presence in each tweet
        for word in tech_words:
            features_dict[word] = (word in tweet_words)

        return features_dict

    @staticmethod
    def extract_sentiment140_features(preprocessed_training_data):
        from buildSentiment140trainingset import sentiment140_words
        features_dict = {}
        # Converts tweet to an ordered sequence of distinct elements
        tweet_words = set(preprocessed_training_data.split())

        # Check if word in features is in the tweet
        # Creates dictionary where keys are all words in features
        # and values are True/False for their presence in each tweet
        for word in sentiment140_words:
            features_dict[word] = (word in tweet_words)

        return features_dict

    @staticmethod
    def extract_airline_features(preprocessed_training_data):
        from buildairlinetrainingset import airline_words
        features_dict = {}

        # Converts tweet to an ordered sequence of distinct elements
        tweet_words = set(preprocessed_training_data.split())

        # Check if word in features is in the tweet
        # Creates dictionary where keys are all words in features
        # and values are True/False for their presence in each tweet
        for word in airline_words:
            features_dict[word] = (word in tweet_words)

        return features_dict

    @staticmethod
    def extract_test_features(tweet_list, chosen_model):
        from buildtechtrainingset import tech_words
        from buildSentiment140trainingset import sentiment140_words
        from buildairlinetrainingset import airline_words
        if chosen_model == '1':
            chosen_words = tech_words
        elif chosen_model == '2':
            chosen_words = sentiment140_words
        elif chosen_model == '3':
            chosen_words = airline_words
        test_features = {}
        for tweet in tweet_list:
            # Converts tweet to an ordered sequence of distinct elements
            tweet_words = set(tweet.split())

            # Check if word in features is in the tweet
            # Creates dictionary where keys are all words in features
            # and values are True/False for their presence in each tweet
            for word in chosen_words:
                test_features[word] = (word in tweet_words)

        return test_features

