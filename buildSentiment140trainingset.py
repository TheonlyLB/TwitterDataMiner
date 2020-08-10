
import sys
from functions import build_sentiment140_training_set, filter_tweets, personal_classifier
from preprocessor.api import clean
from nltk.corpus import stopwords  # Natural Language Toolkit
from string import punctuation

sys.setrecursionlimit(2000)

# Converts array of english stopwords to an ordered sequence of distinct elements
# Shifted from filter_tweets to avoid initialising stop_words every loop
stop_words = set(stopwords.words('english') + list(punctuation) + ['AT_USER', 'URL'])

sentiment140_dataset = r'C:\Users\Lenovo\PycharmProjects\TwitterDataMiner\Training Models\Sentiment140dataset.xlsx'
sentiment140_training = r'C:\Users\Lenovo\PycharmProjects\TwitterDataMiner\general_training.xlsx'

#  Builds tweet dicts containing label and keys, stores it in csv file and returns list.
sentiment140_training_list = build_sentiment140_training_set(sentiment140_dataset, sentiment140_training)
keys_list = []
values_list = []
for dict in sentiment140_training_list:
    keys_list.extend(dict.keys())
    values_list.extend(dict.values())

stripped_dict = {}
count = 0
while count <= (len(values_list) - 2):
    stripped_dict[values_list[count]] = values_list[count + 1]
    count += 2
# Converting into list of tuple
sentiment140_tuple_list = [(k, v) for k, v in stripped_dict.items()]

# create instance of class
personal = personal_classifier()

for tweet_dict in sentiment140_training_list[:]:
    clean_text = clean(tweet_dict['text'])
    filtered_text = filter_tweets(clean_text, stop_words)
    tweet_dict['text'] = filtered_text

# Build vocabulary using cleaned training lists
sentiment140_words = personal.build_vocabulary(sentiment140_training_list)




