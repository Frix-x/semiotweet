#coding:utf8
from __future__ import print_function, division
from future import standard_library
standard_library.install_aliases()
from builtins import str
import oauth2
from io import BytesIO
import json
import os, sys


from django.utils import timezone
from .models import Tweet,User
import random
import string
import time
import pytz
from datetime import datetime

from .semanticAnalysis import toJsonForGraph

#==============================#
#========== REQUESTS ==========#
#==============================#

def oauthRequest(url,credentials,http_method="GET",post_body="",http_headers=None):
    """Send a request to the Twitter API ; returns the result"""
    consumer = oauth2.Consumer(key=credentials[0], secret=credentials[1])
    token = oauth2.Token(key=credentials[2], secret=credentials[3]) #Token of the app
    client = oauth2.Client(consumer, token) #Token of the user using the app
    resp, content = client.request( url, method=http_method, body=post_body.encode('utf-8'), headers=http_headers )
    return content

#==============================#
#=========== TWEETS ===========#
#==============================#

def returnTweetsBatch(screen_name,count=False,max_id=False,since_id=False):
    """Return nbTweet<200 tweets from user 'screen_name' with id in [max_id,since_id]"""
    """The parameters count, max_id and since_id can be specified"""
    global credentials
    global baseURL
    url = baseURL+'statuses/user_timeline.json?screen_name='+screen_name

    # Building the URL :
    if count:
        url +='&count='+str(count)
    if max_id :
        url += "&max_id="+str(max_id)
    if since_id :
        url += "&since_id="+str(since_id)

    # Request
    res = oauthRequest(url,credentials)
    res = json.loads(res.decode('utf-8'))

    # If there's an error or no response :
    if 'errors' in res or len(res) == 0:
        return []

    # Cleaning the tweets
    for tweet in res:
        tweet = cleanTweet(tweet)
    return res

def returnTweetsMultiple(screen_name,lastId=0):
    """Return tweets for user 'screen_name'.
    If lastId = 0 : return all the tweets from the user ;
    Else :          only returns the latest
    Uses returnTweetsBatch() since the Twitter API limits response to 200 Tweets"""

    # Preventing from getting tweets from other users :
    if not screen_name in screen_nameToExtract:
        return []

    tweets = [] # List of the nbTweet tweets
    currentId = returnTweetsBatch(screen_name,1)[0]["id"]# id of the user's last tweet
    nbTweet = 3000 # NOTE : important setting
    batchSize = min(nbTweet,200) # batchSize between 1 and 200

    if lastId == 0: # We only want to get ALL the tweets ; it supposes there are no tweets in the DB
        maxIter = nbTweet // (batchSize+1) + 1 # number of requests to send
        iterNum = 0 # counter for the loop
        lastId = 0
        while lastId != currentId and iterNum < maxIter:
            tweets += returnTweetsBatch(screen_name,batchSize,currentId,False)
            # Updating the ids
            lastId = currentId
            currentId = tweets[-1]["id"]-1

            iterNum = iterNum+1
    else: # We only want to get the latest here ; it supposes there already exist some tweets in the DB
        catch = returnTweetsBatch(screen_name,batchSize,currentId,lastId)
        while catch :
            tweets += catch
            # Updating the id
            currentId = tweets[-1]["id"]-1
            catch = returnTweetsBatch(screen_name,batchSize,currentId,lastId)


    return tweets

def cleanTweet(tweet):
    """Clean a Tweet : delete the some fields and modify others in order
    to store info in the database"""
    global uselessFields
    global stringFields

    fieldsToDelete = [k for k in tweet.keys() if k not in usefullFields]
    for key in fieldsToDelete:
        del tweet[key]

    # Catching the foreign key : user_id
    tweet["user_id"] = tweet["user"]["id"]
    del tweet["user"]

    # Getting the source ; x.find(y) returns -1 if string y not in string x
    for s in tweetSources:
        if tweet["source"].lower().find(s.lower()) != -1:
            tweet["source"] = s
            break
    else:
        tweet["source"] = "Other"

    return tweet


def saveTweet(tweet,user):
    """Saves one tweet from user in database"""
    newTweet = Tweet()
    newTweet.id = tweet['id']
    newTweet.user_id = user
    newTweet.text = tweet['text']
    newTweet.created_at = tweet['created_at']
    newTweet.is_quote_status = tweet['is_quote_status']
    newTweet.in_reply_to_status_id = tweet['in_reply_to_status_id']
    newTweet.favorite_count = tweet['favorite_count']
    newTweet.retweet_count = tweet['retweet_count']
    newTweet.source = tweet['source']
    newTweet.in_reply_to_user_id = tweet['in_reply_to_user_id']
    newTweet.lang = tweet['lang']
    newTweet.tokenArray = tweet['tokenArray']
    newTweet.lemmaArray = tweet['lemmaArray']

    # Formating the date
    current_tz = timezone.get_current_timezone()
    newTweet.created_at = datetime.strptime(newTweet.created_at, '%a %b %d %H:%M:%S +0000 %Y')
    newTweet.created_at= current_tz.localize(newTweet.created_at)
    # newTweet.created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(newTweet.created_at,'%a %b %d %H:%M:%S +0000 %Y'))


    # Saving the tweet
    try:
        newTweet.save()
        return True
    except BaseException as error:
        print("saveTweet() ; error : ", error)
        return False

