#!/usr/bin/python
import copy
import random
import re
import tweepy
import feedparser
import markovify
import pickle
from random import shuffle
from unicodedata import normalize
from bs4 import BeautifulSoup

import urllib2
from htmlentitydefs import name2codepoint as n2c
from urllib2 import urlopen
chr = unichr

from local_settings import *

def strip_duplicate_words(string):
    '''Remove any consecutive duplicate words in provided string'''
    if not string:
        # Nothing to do for empty strings
        return string
    
    new_string = []
    current_index = 0
    for word in re.split('\.|,| ', string):
        if not word:
            continue
        if current_index == 0:
            new_string += [word]
            current_index += 1
        else:
            if word != new_string[current_index - 1]:
                new_string += [word]
                current_index += 1
    return ' '.join(new_string)
        
def connect():
    '''Get a twitter API handle'''
    
    auth = tweepy.OAuthHandler(MY_CONSUMER_KEY,  MY_CONSUMER_SECRET)
    auth.set_access_token(MY_ACCESS_TOKEN_KEY, MY_ACCESS_TOKEN_SECRET)
    return tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


def entity(text):
    if text[:2] == "&#":
        try:
            if text[:3] == "&#x":
                return chr(int(text[3:-1], 16))
            else:
                return chr(int(text[2:-1]))
        except ValueError:
            pass
    else:
        guess = text[1:-1]
        numero = n2c[guess]
        try:
            text = chr(numero)
        except KeyError:
            pass
    return text


def filter_text(text):
    '''Common function for doing various bits of clean-up on text.'''

    # take out RT or MT part (but leave the rest of the tweet intact)
    text = re.sub(r'\b(RT|MT) \@\w+: ', '', text)  
    # Take out URLs, hashtags, hts, etc.    
    text = re.sub(r'((h\/t)|(http))\S+', '', text)  

    # Replace references to other accounts    
    text = re.sub(r'the \.\@\w+', random.choice(REPLACE_WORDS), text)
    text = re.sub(r'the \@\w+', random.choice(REPLACE_WORDS), text)
    text = re.sub(r'\.\@\w+', random.choice(REPLACE_WORDS), text)  
    text = re.sub(r'\@\w+', random.choice(REPLACE_WORDS), text)
    
    # collaspse consecutive whitespace to single spaces.    
    text = re.sub(r'\s+', ' ', text)
    # take out quotes.    
    text = re.sub(r'\"|\(|\)', '', text)
    # remove attribution    
    text = re.sub(r'\s+\(?(via|says)\s@\w+\)?', '', text)
    # Filter out some unicode garbage    
    text = re.sub(ur'\u2026', '', text)
    
    htmlsents = re.findall(r'&\w+;', text)
    for item in htmlsents:
        text = text.replace(item, entity(item))
    text = re.sub(r'\xe9', 'e', text)  # take out accented e

    if type(text) == unicode:
        text = normalize('NFKD', text).encode('ascii','ignore')

    if not re.search('([\.\!\?\"\']$)', text):
        text += "."
        
    text = text.strip()
    return text


def filter_tweet(tweet):
    '''Wrapper function to support receiving a tweet.'''
    return filter_text(tweet.text)


def scrape_page(src_url, web_context, web_attributes):
    '''Take a list of websites, scrape them for specified constructrs/attributes.'''
    
    # Some websites require you to provide some sort of header
    hdr = {'User-Agent': ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 '
                          '(KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'),
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
    
    tweets = []
    last_url = ""
    for i in range(len(src_url)):
        if src_url[i] != last_url:
            last_url = src_url[i]
            print ">>> Scraping {0}".format(src_url[i])
            try:
                req = urllib2.Request(src_url[i], headers=hdr)
                page = urlopen(req)                
            except Exception:
                last_url = "ERROR"
                import traceback
                print ">>> Error scraping {0}:".format(src_url[i])
                print traceback.format_exc()
                continue
            soup = BeautifulSoup(page, 'html.parser')

        hits = soup.find_all(web_context[i], attrs=web_attributes[i])

        if not hits:
            print ">>> No results found!"
            continue
        else:
            errors = 0
            for hit in hits:
                try:
                    tweet = str(hit).strip()                    
                    tweet = tweet.replace('\n', '')
                except (UnicodeEncodeError, UnicodeDecodeError):
                    print hit.text
                    errors += 1
                    continue
                if tweet:
                    tweets.append(tweet)
            if errors > 0:
                print ">>> We had trouble reading {} result{} out of {}.".format(
                    errors, "s" if errors > 1 else "", len(hits))

    return tweets

