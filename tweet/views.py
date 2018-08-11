from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.http import JsonResponse
from django.conf import settings
import tweepy
import requests
import re

from searchtweets import ResultStream, gen_rule_payload, load_credentials, collect_results
premium_search_args = load_credentials(filename="twitter_keys.yaml",yaml_key="search_tweets_api",env_overwrite=True)
premium_search_full_args = load_credentials(filename="twitter_keys.yaml",yaml_key="search_tweets_full_api",env_overwrite=False)


emoticons_str = r"""
    (?:
        [:=;] # Eyes
        [oO\-]? # Nose (optional)
        [D\)\]\(\]/\\OpP] # Mouth
    )"""
 
regex_str = [
    emoticons_str,
    r'<[^>]+>', # HTML tags
    r'(?:@[\w_]+)', # @-mentions
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)", # hash-tags
    r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&amp;+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+', # URLs
    r'(?:(?:\d+,?)+(?:\.?\d+)?)', # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])", # words with - and '
    r'(?:[\w_]+)', # other words
    r'(?:\S)' # anything else
]

tokens_re = re.compile(r'('+'|'.join(regex_str)+')', re.VERBOSE | re.IGNORECASE)
emoticon_re = re.compile(r'^'+emoticons_str+'$', re.VERBOSE | re.IGNORECASE)
 
def tokenize(s):
    return tokens_re.findall(s)
 
def preprocess(s, lowercase=False):
    tokens = tokenize(s)
    if lowercase:
        tokens = [token if emoticon_re.search(token) else token.lower() for token in tokens]
    return tokens

def index(request, which, coords):
    
    # // BASIC
    print ('consumer_key', settings.TWITTER['consumer_key'])
    auth = tweepy.OAuthHandler(settings.TWITTER['consumer_key'], settings.TWITTER['consumer_secret'])
    auth.set_access_token(settings.TWITTER['access_token'], settings.TWITTER['access_token_secret'])
    api = tweepy.API(auth)
    public_tweets = api.home_timeline
    dct = {'rate_limit': api.rate_limit_status()['resources']['search'], 'tweets': [], 'len': 0}
    coords = coords or '51.2385413,6.7443112,30km'
    call = ''
    strn = which
    lenght = len(strn.split(',')) - 1 
    for i, ref in enumerate(strn.split(',')):
        if (i == lenght):
            call += '#' + ref
        else:
            call += '#' + ref + ' OR '
    print (call)
    for tweet in tweepy.Cursor(api.search, q=call, geocode=coords).items(20):
        # Process a single status
        # print(tweet.geo, tweet.extended_entities)
        # if hasattr(tweet, 'extended_entities') and str(tweet.geo) != 'None':
        if hasattr(tweet, 'extended_entities'):
            dct['len']+= 1
            # print(preprocess(tweet.text))
            dct['preprocess'] = preprocess(tweet.text)
            dct['tweets'].append(tweet._json)
    return JsonResponse(dct)

def thirty_days(request, which, where):
    
    call = ''
    strn = which
    lenght = len(strn.split(',')) - 1 
    for i, ref in enumerate(strn.split(',')):
        if (i == lenght):
            call += '#' + ref
        else:
            call += '#' + ref + ' OR '
    print (call)
    rule = gen_rule_payload(f"({call}) has:images point_radius:[{where}]", results_per_call=100) # testing with a sandbox account
    print(rule)
    tweets = collect_results(rule, max_results=100, result_stream_args=premium_search_args) # change this if you need to
    [print(tweet.all_text + '-' + tweet['created_at'], end='\n\n') for tweet in tweets[0:20]];
    return JsonResponse(tweets, safe=False)

def full_archive(request, which, where, fr, until):
    
    call = ''
    strn = which
    lenght = len(strn.split(',')) - 1 
    for i, ref in enumerate(strn.split(',')):
        if (i == lenght):
            call += '#' + ref
        else:
            call += '#' + ref + ' OR '
    print (call)
    rule = gen_rule_payload(f"({call}) has:images point_radius:[{where}]", results_per_call=100, from_date=f"{fr}", to_date=f"{until}") 
    print(rule)
    tweets = collect_results(rule, max_results=100, result_stream_args=premium_search_full_args)
    [print(tweet.all_text) for tweet in tweets[0:10]];
    return JsonResponse(tweets, safe=False)