#==============================#
#=========== USERS  ===========#
#==============================#

def returnUser(screen_name,toClean=True):
    """Return the profile of the user whose the name 'user' was given
    toClean true is used in order to keep the main infos, that is the ones
    to be stored in the database"""
    global baseURL
    global credentials
    # Preventing from getting other users :
    if not screen_name in screen_nameToExtract:
        return {}

    # Request
    res = oauthRequest(baseURL+'users/show.json?screen_name='+screen_name,credentials)
    user = json.loads(res.decode('utf-8'))

    if toClean:
        user = cleanUser(user)
    return user

def cleanUser(user):
    """Clean a Tweet : delete the useless features to store infos in the database"""
    global usefullFieldsUser
    global stringFields

    fieldsToDelete = [k for k in user.keys() if k not in usefullFieldsUser]
    for key in fieldsToDelete:
        del user[key]

    return user

def saveUser(userInfo):
    """Saves one user in database"""
    newUser = User()

    newUser.id = userInfo['id']
    newUser.name = userInfo['name']
    newUser.screen_name = userInfo['screen_name']
    newUser.created_at = userInfo['created_at']
    newUser.contributors_enabled = userInfo['contributors_enabled']
    newUser.verified = userInfo['verified']

    # Formating the date
    current_tz = timezone.get_current_timezone()
    newUser.created_at = datetime.strptime(newUser.created_at, '%a %b %d %H:%M:%S +0000 %Y')
    newUser.created_at= current_tz.localize(newUser.created_at)
    # newUser.created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(newUser.created_at,'%a %b %d %H:%M:%S +0000 %Y'))

    # Saving the user in the database
    try:
        newUser.save()
        return True
    except BaseException as error:
        print("saveUser() ; error : ", error)
        return False

#==============================#
#==== SETTINGS & VARIABLES ====#
#==============================#

# Settings :
def getEnvValue(varName):
    """Return the value of an environment variable or an error if it isn't set"""
    if varName in os.environ:
        return os.environ.get(varName)
    else:
        sys.exit(varName + " is not defined in the environment variables")

### Credentials
consumerKey=getEnvValue('CONSUMER_KEY')
consumerSecret=getEnvValue('CONSUMER_SECRET')
key = getEnvValue('KEY')
secret = getEnvValue('SECRET')
credentials = [consumerKey,consumerSecret,key,secret]

baseURL = "https://api.twitter.com/1.1/"

### Tweets' Fields (see : https://dev.twitter.com/overview/api/tweets):

usefullFields = ["user","text","is_quote_status","in_reply_to_status_id","id",
                "favorite_count","user_id","source","in_reply_to_user_id","retweet_count",
                "lang","created_at"]

# Used to encode string
stringFields = ["created_at","filter_level,id_str","in_reply_to_screen_name",
                "in_reply_to_status_id_str","in_reply_to_user_id_str","lang",
                "quoted_status_id_str","source","withheld_scope"]

# Source sorted by popularity ; used in cleanTweet()
tweetSources =["Twitter Web Client",
               "Twitter for iPhone",
               "Twitter for Android",
               "HootSuite",
               "Media Studio",
               "Twitterfeed",
               "TweetDeck",
               "Twitter for iPad",
               "Twitter for Websites",
               "Twitter Business Experience",
               "SnappyTV",
               "Echofon",
               "Twitter Ads",
               "Google",
               "Medium",
               "Mobile Web",
               "Twitter for  Android",
               "Periscope",
               "Tweet bot for Mac",
               "Mobil Web",
               "Thunderclap",
               "Twitter for Mac",
               "Storify",
               "Tweetbot for iOS",
               "Instagram"]

### Users' Fields (see : https://dev.twitter.com/overview/api/users):

usefullFieldsUser = ["id","name","screen_name","created_at",
                     "contributors_enabled","verified"]

screen_nameToExtract = ["EmmanuelMacron",
                        "MLP_officiel",
                        "FrancoisFillon",
                        "benoithamon",
                        "JLMelenchon",
                        "PhilippePoutou",
                        "dupontaignan",
                        "n_arthaud",
                        "UPR_Asselineau",
                        "JCheminade",
                        "jeanlassalle",
                        ]

#==============================#
#=========== TESTS ============#
#==============================#

def testBatch(screen_name,count=False,max_id=False,since_id=False):
    res = returnTweetsBatch(screen_name,count,max_id,since_id)
    for t in res:
        print(t["id"], t["text"])

    print(len(res))

def testMultiple(screen_name,since_id=False):
    res = returnTweetsMultiple(screen_name,since_id)
    for t in res:
        print(t["id"], t["text"])

    print(len(res))


def testProfile(screen_name,toClean=True):
    user = returnUser(screen_name,credentials,toClean)

    remainingFields = user.keys()
    for i in remainingFields:
        print(i,":", user[i])

if __name__ == '__main__':
    #testBatch("EmmanuelMacron",count=4,max_id=833962028842770432,since_id=832997764984401920)
    #testMultiple("JLMelenchon",since_id=834891272267653122)
    #testBatch("JLMelenchon",since_id=834891272267653122)
    #testTweet("jjerphan")
    #testProfile("jjerphan",False)
    pass