def scrape_rss(src_rss):
    '''Similar to scrape page, but geared to processing RSS feeds.'''
    
    tweets = []
    last_rss = ""
    for i in range(len(src_rss)):
        if src_rss[i] != last_rss:
            last_rss = src_rss[i]
            print ">>> Scraping {0}".format(src_rss[i])
            try:
                d = feedparser.parse(src_rss[i])
            except Exception:
                last_rss = "ERROR"
                import traceback
                print ">>> Error scraping RSS {0}:".format(src_rss[i])
                print traceback.format_exc()
                continue

        hits = []
        for entry in d.entries:
            # Add the title and any subtitle, if available
            # Be sure to remove any HTML tags, if they exist
            hits += [re.sub('<[^<]+?>', '', entry.title)]
            hits += [re.sub('<[^<]+?>', '', entry.summary[:entry.summary.find('<')])]

        if not hits:
            print ">>> No results found!"
            continue
        else:
            errors = 0
            for hit in hits:
                try:
                    tweet = normalize('NFKD', hit).encode('ascii','ignore')
                    tweet = str(tweet).strip()
                    tweet = tweet.replace('\n', '')
                except (UnicodeEncodeError, UnicodeDecodeError):
                    print hit
                    errors += 1
                    raise
                    continue
                if tweet:
                    tweet = tweet.replace('...', '')
                    tweets.append(tweet)
            if errors > 0:
                print ">>> We had trouble reading {} result{} out of {}.".format(
                    errors, "s" if errors > 1 else "", len(hits))

    return tweets


def grab_tweets(api, user):
    '''Helper function for grabbing all the tweets of a specified user, and filtering out
    ones that contain any 'illegal' terms.'''
    
    tweets = []
    user_tweets = api.user_timeline(screen_name=user, count=200)
    
    if len(user_tweets) == 0:
        print "No tweets found for user:", user
    else:
        for tweet in user_tweets:
            tweet.text = filter_tweet(tweet)
            # Make sure we exclude tweets that contain any terms we don't
            # want included
            if re.search(SOURCE_EXCLUDE, tweet.text):
                continue
            if tweet.text:
                tweets.append(tweet.text)
                
    return tweets

def get_twitter_search_tweets(api, search_terms, search_terms_limits):
    tweets = []
    for index, search_term in enumerate(search_terms):
        search_tweets = tweepy.Cursor(api.search, q=search_term,
                                      count=search_terms_limits[index], lang='en')

        count = 0
        for tweet in search_tweets.items(limit=search_terms_limits[index]):
            count += 1
            tweet.text = filter_tweet(tweet)
            if re.search(SOURCE_EXCLUDE, tweet.text):
                continue
            if tweet.text:
                tweets.append(tweet.text)

        print "{0} tweets found with term '{1}'".format(count, search_term)
        
    return tweets 


def get_twitter_user_tweets(api, users):
    '''Get a bunch of tweets for each of the specified users.'''
    
    tweets = []
    for handle in users:
        tweets_iter = grab_tweets(api, handle)
        tweets += tweets_iter
        print "{0} tweets found in {1}".format(len(tweets_iter), handle)
        if not tweets:
            print "Error fetching tweets from Twitter. Aborting."
            exit()
            
    return tweets


def load_aggregated_data_file(fname):
    '''Load up previously aggregated/saved data.'''
    
    print '<<< Loading from', fname
    # Load up the previously aggregated data
    consolidated_tweets = pickle.load(open(fname, "rb"))
    return consolidated_tweets


def load_test_data(fname):
    '''Load up some pre-created test file of data. Intended for debugging.'''
    
    tweets = []
    print ">>> Generating from {0}".format(fname)
    string_list = open(fna,e).readlines()
    for item in string_list:
        tweets += item.split(",")

    return tweets

def load_files(fnames, read_amounts):
    '''Load up a list of text files, with support for only saving a fraction
    of the whole file. This assumes all text is on a single line.'''
    
    tweets = []
    # Files tend to dominate the pool, so to avoid that,
    # simply cut out part of it
    for index, fname in enumerate(fnames):
        print '>>>Loading file', fname
        text = ' '.join(open(fname).readlines())
        text = text[:int(len(text)*read_amounts[index])]

        new_text = ""
        for word in text.split(' '):
            try:
                word.encode('utf-8')
            except UnicodeDecodeError:
                continue
            new_text += ' ' + word

        tweets += [new_text]
        
    return tweets


