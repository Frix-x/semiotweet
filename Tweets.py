#coding:utf8
import oauth2
from StringIO import StringIO
import json
import os, sys, getenv


def oauthRequest(url, key, secret, http_method="GET", post_body="", http_headers=None):
    """Prepare a request """
    consumer = oauth2.Consumer(key="oYYo7f9lxceE8PZJiux8C36cJ", secret="VdnGr0H1tZHC0g1w1rYmYApHvxA1iNhzNFAcOTa4KV4qYmszDL")
    token = oauth2.Token(key=key, secret=secret) #Token of the app
    client = oauth2.Client(consumer, token) #Token of the user using the app
    resp, content = client.request( url, method=http_method, body=post_body, headers=http_headers )
    return content

def returnProfile(user,baseURL,key,secret):
    """Return the profile of the user whose the name 'user' was given"""
    res = oauthRequest(baseURL+'users/show.json?screen_name='+user, key,secret)
    return json.load(StringIO(res))

def returnTweet(user,baseURL,key,secret,nbTweet):
    """Return the last nbTweet he user 'user'"""
    res = oauthRequest(baseURL+'statuses/user_timeline.json?screen_name='+user+'&count='+str(nbTweet),key,secret)
    res = json.load(StringIO(res)) # converting the string into good json format

    for tweet in res: #cleaning the tweets
        tweet = cleanTweet(tweet)
    return res

def cleanTweet(tweet):
    """Clean a Tweet : delete the useless features and encode string in UTF8"""
    global uselessFields
    global stringFields

    fieldsToDelete = [k for k,v in tweet.items() if k not in usefullFields]
    for key in fieldsToDelete:
        del tweet[key]

    remainingStrFields = [k for k,v in tweet.items() if k in stringFields]
    # for key in remainingStrFields:
    #     tweet[key] = str(tweet[key]).encode("utf-8")

    tweet["user_id"] = tweet["user"]["id"]
    del tweet["user"]

    return tweet

#####

# Settings :
def getEnvValue(varName):
    """Return the value of an environment variable or an error if it isn't set"""
    if varName in os.environ:
        return os.environ.get(varName)
    else:
        sys.exit(varName + " is not defined in the environment variables")

key = getEnvValue('KEY')
secret = getEnvValue('SECRET')
baseURL = "https://api.twitter.com/1.1/"

# Fields (see : https://dev.twitter.com/overview/api/tweets):

usefullFields = ["user","text","is_quote_status","in_reply_to_status_id","id_str",
                "favorite_count","user_id","source","entities",
                "in_reply_to_screen_name","in_reply_to_user_id","retweet_count",
                "lang","created_at"]

# uselessFields = ["contributors","id","filter_level","geo","favorited",
#              "geo","in_reply_to_user_id_str","in_reply_to_status_id_str",
#              "place","possibly_sensitive","quoted_status_id_str","quoted_status",
#              "quoted_status_id","retweeted","retweeted_status","withheld_copyright"
#              "withheld_in_countries","withheld_scope","favorited",
#              "truncated","coordinates","extended_entities"]

stringFields = ["created_at","filter_level,id_str","in_reply_to_screen_name","in_reply_to_status_id_str",
              "in_reply_to_user_id_str","lang","quoted_status_id_str","source","withheld_scope"]

def main():
    tweets = returnTweet("EmmanuelMacron",baseURL,key,secret,4)
    # for tweet in tweets:
    #     print tweet["text"].encode("utf-8")

    remainingFields = [k for k,v in tweets[0].items()]
    for i in remainingFields:
        print i, type(tweets[0][i])

    print tweets[0]["in_reply_to_status_id"]
    print tweets[0]["in_reply_to_user_id"]



if __name__ == '__main__':
    main()
