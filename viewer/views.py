#-*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import
from builtins import str
from django.utils import timezone
from django.http import HttpResponse,Http404
from django.shortcuts import render,redirect
from .models import Tweet,User,LdaModel
import random
import string
import time
import pytz
from datetime import datetime
from django.db.models import Max
from django.db import connection #for direct SQL requests

import json
import ast # convert string to list

from .extraction import *
from .semanticFields import *

#==============================#
#=========== OTHERS ===========#
#==============================#

def handler404(request,typed):
    """A basic 404 error handler"""
    response = render(request,'404.html', {"typed":typed})
    response.status_code = 404
    return response


def home(request):
    """Redirect to the home page : global statistics"""
    global requestToGetSources

    # Getting tweets' sources
    cursor = connection.cursor()
    try:
        cursor.execute(requestToGetSources)
    except BaseException as error:
        print("view home ; error : ", error)
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
        sources.append(u"Others")
        num[5] = sum(num[5:-1])
        num = num[0:6]

    # JSON Formating
    sources = json.dumps(sources)
    num = json.dumps(num)

    # Getting the number of tweets for each user
    try:
        cursor.execute("SELECT u.name, COUNT(t.id) AS nbTweets FROM viewer_tweet t, viewer_user u WHERE u.id = t.user_id_id GROUP BY u.name ORDER BY nbTweets DESC")
    except BaseException:
        print("view home ; error : ",error)
        return render(request,'home.html',{"error":"No data yet ; click on 'Get the data'"})
    res = cursor.fetchall()
    politics = []
    nbTweets = []
    for (p,n) in res:
        politics.append(p)
        nbTweets.append(n)

    # JSON Formating
    politics = json.dumps(politics)
    nbTweets = json.dumps(nbTweets)

    # tokenArray and lemmaArray are stored as a string : we need to get the lists back
    allTokenArray = Tweet.objects.values('tokenArray')
    words = [ast.literal_eval(t["tokenArray"]) for t in allTokenArray]
    allLemmaArray = Tweet.objects.values('lemmaArray')
    lemmes = [ast.literal_eval(t["lemmaArray"]) for t in allLemmaArray]

    # words is a JSON list of dict like : {"word":"foo", "occur":42}
    words = json.dumps(toJsonForGraph(countWords(words)))
    lemmes = json.dumps(toJsonForGraph(countWords(lemmes)))
    colorsForBars = ['rgba(54, 162, 235, 1)']*len(words)

    #Get hours distribution of all tweets
    try:
        cursor.execute("SELECT DISTINCT created_at AS timePosted FROM viewer_tweet ORDER BY timePosted")
    except BaseException as error:
        print("displayInfo() ; error : ", error)
        return render(request,'home.html',locals())
    res = cursor.fetchall()
    hours =[0]*24
    for (time,) in res:
        hours[time.time().hour]+=1

    # Get LDA topics distribution for bubble Graph
    ldamodel = pickle.loads(LdaModel.objects.get(user_id=0).ldamodel)
    topics = ldamodel.print_topics(num_topics=10, num_words=5)
    print(topics)

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
    allTokenArray = Tweet.objects.filter(user_id=idUser).values('tokenArray')

    # tokenArray is stored as a string : we need to get the list back
    words = [ast.literal_eval(t["tokenArray"]) for t in allTokenArray]

    # words is a JSON list of dict like : {"word":"foo", "occur":42}
    words = json.dumps(toJsonForGraph(countWords(words)))

    # Sources of Tweets
    global requestToGetSources
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT DISTINCT source, COUNT(source) AS nb FROM viewer_tweet WHERE user_id_id ='"+ str(idUser)+"' GROUP BY source ORDER BY nb DESC")
    except BaseException as error:
        print("displayInfo() ; error : ", error)
        return render(request,'home.html',locals())
    res = cursor.fetchall()
    sources = []
    num = []
    for (s,n) in res:
        sources.append(s)
        num.append(n)

    # Keeping only the most commons stats
    if len(sources)>5 :
        sources = sources[0:5]
        sources.append(u"Others")
        num[5] = sum(num[5:-1])
        num = num[0:6]

    # JSON Formating
    sources = json.dumps(sources)
    num = json.dumps(num)

    #Get hours distribution of user's tweets
    try:
        cursor.execute("SELECT DISTINCT created_at AS timePosted FROM viewer_tweet WHERE user_id_id ='"+ str(idUser)+"' ORDER BY timePosted")
    except BaseException as error:
        print("displayInfo() ; error : ", error)
        return render(request,'home.html',locals())
    res = cursor.fetchall()
    hours =[0]*24
    for (time,) in res:
        hours[time.time().hour]+=1

    return render(request,'displayInfo.html',locals())

