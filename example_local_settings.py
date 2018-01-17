'''Local Settings for a heroku_ebooks account. #
Fill in the name of the account you're tweeting from here.
'''

# Configuration
MY_CONSUMER_KEY = ''
MY_CONSUMER_SECRET = ''
MY_ACCESS_TOKEN_KEY = ''
MY_ACCESS_TOKEN_SECRET = ''

# A list of comma-separated, quote-enclosed Twitter handles of account that you'll generate tweets based on. It should look like ["account1", "account2"]. If you want just one account, no comma needed.
SOURCE_ACCOUNTS = []

SEARCH_TERMS = []

# Cap on how many tweets to load in for each search term
SEARCH_TERMS_LIMITS = [400] * len(SEARCH_TERMS)

# List of what orders of the Markov model to use. Higher values yield higher complexity
# and may result in fewer unique sentences
# If multiple a specified, then a model for each provided order is generated and saved.
ORDERS = [3,2]
# Source tweets that match this regexp will not be added to the Markov chain.
#You might want to filter out inappropriate words for example.
SOURCE_EXCLUDE = r''
DEBUG = False  
# Set this to True if you want to test Markov generation from a static file instead of the API
STATIC_TEST = False  
# The name of a text file of a string-ified list for testing.
#To avoid unnecessarily hitting Twitter API. You can use the included testcorpus.txt, if needed.
TEST_SOURCE = ".txt"  

# Files of text to load in. We assume all the text is basically on a single (possibly giant) line.
FILES = []
# How much of each file we should keep
# This a crude way to prevent large text files from dominating the pool
# e.g. 1/4 -> the first 1/4 of the file will be read
FILE_READ_AMT = [1]*len(FILES)

SCRAPE_RSS = False
SRC_RSS = []

# Set this to true to scrape webpages.
SCRAPE_URL = False  
# A comma-separated list of URLs to scrape
SRC_URL = []

# A comma-separated list of the tag or object to search for in each page above.
WEB_CONTEXT = ['http://example.com']
# A list of dictionaries containing the attributes for each page.
WEB_ATTRIBUTES = [{'description'}]
# The name of the account you're tweeting to.
TWEET_ACCOUNT = ''  

# How to combine the various models.
# seq -> form sentences from models sequentially (use on model exclusively for the first half, then another
#        model for the second half)
# hybrid -> use the hybrid model that combines the standalone models
MODEL_MODE = 'seq'
