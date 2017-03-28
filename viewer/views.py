#-*- coding: utf-8 -*-
from __future__ import print_function, absolute_import # For Py2 retrocompatibility
from builtins import str
from django.http import HttpResponse,Http404
from django.shortcuts import render,redirect

# Forthe database
from .models import Tweet,User,LdaModel
from django.db import connection #for direct SQL requests
from django.db.models import Max

# For time and date processing
import random
from django.utils import timezone
import time
import pytz
from datetime import datetime


# Data Processing
from .extraction import *
from .semanticAnalysis import *
import string
import json
import ast # convert string to list
import math


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
        return render(request,'home.html',{'error':'No data yet ; click on "Get the data"'})
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
    except BaseException: # No data in DB
        print("view home ; error : ",error)
        return render(request,'home.html',{"error":"Fonctionnalité indisponible pour le moment."})
    res = cursor.fetchall()
    politics = []
    nbTweets = []
    for (p,n) in res:
        politics.append(p)
        nbTweets.append(n)
    # JSON Formating
    politics = json.dumps(politics)
    nbTweets = json.dumps(nbTweets)

    # Getting the date of the last tweet
    lastTweet = Tweet.objects.aggregate(Max('id'))
    lastId = lastTweet["id__max"]
    try:
        maj = Tweet.objects.get(id=lastId).created_at
    except BaseException as e:
        maj = False
        print(e)
        pass

    return render(request,'home.html',{'sources': sources,
                                       'num': num,
                                       'politics': politics,
                                       'nbTweets': nbTweets,
                                       'maj' : maj})

def generalOverview(request):
    """Redirect to the words page : analysis around words used by politics"""
    # Getting tweets' sources
    cursor = connection.cursor()
    # Getting the number of tweets for each user
    try:
        cursor.execute("SELECT u.name, COUNT(t.id) AS nbTweets FROM viewer_tweet t, viewer_user u WHERE u.id = t.user_id_id GROUP BY u.name ORDER BY nbTweets DESC")
    except BaseException:
        print("view generalOverview ; error : ",error)
        return render(request,'generalOverview.html',{'error':'No data yet ; click on "Get the data"'})
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

    #Get hours distribution of all tweets
    try:
        cursor.execute("SELECT DISTINCT created_at AS timePosted FROM viewer_tweet ORDER BY timePosted")
    except BaseException as error:
        print("displayInfo() ; error : ", error)
        return render(request,'home.html',{'politics': politics, 'nbTweets': nbTweets, 'words': words, 'lemmes': lemmes})
    res = cursor.fetchall()
    hours =[0]*24
    for (time,) in res:
        hours[time.time().hour]+=1

    # Get LDA topics distribution for bubble Graph
    try :
        ldamodel = pickle.loads(LdaModel.objects.get(user_id=0).ldamodel)
    except BaseException as error:
        print("displayInfo() ; error : ", error)
        return render(request,'generalOverview.html',{'politics': politics, 'nbTweets': nbTweets, 'words': words, 'lemmes': lemmes, 'hours': hours})

    topics = ldamodel.show_topics(num_topics=10, num_words=8, log=False, formatted=False)
    bubblesJson = {"label":"Topics","amount":50,"children":[]}
    for index, topic in enumerate(topics):
        bubblesJson["children"].append({"label":topic[0],"amount":10,"children":[]})
        for word in topic[1]:
            bubblesJson["children"][index]["children"].append({"label":word[0],"amount":math.floor(300*word[1])})
    bubblesJson = json.dumps(bubblesJson,default=str)

    return render(request,'generalOverview.html',{'politics': politics, 'nbTweets': nbTweets, 'words': words, 'lemmes': lemmes, 'hours': hours, 'bubblesJson': bubblesJson})

