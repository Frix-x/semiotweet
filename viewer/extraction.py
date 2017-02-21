#coding:utf8
import oauth2
from StringIO import StringIO
import json
import os, sys, getenv

# NOTE - TODO : ERROR during import ; the better way would be to save tweets in the views
from django.db.models import Max
#from models import Tweet,User

#==============================#
#========== REQUESTS ==========#
#==============================#

def oauthRequest(url,credentials,http_method="GET",post_body="",http_headers=None):
    """Prepare a request """
    consumer = oauth2.Consumer(key=credentials[0], secret=credentials[1])
    token = oauth2.Token(key=credentials[2], secret=credentials[3]) #Token of the app
    client = oauth2.Client(consumer, token) #Token of the user using the app
    resp, content = client.request( url, method=http_method, body=post_body, headers=http_headers )
    return content

#==============================#
#=========== TWEETS ===========#
#==============================#

def returnTweetsBatch(screen_name,count=False,max_id=False,since_id=False):
    """Return nbTweet<200 tweets form 'screen_name' with id in [max_id,since_id]"""
    """max_id and since_id can be specified"""
    global credentials
    global baseURL
    url = baseURL+'statuses/user_timeline.json?screen_name='+screen_name
    if count:
        url +='&count='+str(count)

    if max_id :
        url += "&max_id="+str(max_id)

    if since_id :
        url += "&since_id="+str(since_id)

    # Request
    res = oauthRequest(url,credentials)
    res = json.load(StringIO(res)) # converting the string into good json format

    if 'errors' in res or len(res) == 0:
        return False

    for tweet in res: #cleaning the tweets
        tweet = cleanTweet(tweet)
    return res

def returnTweetsMultiple(screen_name,option="latest"):
    """Return +/- the last nbTweet for user 'screen_name'.
    Uses returnTweetsBatch since the Twitter API limits to 200 Tweets"""
    # Preventing from saving other tweets :
    if not screen_name in screen_nameToExtract:
        return False

    tweets = [] # List of the nbTweet tweets
    currentId = returnTweetsBatch(screen_name,1)[0]["id"]# id of the user's last tweet
    if option == "all": # We only want to get ALL the tweets ; it supposes there are no tweets in the DB
        nbTweet = 3000 # NOTE : important setting
        batchSize = min(nbTweet,200) # batchSize between 1 and 200
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
        lastId = Tweet.objects.all().aggregate(Max('id'))
        while lastId < currentId :
            tweets += returnTweetsBatch(screen_name,batchSize,currentId,lastId)
            # Updating the id
            currentId = tweets[-1]["id"]-1

    # If the user doesn't exist or errors during the request
    if not(tweets):
        return False

    userFrom = User.objects.get(screen_name=screen_name)
    success = True

    # Saving tweets in database
    for t in tweets:
        success = saveTweet(t,userFrom) and success

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

    # Getting the source ; x.find(y) returns -1 if string y not in string x
    for s in tweetSources:
        if tweet["source"].lower().find(s.lower()) != -1:
            tweet["source"] = s
            break

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

    # Formating the date
    newTweet.created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(newTweet.created_at,'%a %b %d %H:%M:%S +0000 %Y'))

    # Saving the tweet
    try:
        newTweet.save()
        return True
    except BaseException:
        return False

#==============================#
#=========== USERS  ===========#
#==============================#

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

def cleanUser(user):
    """Clean a Tweet : delete the useless features and encode string in UTF8"""
    global usefullFieldsUser
    global stringFields

    fieldsToDelete = [k for k,v in user.items() if k not in usefullFieldsUser]
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
    newUser.created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(newUser.created_at,'%a %b %d %H:%M:%S +0000 %Y'))

    # Saving the user in the database
    try:
        newUser.save()
        return True
    except BaseException:
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

def testBatch(screen_name,count=False,max_id=False,since_id=False):
    res = returnTweetsBatch(screen_name,count,max_id,since_id)
    for t in res:
        print t["id"], t["text"]

    print len(res)

def testProfile(screen_name,toClean=True):
    user = returnProfile(screen_name,credentials,toClean)

    remainingFields = [k for k,v in user.items()]
    for i in remainingFields:
        print i,":", user[i]

if __name__ == '__main__':
    testBatch("EmmanuelMacron",count=4,max_id=833962028842770432,since_id=832997764984401920)
    # testTweet("jjerphan")
    #testProfile("EmmanuelMacron",False)