def aggregate_data(api, save_aggregated_data, save_fname='aggregated_data.p'):
    '''Using parameters specified in local_settings, aggregate all the data to be used 
    by the Markov model.'''

    source_tweets = []
    
    if STATIC_TEST:
        # Loading test data takes precedence over everything else
        source_tweets += load_test_data(TEST_SOURCE)
        print 'Total source_tweets:', len(source_tweets)        
    else:
        if SCRAPE_URL:
            source_tweets += scrape_page(SRC_URL, WEB_CONTEXT, WEB_ATTRIBUTES)
        
        print 'Total source_tweets:', len(source_tweets)
    
        if SCRAPE_RSS:
            source_tweets += scrape_rss(SRC_RSS)

        print 'Total source_tweets:', len(source_tweets)                        
    
        if SEARCH_TERMS:
            source_tweets += get_twitter_search_tweets(api, SEARCH_TERMS, SEARCH_TERMS_LIMITS)
            
        print 'Total source_tweets:', len(source_tweets)                                    

        if SOURCE_ACCOUNTS and len(SOURCE_ACCOUNTS[0]) > 0:
            source_tweets += get_twitter_user_tweets(api, SOURCE_ACCOUNTS)
        
        print 'Total source_tweets:', len(source_tweets)
    
    # Throw it all into one giant text blob
    aggregated_data = ' '.join(source_tweets)
    
    if save_aggregated_data:
        print '>>> Saving to', save_fname
        pickle.dump(aggregated_data, open(save_fname, "wb"))

    return aggregated_data
    
def generate_tweets(num, api, save_aggregated_data=False, load_aggregated_data=False):
    '''Main function that comes up with all the data to be used by the Markov model 
    and generates that Markov chains to be tweeted.'''
    
    order = ORDER
    tweets = []
    file_text = []
    
    ##########################################################################
    # Aggregate the data and put it into the Markov model
    if len(FILES):
        file_text += load_files(FILES, FILE_READ_AMT)
    
    if load_aggregated_data:
        aggregated_data = load_aggregated_data_file("aggregated_data.p")
    else:
        aggregated_data = aggregate_data(api, save_aggregated_data)
        
    # We assume text files have a huge amount of data.
    # To avoid it dorwning out the other sets of data, put it in a separate model
    # and simply give both models equal weight.
    file_model = markovify.Text(file_text, state_size=order)
    aggregated_data_model = markovify.Text(aggregated_data, state_size=order)

    text_model = markovify.combine([ file_model, aggregated_data_model ], [ 1, 4 ])

    ##########################################################################
    # Now to create the actual sentences
    while len(tweets) < num:
        if len(tweets) % 10 == 0:
            print 'Current count:', len(tweets)

        # Sometimes just go about making a sentence
        if random.randint(0, 1) == 1:        
            tweet = text_model.make_short_sentence(160)
        else:
            # If other tweet is empty, restart the whole process
            # Do this indefinitely -- we assume we can't get stuck in an inifite loop
            while True:
                # Other times, make two smaller sentences to join together
                tweet = text_model.make_short_sentence(80)
                if not tweet:
                    continue
                
                other_tweet = text_model.make_short_sentence(80)

                if not other_tweet:
                    continue
                
                tweet += "." + other_tweet
                break

        # For sufficiently short tweets, add another sentence to it
        if len(tweet) < 60:
            tweet += '.' + text_model.make_short_sentence(160)
            
        if tweet:
            tweet = filter_text(tweet)
            tweet = strip_duplicate_words(tweet)            
        else:
            # We don't want empty tweets
            continue

        # Randomly convert everything to upper case
        if random.randint(0, 10) == 1:
            tweet = tweet.upper()

        tweets += [tweet]
        
    return tweets

def send_tweet(api, tweet):
    '''Send out a tweet -- simple as that.'''
    status = api.update_status(tweet)
    print '>>>Tweet sent:', status.text.encode('utf-8')

if __name__ == "__main__":
    api = connect()        
    tweets = generate_tweets(1000, api)
    print tweets
