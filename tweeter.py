#!/usr/bin/python
###############################################
#
# Upon execution, figure out whether
# we want to send a tweet (random probability).
# If so, look in a file containing a list of
# available tweets to send (presumably already curated).
#
###############################################

import random
import pickle
import argparse
from markov_chain_generator import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='''Utility script for randomly sending a curated tweet.''')
    
    parser.add_argument('-l', type=str, default='accepted_tweets.p',
                        help="Curated list of tweets to look at. Default = %(default)s")
    parser.add_argument('-p', type=int, default=33,
                        help="Probability of sending tweet upon current execution. 1/x probability. Default = %(default)s")
    

    args = parser.parse_args()
    api = connect()

    # Decide if it's time to send
    # Picking a random value since it should be equiprobable
    if random.randint(0, args.p) == 0:
        # Open the pickled file, exctract the text, send it out.
        # Then save the updated list with the now-removed remove
        try:
            tweets = pickle.load( open( args.l, "rb" ) )
        except:
            print 'Filename:', args.l
            raise
        if len(tweets) == 0:
            print 'Warning: No available tweets were found!'
            # TODO: Add support to send an email 
            exit(1)
        else:
            tweet = tweets[0]
            send_tweet(api, tweet)
            pickle.dump(tweets[1:], open( args.l, "wb" ))
    else:
        print '>>>Not doing anything this time...'

    
    
    

