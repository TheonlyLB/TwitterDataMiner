
import sys
from functions import build_tech_training_set, filter_tweets, personal_classifier
from preprocessor.api import clean
from nltk.corpus import stopwords  # Natural Language Toolkit
from string import punctuation

sys.setrecursionlimit(2000)

# Converts array of english stopwords to an ordered sequence of distinct elements
# Shifted from filter_tweets to avoid initialising stop_words every loop
stop_words = set(stopwords.words('english') + list(punctuation) + ['AT_USER', 'URL'])
"""
Training Sets are pre-built/cleaned and classifiers are pre-trained in separate file 
since it requires significant processing time. 
'r' prefix to convert to raw string, since backslash U starts a unicode seq
"""
tech_dataset = r'C:\Users\Lenovo\PycharmProjects\TwitterDataMiner\Training Models\Tech Dataset.xlsx'
tech_training = r'C:\Users\Lenovo\PycharmProjects\TwitterDataMiner\tech_training.xlsx'


# tech_training_list should be a list of (text, label) tuples
# Returns list of tweet dicts containing label and text
tech_training_list = build_tech_training_set(tech_dataset, tech_training)


keys_list = []
values_list = []
for dict in tech_training_list:
    keys_list.extend(dict.keys())
    values_list.extend(dict.values())

stripped_dict = {}
count = 0
while count <= (len(values_list) - 2):
    stripped_dict[values_list[count]] = values_list[count + 1]
    count += 2

# Converting into list of tuple
tech_tuple_list = [(k, v) for k, v in stripped_dict.items()]
# create instance of class
personal = personal_classifier()

# Try-except inside while loop to restart code segments with long processing time to handle random errors during
# connection with API.
# Cleans text of each tweet and returns them to dict
# If you need to modify the sequence you are iterating over while inside the loop, make a copy by slicing
for tweet_dict in tech_training_list[:]:
    clean_text = clean(tweet_dict['text'])
    filtered_text = filter_tweets(clean_text, stop_words)
    tweet_dict['text'] = filtered_text


# Build vocabulary using cleaned training list
tech_words = personal.build_vocabulary(tech_training_list)


