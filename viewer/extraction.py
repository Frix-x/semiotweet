#coding:utf8
import oauth2
from StringIO import StringIO
import json
import os, sys, getenv


def oauthRequest(url,credentials,http_method="GET",post_body="",http_headers=None):
    """Prepare a request """
    consumer = oauth2.Consumer(key=credentials[0], secret=credentials[1])
    token = oauth2.Token(key=credentials[2], secret=credentials[3]) #Token of the app
    client = oauth2.Client(consumer, token) #Token of the user using the app
    resp, content = client.request( url, method=http_method, body=post_body, headers=http_headers )
    return content

def returnProfile(screen_name,credentials,toClean=True):
    """Return the profile of the user whose the name 'user' was given
    toClean true is used in order to keep the main infos, that is the ones
    to be stored in the database"""
    global baseURL
    res = oauthRequest(baseURL+'users/show.json?screen_name='+screen_name,credentials)
    user = json.load(StringIO(res))
    if toClean:
        user = cleanUser(user)
    return user

def returnTweets(screen_name,credentials,nbTweet,max_id=False):
    """Return the last nbTweet<200 tweets form user 'screen_name'"""
    """max_id can be specified"""
    global baseURL
    url = baseURL+'statuses/user_timeline.json?screen_name='+screen_name+'&count='+str(nbTweet)
    if max_id :
        url+="&max_id="+str(max_id)
    res = oauthRequest(url,credentials)
    res = json.load(StringIO(res)) # converting the string into good json format

    if 'errors' in res or len(res) == 0:
        return False

    for tweet in res: #cleaning the tweets
        tweet = cleanTweet(tweet)
    return res

def returnOldTweets(screen_name,credentials,nbTweet):
    """Return (approximately) the last nbTweet for user 'screen_name'"""
    currentId = returnTweets(screen_name,credentials,1)[0]["id"]# id of the user's last tweet

    batchSize = min(nbTweet,200) # batchSize between 1 and 200
    maxIter = nbTweet/(batchSize+1) + 1 # number of requests to be send
    iterNum = 0 # counter for the loop
    lastId = 0
    tweets = [] # List of the nbTweet tweets
    while lastId != currentId and iterNum < maxIter:
        tweets += returnTweets(screen_name,credentials,batchSize,currentId)
        # Updating the ids
        lastId = currentId
        currentId = tweets[-1]["id"]-1

        iterNum = iterNum+1

    return tweets

def cleanTweet(tweet):
    """Clean a Tweet : delete the useless features to store infos in the database"""
    global uselessFields
    global stringFields

    fieldsToDelete = [k for k,v in tweet.items() if k not in usefullFields]
    for key in fieldsToDelete:
        del tweet[key]

    # remainingStrFields = [k for k,v in tweet.items() if k in stringFields]
    # for key in remainingStrFields:
    #     tweet[key] = str(tweet[key]).encode("utf-8")

    tweet["user_id"] = tweet["user"]["id"]
    del tweet["user"]

    return tweet


def cleanUser(user):
    """Clean a Tweet : delete the useless features and encode string in UTF8"""
    global usefullFieldsUser
    global stringFields

    fieldsToDelete = [k for k,v in user.items() if k not in usefullFieldsUser]
    for key in fieldsToDelete:
        del user[key]

    return user

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

# Credentials
consumerKey=getEnvValue('CONSUMER_KEY')
consumerSecret=getEnvValue('CONSUMER_SECRET')
key = getEnvValue('KEY')
secret = getEnvValue('SECRET')
credentials = [consumerKey,consumerSecret,key,secret]

baseURL = "https://api.twitter.com/1.1/"


# Tweets' Fields (see : https://dev.twitter.com/overview/api/tweets):

usefullFields = ["user","text","is_quote_status","in_reply_to_status_id","id",
                "favorite_count","user_id","source","in_reply_to_user_id","retweet_count",
                "lang","created_at"]

# uselessFields = ["contributors","id_str","filter_level","geo","favorited",
#              "geo","in_reply_to_user_id_str","in_reply_to_status_id_str",
#              "place","possibly_sensitive","quoted_status_id_str","quoted_status",
#              "quoted_status_id","retweeted","retweeted_status","withheld_copyright"
#              "withheld_in_countries","withheld_scope","favorited",
#              "truncated","coordinates","extended_entities","in_reply_to_screen_name","entities"]

stringFields = ["created_at","filter_level,id_str","in_reply_to_screen_name",
                "in_reply_to_status_id_str","in_reply_to_user_id_str","lang",
                "quoted_status_id_str","source","withheld_scope"]

# Users' Fields (see : https://dev.twitter.com/overview/api/users):

usefullFieldsUser = ["id","name","screen_name","created_at",
                     "contributors_enabled","verified"]

tweetSources =["HootSuite","Twitter for Android","Twitter Web Client",
            "Media Studio","Twitter for iPhone","Google","Twitter Ads",
            "Medium","TweetDeck","Twitter for iPad","SnappyTV"]

screen_nameToExtract = ["EmmanuelMacron","MLP_officiel","FrancoisFillon",
                        "benoithamon","JLMelenchon","MarCharlott","PhilippePoutou"]

#==============================#
#=========== TESTS ============#
#==============================#

def testTweet(screen_name):
    currentId = 798831991361703936
    maxIter = 0
    lastId = 0
    tweets = []
    while lastId != currentId and maxIter < 10:
        batchSize = 200
        tweets += returnTweets(screen_name,credentials,batchSize,currentId)
        lastId = currentId
        currentId = tweets[-1]["id"]-1
        print "----"
        print lastId, currentId
        print currentId," vs ",tweets[-1]["id"]
        # if tweets:
        #     remainingFields = [k for k,v in tweets[0].items()]
        #     print "---------------"
        #     for t in tweets:
        #         print t["id"]
        #     print "---------------"
        # else:
        #     print "Fail"

        maxIter = maxIter+1
    print len(tweets)

def testProfile(screen_name,toClean=True):
    user = returnProfile(screen_name,credentials,toClean)

    remainingFields = [k for k,v in user.items()]
    for i in remainingFields:
        print i,":", user[i]

if __name__ == '__main__':
    testTweet("jjerphan")
    #testProfile("EmmanuelMacron",False)
