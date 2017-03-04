#-*- coding: utf-8 -*-
# from datetime import datetime
from django.utils import timezone
from django.http import HttpResponse,Http404
from django.shortcuts import render,redirect
from .models import Tweet,User,Word
import random
import string
import time
from django.db.models import Max
from django.db import connection #for direct SQL requests

import json

from extraction import *
from semanticFields import *
#==============================#
#=========== OTHERS ===========#
#==============================#

def home(request):
    """Redirect to the home page : global statistics"""
    cursor = connection.cursor()
    try:
        cursor.execute('SELECT DISTINCT source, COUNT(source) AS nb  FROM viewer_tweet GROUP BY source ORDER BY nb DESC')
    except BaseException:
        return render(request,'home.html',{"error":"No data yet ; click on 'Get the data'"})
    res = cursor.fetchall()
    sources = []
    num = []
    for (s,n) in res:
        sources.append(s)
        num.append(n)

    # Keeping only the most commons stats
    if len(sources)>5 :
        sources = sources[0:5]
        sources.append("Others")
        num[6] = sum(num[6:-1])
        num = num[0:6]

    # JSON Formating
    sources = json.dumps(sources)
    num = json.dumps(num)

    listTweetText = Tweet.objects.values('text')
    listTweetText = [t["text"] for t in listTweetText]
    listTweetText = countWords(listTweetText)

    words = []
    occurences = []
    for w,o in listTweetText.items():
        words.append(w)
        occurences.append(o)

    colorsForBars = ['rgba(54, 162, 235, 1)']*len(words)

    # JSON Formating
    words = json.dumps(words)
    occurences = json.dumps(occurences)
    return render(request,'home.html',locals())

def displayInfo(request,screen_name):
    """Display all the tweets for a user
    Requests the Twitter API directly and search for the most common words"""
    userInfo = returnUser(screen_name,toClean=False)
    success = True
    if not(userInfo): # If the user doesn't exist
        success = False
        return render(request,'displayInfo.html',locals())

    userInfo["profile_image_url_https"] = userInfo["profile_image_url_https"].replace('_normal.jpg','.jpg')

    # Most common words said by the user
    idUser = userInfo["id"]
    listTweetText = Tweet.objects.filter(user_id=idUser).values('text')
    listTweetText = [t["text"] for t in listTweetText]

    # words is a JSON list of dict like : {"word":"foo", "occur":42}
    words = json.dumps(toJsonForBubbles(countWords(listTweetText)))
    return render(request,'displayInfo.html',locals())

#==============================#
#=========== TWEETS ===========#
#==============================#

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

def getData(request):
    """Save the latest tweets from all the users defined in screen_nameToExtract"""
    """Stores info about a users in the database
    If screen_name == "all" : store all
    Else : only store info of one user"""
    global screen_nameToExtract

    # SAVING USERS
    for screen_name in screen_nameToExtract:
        userInfo = returnUser(screen_name,toClean=True)

        if not(userInfo): #If the user doesn't exist
            success = False
            error = "The user doesn't exist"
            return render(request,'getData.html',{"success" : success,
                                                  "error" : error})

        # Saving the user
        success = saveUser(userInfo)
        if not(success):
            error = "Error during saving in DB"
            return render(request,'getData.html',{"success" : success,
                                                  "error" : error})

    # SAVING TWEETS
    lastId = 0
    nbTweets = 0 # number of extracted tweets

    for screen_name in screen_nameToExtract:
        try:
            idUser = User.objects.filter(screen_name=screen_name).values('id')[0]["id"]
        except SomeModel.DoesNotExist: # If the user does not exist
            continue # continue with the next user

        try: # We try to get the id of the user's last tweet
            lastId = Tweet.objects.filter(user_id=idUser).aggregate(Max('id'))["id__max"]
        except SomeModel.DoesNotExist:
            lastId = 0 # No tweet in the data base

        tweets = returnTweetsMultiple(screen_name,lastId)
        nbTweets += len(tweets)

        # Saving tweets in database
        userFrom = User.objects.get(screen_name=screen_name)
        for t in tweets:
            success = saveTweet(t,userFrom) and success


    return render(request,'getData.html',{"success" : success,
                                          "nbTweets" : nbTweets,
                                          "screen_nameToExtract": screen_nameToExtract})

#==============================#
#=========== USERS  ===========#
#==============================#

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
#=========== WORDS  ===========#
#==============================#

def getWords(request):
    """ Stores common words and semantic fields of the specifiedWords """
    global specifiedWords

    # Saving the common words
    for word in commonWords:
        newWord = Word(word=word,semanticField="#")
        newWord.save()

    # Saving the semantic field of the specifiedWords
    for word in specifiedWords:
        semanticField = getSemanticField(word)
        for relatedWord in semanticField:
            newWord = Word(word=relatedWord,semanticField=word)
            newWord.save()

    return render(request,'getWords.html',{"success": True, "specifiedWords" : specifiedWords})

#==============================#
#===== SEMANTIC NETWORK =======#
#==============================#

def displayNetwork(request):
    """Display a force network with users linked to their matching keywords"""

    return render(request,'displayNetwork.html',{"success": True})
