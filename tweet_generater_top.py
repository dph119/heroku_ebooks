#!/usr/bin/python
##########################################################
#
# Top-level utility for creating/loading tweets,
# reviewing them, and deciding whether to actually
# send them out.
# Support to keep the current generated list saved offline
# to quickly pick up where you left off (vs generating
# a new list every time)
#
##########################################################

import sys
import pickle
import argparse
import logging
from markov_chain_generator import *

LOGGER = get_logger(os.path.basename(__file__))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='''Utility script for generating/pushing tweets.''')

    parser.add_argument('-g', action='store_true',
                        help="Generate a new batch of tweets. -l switch takes precedence.")
    parser.add_argument('-s', action='store_true',
                        help="Pickle the list of possible tweets to approve. Saved to tweets.p")
    parser.add_argument('-l', action='store_true',
                        help="Load a list of possible tweets from tweets.p to approve. Takes precedence over -g switch.")
    parser.add_argument('-sa', action='store_true',
                        help="Pickle the aggregated text data for re-use.")
    parser.add_argument('-la', action='store_true',
                        help="Load previously saved aggregated text data.")
    parser.add_argument('-n', type=int, default=50,
                        help=("Number of candidate tweets to generate. Used with -g. "
                              "Default = %(default)s."))
    parser.add_argument('-i', action='store_true',
                        help=("Interactively go through to approve each generated tweet. "
                              "By default they are all approved."))

    args = parser.parse_args()
    api = connect()
    
    if args.l:
        tweets = pickle.load( open( "tweets.p", "rb" ) )
    elif args.g:
        tweets = generate_tweets(args.n, api, args.sa, args.la)
    else:
        LOGGER.error('Not loading any tweets to process?')
        
    # Start processing the tweets
    quit_processing = False
    queued_tweets = []
    if args.i:
        for index, tweet in enumerate(tweets):        
            LOGGER.info('\n%s' % tweet)
            valid_input = False
            while not valid_input:
                valid_input = True
                val = str(raw_input('y/n/q/d: '))
            
                if val == 'y':
                    send_tweet(api, tweet)
                    LOGGER.info('SENT!')
                elif val == 'n':
                    pass
                elif val == 'q':
                    # Do nothing, just quit
                    quit_processing = True
                elif val == 'd':
                    # Add to the list of tweets to queue up (i.e. save to accepted_tweets.p)
                    queued_tweets += [tweet]
                else:
                    valid_input = False
                    LOGGER.warning('Invalid input. Try again.')

            if quit_processing:
                break                
    else:
        queued_tweets = tweets
        
    if args.s:
        LOGGER.info('Saving to tweets.p')
        pickle.dump(tweets[index:], open( "tweets.p", "wb" ))

    if len(queued_tweets):
        LOGGER.info('Saving to accepted_tweets.p')
        # Append to existing list of queued tweets (or make a new one if it doesn't exist)
        try:
            saved_tweets = pickle.load( open( 'accepted_tweets.p', "rb" ) )
        except:
            LOGGER.info("Couldn't open accepted_tweets.p. Starting a new file.")
            pickle.dump(queued_tweets, open( 'accepted_tweets.p', "wb" ))
        else:
            # If we got to this point, then we have a list to append to
            saved_tweets = saved_tweets + queued_tweets
            pickle.dump(saved_tweets, open( 'accepted_tweets.p', "wb" ))
        
            


    
    
    
