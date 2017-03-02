#coding:utf8
import oauth2
from StringIO import StringIO
import json
import os, sys, getenv

#==============================#
#========== REQUESTS ==========#
#==============================#

def oauthRequest(url,credentials,http_method="GET",post_body="",http_headers=None):
    """Send a request to the Twitter API ; returns the result"""
    consumer = oauth2.Consumer(key=credentials[0], secret=credentials[1])
    token = oauth2.Token(key=credentials[2], secret=credentials[3]) #Token of the app
    client = oauth2.Client(consumer, token) #Token of the user using the app
    resp, content = client.request( url, method=http_method, body=post_body, headers=http_headers )
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
    res = json.load(StringIO(res)) # converting the string into good json format

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
        maxIter = nbTweet/(batchSize+1) + 1 # number of requests to send
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

    # NOTE : To encode string : no more usefull now
    # remainingStrFields = [k for k in tweet.keys() if k in stringFields]
    # for key in remainingStrFields:
    #     tweet[key] = str(tweet[key]).encode("utf-8")

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

    res = oauthRequest(baseURL+'users/show.json?screen_name='+screen_name,credentials)
    user = json.load(StringIO(res))
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

# uselessFields = ["contributors","id_str","filter_level","geo","favorited",
#              "geo","in_reply_to_user_id_str","in_reply_to_status_id_str",
#              "place","possibly_sensitive","quoted_status_id_str","quoted_status",
#              "quoted_status_id","retweeted","retweeted_status","withheld_copyright"
#              "withheld_in_countries","withheld_scope","favorited",
#              "truncated","coordinates","extended_entities","in_reply_to_screen_name","entities"]

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

screen_nameToExtract = ["EmmanuelMacron","MLP_officiel","FrancoisFillon",
                        "benoithamon","JLMelenchon","MarCharlott","PhilippePoutou"]

screen_nameToID = {'benoithamon': 14389177,
                  'JLMelenchon': 80820758,
                  'MLP_officiel': 217749896,
                  'PhilippePoutou': 374392774,
                  'FrancoisFillon': 551669623,
                  'MarCharlott': 1567664221,
                  'EmmanuelMacron': 1976143068,}





#==============================#
#=========== TESTS ============#
#==============================#

def testBatch(screen_name,count=False,max_id=False,since_id=False):
    res = returnTweetsBatch(screen_name,count,max_id,since_id)
    for t in res:
        print t["id"], t["text"]

    print len(res)

def testMultiple(screen_name,since_id=False):
    res = returnTweetsMultiple(screen_name,since_id)
    for t in res:
        print t["id"], t["text"]

    print len(res)


def testProfile(screen_name,toClean=True):
    user = returnUser(screen_name,credentials,toClean)

    remainingFields = user.keys()
    for i in remainingFields:
        print i,":", user[i]

if __name__ == '__main__':
    # testBatch("EmmanuelMacron",count=4,max_id=833962028842770432,since_id=832997764984401920)
    testMultiple("JLMelenchon",since_id=834891272267653122)
    # testBatch("JLMelenchon",since_id=834891272267653122)
    #testTweet("jjerphan")
    #testProfile("jjerphan",False)