#==============================#
#===========  DATA  ===========#
#==============================#

def getData(request):
    """Save the latest tweets from all the users defined in screen_nameToExtract
     and stores info about a users in the database not already done"""
    global screen_nameToExtract

    # SAVING USERS
    for screen_name in screen_nameToExtract:
        print ("GET User info : "+screen_name)
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
        print ("GET user tweets : "+screen_name)
        try:
            idUser = User.objects.filter(screen_name=screen_name).values('id')[0]["id"]
        except SomeModel.DoesNotExist: # If the user does not exist
            continue # continue with the next user

        try: # We try to get the id of the user's last tweet
            lastId = Tweet.objects.filter(user_id=idUser).aggregate(Max('id'))["id__max"]
        except SomeModel.DoesNotExist:
            lastId = 0 # No tweet in the data base

        # The important request here : returns the new tweets from the Twitter API
        tweets = returnTweetsMultiple(screen_name,lastId)

        lenghtTweets = len(tweets)
        nbTweets += lenghtTweets

        # After this operations each tweet in tweets contains 2 more fields : 'tokenArray' & 'lemmaArray'
        tweets = tokenizeAndLemmatizeTweets(tweets)

        # Saving tweets in database
        userFrom = User.objects.get(screen_name=screen_name)
        nbTweetsSaved = 1; #counter for printing
        for t in tweets:
            print ("Saving {1} tweets from {0} ; {2:0.2f} %".format(screen_name,lenghtTweets,nbTweetsSaved/lenghtTweets*100))
            success = saveTweet(t,userFrom) and success
            nbTweetsSaved += 1;

    # MAKING LDA MODELS
    for screen_name in screen_nameToExtract:
        print ("MAKING LDA MODEL FOR : "+screen_name)
        try:
            idUser = User.objects.filter(screen_name=screen_name).values('id')[0]["id"]
        except SomeModel.DoesNotExist: # If the user does not exist
            continue # continue with the next user
        makeLdaModel(idUser)
    print("MAKING GLOBAL LDA MODEL...")
    makeLdaModel(0)

    print("\nEVERYTHING DONE !")
    return render(request,'getData.html',{"success" : success,
                                          "nbTweets" : nbTweets,
                                          "screen_nameToExtract": screen_nameToExtract})

#==============================#
#=========== WORDS  ===========#
#==============================#

# def getWords(request):
#     """ Stores common words and semantic fields of the specifiedWords """
#     global specifiedWords
#     global frenchStopwords
#
#     # Saving the common words
#     for word in frenchStopwords:
#         newWord = Word(word=word,semanticField="#")
#         newWord.save()
#
#     # Saving the semantic field of the specifiedWords
#     for word in specifiedWords:
#         semanticField = getSemanticField(word)
#         for relatedWord in semanticField:
#             newWord = Word(word=relatedWord,semanticField=word)
#             newWord.save()
#
#     return render(request,'getWords.html',{"success": True, "specifiedWords" : specifiedWords})

#==============================#
#===== SEMANTIC NETWORK =======#
#==============================#

def displayNetwork(request):
    """Display a force network with users linked to their matching keywords"""

    return render(request,'displayNetwork.html',{"success": True})
