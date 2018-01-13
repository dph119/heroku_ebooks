# markov_chain_twitter_bot

This is forked from tommeagher's [heroku_ebooks](https://github.com/tommeagher/heroku_ebooks) Python script. I simply took it as a baseline and refactored/played with it to suit my needs. Maybe someone else will find it useful.

Main differences, in no particular order:

1. Replaced use of twitter module with tweepy
   tweepy has this concept of Cursors that abstracts away the need to
   come up with multiple queries when you want more data than the Twitter API
   allows for a single call. Plus, if you hit your 15-minute limit, it will
   simply wait until the window has expired and continue the query.
2. Added support for scraping RSS feeds.
3. Added support for ingesting text files (aside from the test file provided).
4. Replaced the home-grown markov chain code with markovify.
   Given markovify is pretty widely used, I figured I'd leverage it here. Less code to manage, and they also have this nice support for handling multiple markov models and letting you give weights to which one to use when making a sentence, checks to make sure sentences don't overlap too much with the original text, and support for controlling the length of the sentences.
5. Add a sample crontab file to show I'm running this locally. No heroku stuff for me.
   As a sort of side-effect, I regressed back to Python 2.7 and adjusted the syntax accordingly. 

The rest of this README was modifed to reflect the latest changes.

## Setup

1. Clone this repo
2. Create a Twitter account that you will post to.
3. Sign into https://dev.twitter.com/apps with the same login and create an application. Make sure that your application has read and write permissions to make POST requests.
4. Make a copy of the `local_settings_example.py` file and name it `local_settings.py`
5. Take the consumer key (and secret) and access token (and secret) from your Twiter application and paste them into the appropriate spots in `local_settings.py`.
6. In `local_settings.py`, be sure to add the handle of the Twitter user you want your _ebooks account to be based on. To make your tweets go live, change the `DEBUG` variable to `False`.

## Configuring

There are several parameters that control the behavior of the bot. You can adjust them by setting them in your `local_settings.py` file.

As you've no doubt gathered from the file list, there are a few scripts here. The naming/organization could be improved upon.

### markov_chain_generator.py
Responsbile for aggregating all of the data and generating the list of tweets. This also defines functions that others can use for setting up an API connection and sending tweets.

### tweet_generator_top.py
A sort of top-level script that leverages markov_chain_generator.py. When you want to generate content, you run this. The idea behind this is you generate/review the tweets to send out, and then they are pickled. If you don't trust your bot to reliably come up with dank material, you can run the script in 'interactive mode' where you say whether a given tweet meets your high standards and is worthy of actually being sent out. You can choose to tweet it immediately, or save it to be sent later.

### tweeter.py
If you want to delay sending the tweets generated via tweet_generator_top, but have it done automatically you can use this. This checks for whatever tweets you have saved and, upon invocation, will decide whether it's time to send out a tweet. The common use case is to call this in a cronjob every so often, resulting in tweets being sent in a psuedorandom time. Run with -h to see available options, including setting the probability for sending a tweet on a given invocation.

### Additional sources

This bot was originally designed to pull tweets from a Twitter account, however, it can also process comma-separated text in a text file, or scrape content from the web.

#### Static Text
To use a local text file, set `STATIC_TEST = True` and specify the name of a text file containing comma-separated "tweets" as `TEST_SOURCE`.

#### Web Content
To scrape content from the web, set `SCRAPE_URL` to `True`. This bot makes use of the [`find_all()` method](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#find-all) of Python's BeautfulSoup library. The implementation of this method requires the definition of three inputs in `local_settings.py`.

1. A list of URLs to scrape as `SRC_URL`.
2. A list, `WEB_CONTEXT`, of the [names](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#id11) of the elements to extract from the corresponding URL. This can be "div", "h1" for level-one headings, "a" for links, etc. If you wish to search for more than one name for a single page, repeat the URL in the `SRC_URL` list for as many names as you wish to extract.
3. A list, `WEB_ATTRIBUTES` of dictionaries containing [attributes](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#attrs) to filter by. For instance, to limit the search to divs of class "title", one would pass the directory: `{"class": "title"}`. Use an empty dictionary, `{}`, for any page and name for which you don't wish to specify attributes.

__Note:__ Web scraping is experimental and may give you unexpected results. Make sure to test the bot in debugging mode before publishing.

#### RSS Content
To scrape RSS sites, set `SCRAPE_RSS` to true. The bot leverages the feedparser module and is hard-coded to look for headlines/descriptions (e.g. from news sites), though with a small amount of work could be made paramaterizable.

## Debugging

If you want to test the script or to debug the tweet generation, you can skip the random number generation and not publish the resulting tweets to Twitter.

First, adjust the `DEBUG` variable in `local_settings.py`.

```
DEBUG = True
```

## Credit
The baseline of this code should got to tommeagher's [heroku_ebooks](https://github.com/tommeagher/heroku_ebooks), which also credits other users/contributors.