def comparison(request):
    """Redirect to the comparison form page : compare two politics"""
    global screen_nameToExtract
    users = {}
    candidats = []
    wordsList = []
    lemmesList = []
    sourcesList = []
    numList = []
    hoursList = []
    for screen_name in screen_nameToExtract:
        users[screen_name] = returnUser(screen_name, toClean=False)

    if request.method == 'GET' and 'candidat1' in request.GET and 'candidat2' in request.GET:
        candidats.append(request.GET['candidat1'])
        candidats.append(request.GET['candidat2'])

        if candidats[0] in screen_nameToExtract and candidats[1] in screen_nameToExtract and candidats[0] != candidats[1]:
            for candidat in candidats:
                idUser = users[candidat]["id"]
                allTokenArray = Tweet.objects.filter(user_id=idUser).values('tokenArray')
                allLemmaArray = Tweet.objects.filter(user_id=idUser).values('lemmaArray')
                # tokenArray is stored as a string : we need to get the list back
                words = [ast.literal_eval(t["tokenArray"]) for t in allTokenArray]
                lemmes = [ast.literal_eval(t["lemmaArray"]) for t in allLemmaArray]
                # words is a JSON list of dict like : {"word":"foo", "occur":42}
                wordsList.append(json.dumps(toJsonForGraph(countWords(words))))
                lemmesList.append(json.dumps(toJsonForGraph(countWords(lemmes))))
                # Sources of Tweets
                global requestToGetSources
                cursor = connection.cursor()
                try:
                    cursor.execute("SELECT DISTINCT source, COUNT(source) AS nb FROM viewer_tweet WHERE user_id_id ='"+ str(idUser)+"' GROUP BY source ORDER BY nb DESC")
                except BaseException as error:
                    return render(request,'comparison.html', {'users':users})
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
                sourcesList.append(json.dumps(sources))
                numList.append(json.dumps(num))

                #Get hours distribution of user's tweets
                try:
                    cursor.execute("SELECT DISTINCT created_at AS timePosted FROM viewer_tweet WHERE user_id_id ='"+ str(idUser)+"' ORDER BY timePosted")
                except BaseException as error:
                    return render(request,'comparison.html', {'users':users})
                res = cursor.fetchall()
                hours =[0]*24
                for (time,) in res:
                    hours[time.time().hour]+=1
                hoursList.append(hours)
            return render(request,'comparison.html', {  "users":users,
                                                        "candidats":candidats,
                                                        "wordsList": wordsList,
                                                        "lemmesList": lemmesList,
                                                        "sourcesList": sourcesList,
                                                        "numList": numList,
                                                        "hoursList": hoursList})
        else:
            return render(request,'comparison.html', {'users':users})


    else:
        return render(request,'comparison.html', {'users':users})
    return render(request,'comparison.html', {'users':users})


def displayInfo(request,screen_name):
    """Display all the tweets for a user
    Requests the Twitter API directly and search for the most common words"""
    userInfo = returnUser(screen_name,toClean=False)
    success = True
    if not(userInfo): # If the user doesn't exist
        success = False
        return render(request,'displayInfo.html',{"success" : success})

    userInfo["profile_image_url_https"] = userInfo["profile_image_url_https"].replace('_normal.jpg','.jpg')

    # Most common words said by the user
    idUser = userInfo["id"]
    allTokenArray = Tweet.objects.filter(user_id=idUser).values('tokenArray')
    allLemmaArray = Tweet.objects.filter(user_id=idUser).values('lemmaArray')

    # tokenArray is stored as a string : we need to get the list back
    words = [ast.literal_eval(t["tokenArray"]) for t in allTokenArray]
    lemmes = [ast.literal_eval(t["lemmaArray"]) for t in allLemmaArray]

    # words is a JSON list of dict like : {"word":"foo", "occur":42}
    words = json.dumps(toJsonForGraph(countWords(words)))
    lemmes = json.dumps(toJsonForGraph(countWords(lemmes)))

    # Sources of Tweets
    global requestToGetSources
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT DISTINCT source, COUNT(source) AS nb FROM viewer_tweet WHERE user_id_id ='"+ str(idUser)+"' GROUP BY source ORDER BY nb DESC")
    except BaseException as error:
        print("displayInfo() ; error : ", error)
        return render(request,'home.html',{"success": success})
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
        return render(request,'home.html',{"success":success})
    res = cursor.fetchall()
    hours =[0]*24
    for (time,) in res:
        hours[time.time().hour]+=1

    return render(request,'displayInfo.html',{"userInfo" : userInfo,
                                              "words" : words,
                                              "lemmes" : lemmes,
                                              "hours" : hours,
                                              "sources" : sources,
                                              "screen_name" : screen_name,
                                              "num" : num,
                                              "success" : success})



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
            lastTweet = Tweet.objects.filter(user_id=idUser).aggregate(Max('id'))
            lastId = lastTweet["id__max"]
            # maj = Tweet.objects.get(id=lastId).created_at
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
#===== SEMANTIC NETWORK =======#
#==============================#

def displayNetwork(request):
    """Display a force network with users linked to their matching keywords"""

    return render(request,'displayNetwork.html',{"success": True})
