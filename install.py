import csv, json, os, time
# Install python-twitter package, not twitter
import twitter
from config import consumer_key, consumer_secret, access_token, access_token_secret
# Do not import api from Main since that was built using tweepy
API_KEY = consumer_key
API_SECRET = consumer_secret

ACCESS_TOKEN = access_token
ACESS_TOKEN_SECRET = access_token_secret

api = twitter.Api(consumer_key=API_KEY,
                  consumer_secret=API_SECRET,
                  access_token_key=ACCESS_TOKEN,
                  access_token_secret=ACESS_TOKEN_SECRET)


def get_user_params():
    user_params = {}

    # get user input params
    user_params['inList'] = input('\nInput file [./corpus.csv]: ')
    user_params['outList'] = input('Results file [./full-corpus.csv]: ')
    user_params['rawDir'] = input('Raw data dir [./rawdata/]: ')

    # apply defaults
    if user_params['inList'] == '':
        user_params['inList'] = './corpus.csv'
    if user_params['outList'] == '':
        user_params['outList'] = './full-corpus.csv'
    if user_params['rawDir'] == '':
        user_params['rawDir'] = './rawdata/'

    return user_params


def dump_user_params(user_params):
    # dump user params for confirmation
    print('Input:    ' + user_params['inList'])
    print('Output:   ' + user_params['outList'])
    print('Raw data: ' + user_params['rawDir'])
    return


class TweetLists:
    def __init__(self):
        # list of tweet ids that still need downloading
        self.rem_list = []
        self.fetched_list = []


def read_total_list(in_filename):

    # read total fetch list csv
    fp = open(in_filename, 'rt' )
    reader = csv.reader(fp, delimiter=',')

    total_list = []
    for row_list in reader:
        total_list.append( row_list )
    return total_list


# Checks whether a tweet has been downloaded, and downloads it if it hasn't
def purge_already_fetched(fetch_list, raw_dir):
    # check each tweet to see if we have it
    tweet_lists = TweetLists()
    for item in fetch_list:
        tweet_file = raw_dir + item[2] + '.json'
        # check if json file exists
        if os.path.exists(tweet_file):
            # Check whether file is empty
            if os.path.getsize(tweet_file) == 0:
                # Delete it and append to rem_list for retry
                os.remove(tweet_file)
                tweet_lists.rem_list.append(item)
                print('Deleted empty file')
            else:
                # Check file can be parsed
                try:
                    parse_tweet_json(tweet_file)
                    tweet_lists.fetched_list.append(item)
                    print('--> already downloaded #' + item[2])
                # Delete it and append to rem_list for retry
                except RuntimeError:
                    os.remove(tweet_file)
                    tweet_lists.rem_list.append(item)
                    print('Deleted broken file')
        else:
            tweet_lists.rem_list.append(item)

    return tweet_lists


def delete_errors(fetch_list, raw_dir):
    # For each tweet
    for item in fetch_list:
        # Form file name
        tweet_file = raw_dir + item[2] + '.json'
        # Check file exists in raw folder
        if os.path.exists(tweet_file):
            # Check whether file is empty
            if os.path.getsize(tweet_file) == 0:
                # Delete it and remove it from fetch_list
                fetch_list.remove(item)
                os.remove(tweet_file)
                print('Deleted empty file')
            else:
                # Check file can be parsed
                try:
                    parse_tweet_json(tweet_file)
                    print('--> already downloaded #' + item[2])
                # Delete it and remove it from fetch_list
                except RuntimeError:
                    fetch_list.remove(item)
                    os.remove(tweet_file)
                    print('Deleted broken file')
        else:
            fetch_list.remove(item)
            print("Deleted unavailable file from fetch_list")
    # Return fetch_list to be new reference to check tweets
    # Not enough items deleted

    return fetch_list


def download_tweets(fetch_list, raw_dir):
    # ensure raw data directory exists
    if not os.path.exists(raw_dir):
        os.mkdir(raw_dir)

    # stay within rate limits
    max_tweets_per_hr = 720
    download_pause_sec = 3600 / max_tweets_per_hr

    # download tweets
    for idx in range(0, len(fetch_list)):

        # current item
        item = fetch_list[idx]

        # print status
        print(f'--> downloading tweet #{item[2]} ({idx + 1} of {len(fetch_list)})')

        # pull data
        with open(raw_dir + item[2] + '.json', 'w') as myFile:
            try:
                data = api.GetStatus(item[2])
                myFile.write(str(data))
            except:
                pass

        # stay in Twitter API rate limits
        print('    pausing %d sec to obey Twitter API rate limits' % download_pause_sec)
        time.sleep(download_pause_sec)

    return


def parse_tweet_json(filename):
    # read tweet
    print('opening: ' + filename)
    fp = open(filename, 'rt')

    # parse json
    try:
        tweet_json = json.load(fp)
    except ValueError:
        raise RuntimeError('error parsing json')

    # look for twitter api error msgs
    if 'error' in tweet_json:
        raise RuntimeError('error in downloaded tweet')

    # extract creation date and tweet text
    return [tweet_json['created_at'], tweet_json['text']]


def build_output_corpus(out_filename, raw_dir, fetched_list, total_list):
    # open csv output file
    fp = open(out_filename, 'wt')
    writer = csv.writer(fp, delimiter=',', quotechar='"', escapechar='\\',
                        quoting=csv.QUOTE_ALL)

    # write header row
    writer.writerow(['Topic', 'Sentiment', 'TweetId', 'TweetDate', 'TweetText'])

    # parse all downloaded tweets
    bad_count = 0
    for item in fetched_list:
        try:
            # parse tweet
            parsed_tweet = parse_tweet_json(raw_dir + item[2] + '.json')
            full_row = item + parsed_tweet

            # character encoding for output
            for i in range(0, len(full_row)):
                full_row[i] = full_row[i].encode("utf-8")

            # write csv row
            writer.writerow(full_row)

        except RuntimeError:
            print('--> bad data in tweet #' + item[2])
            bad_count += 1

    # indicate success
    if bad_count == 0:
        print('\nSuccessfully downloaded corpus!')
        missing_count = len(total_list) - len(fetched_list)
        if missing_count != 0:
            print('\n%d of %d tweets in corpus not available' % (missing_count, len(total_list)))
        print('Output in: ' + out_filename + '\n')
    else:
        print('\nBad data in %d of %d downloaded tweets!' % (bad_count, len(fetched_list)))
        print('Partial output in: ' + out_filename + '\n')

    return


def main():
    # get user parameters
    user_params = get_user_params()
    dump_user_params(user_params)


    # get fetch list
    total_list = read_total_list(user_params['inList'])
    tweet_lists = purge_already_fetched(total_list, user_params['rawDir'])
    fetch_list = tweet_lists.rem_list
    # start fetching data from twitter
    # download_tweets(fetch_list, user_params['rawDir'])

    # Delete any failed downloads
    print(f"\nDeleting any failed downloads from {user_params['rawDir']}")
    delete_errors(fetch_list, user_params['rawDir'])
    # build output corpus
    build_output_corpus(user_params['outList'], user_params['rawDir'], tweet_lists.fetched_list, total_list)

    return


if __name__ == '__main__':
    main()
