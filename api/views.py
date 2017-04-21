#-*- coding: utf-8 -*-
from __future__ import print_function, absolute_import # For Py2 retrocompatibility
from builtins import str
from django.http import HttpResponse,Http404,JsonResponse
from django.shortcuts import render,redirect

# For the API
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser


# Forthe database
from .models import Tweet,User,LdaModel,semanticField
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
from collections import Counter,defaultdict

# Decorators
from django.views.decorators.http import require_GET
#==============================#
#=========== OTHERS ===========#
#==============================#


def handler404(request,typed):
    """A basic 404 error handler"""
    return JsonResponse({"error":"Page "+typed+" not found"}, status=404)


@require_GET
def sources(request):
    """GET Tweets'sources for all or individual candidate"""
    # Getting tweets' sources
    global requestToGetSources

    # GET user and check if he exist
    userId = request.GET.get("id", "")
    try:
        if userId != "":
            User.objects.get(id=userId)
    except BaseException as e:
        return JsonResponse({"sources":-1,"num":-1,"error":str(e)}, status=500)

    cursor = connection.cursor()
    try:
        if userId == "":
            cursor.execute(requestToGetSources)
        else:
            cursor.execute("SELECT DISTINCT source, COUNT(source) AS nb FROM api_tweet WHERE user_id_id ='"+ str(userId)+"' GROUP BY source ORDER BY nb DESC")
    except BaseException as e: # No data in DB
        print("API - sources()\nError : ", e)
        return JsonResponse({"sources":-1,"num":-1,"error":str(e)}, status=500)
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
        num[5] = sum(num[5:-1])
        num = num[0:6]

    return JsonResponse({"sources":sources,"num":num}, status=200)


@require_GET
def userExist(request):
    # GET user and check if he exist
    userId = request.GET.get("id", "")
    if userId == "":
        return JsonResponse({"id":userId,"exist":False}, status=200)
    else:
        try:
            User.objects.get(id=userId)
        except BaseException as e:
            return JsonResponse({"id":userId,"exist":False}, status=200)
        return JsonResponse({"id":userId,"exist":True}, status=200)


@require_GET
def user(request):
    """GET candidate's informations such as followers_count, profile picture, profile description and screen name"""
    # GET user and check if he exist
    userId = request.GET.get("id", "")
    try:
        if userId != "":
            User.objects.get(id=userId)
    except BaseException as e:
        return JsonResponse({"users":-1,"error":str(e)}, status=500)

    cursor = connection.cursor()
    try:
        if userId == "":
            cursor.execute("SELECT id, screen_name, name, description, followers_count, verified, profile_image_url FROM api_user")
        else:
            cursor.execute("SELECT id, screen_name, name, description, followers_count, verified, profile_image_url FROM api_user WHERE id ='"+ str(userId)+ "'")
    except BaseException as e: # No data in DB
        print("API - userInfo()\nError : ", e)
        return JsonResponse({"users":-1,"error":str(e)}, status=500)
    res = cursor.fetchall()
    users = []
    for user in res:
        users.append({"id":user[0], "screen_name":user[1], "name": user[2], "description": user[3], "followers_count": user[4], "verified" : user[5], "profile_image_url": user[6].replace('_normal.jpg','.jpg')})

    return JsonResponse({"users":users}, status=200)


@require_GET
def nbTweets(request):
    """GET number of tweets for each candidates"""
    # Getting the number of tweets for each user
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT u.name, COUNT(t.id) AS nbTweets FROM api_tweet t, api_user u WHERE u.id = t.user_id_id GROUP BY u.name ORDER BY nbTweets DESC")
    except BaseException as e: # No data in DB
        print("API - nbTweets()\nError : ", e)
        return JsonResponse({"politics":-1,"nbTweets":-1,"error":str(e)}, status=400)
    res = cursor.fetchall()

    politics = []
    nbTweets = []
    for (p,n) in res:
        politics.append(p)
        nbTweets.append(n)
    # JSON Formating
    return JsonResponse({"politics":politics,"nbTweets":nbTweets}, status=200)


@require_GET
def lastTweet(request):
    """GET date of the last tweet saved in DB"""
    # Getting the date of the last tweet
    try:
        lastTweetReq = Tweet.objects.aggregate(Max('id'))
        lastId = lastTweetReq["id__max"]
        lastTweet = Tweet.objects.get(id=lastId).created_at
    except BaseException as e:
        print("API - lestTweet()\nError : ", e)
        return JsonResponse({"lasttweet":-1,"error":str(e)}, status=500)

    return HttpResponse(lastTweet, status=200)


@require_GET
def hours(request):
    """GET tweets hours distribution for one or all candidates"""
    # GET user and check if he exist
    userId = request.GET.get("id", "")
    try:
        if userId != "":
            User.objects.get(id=userId)
    except BaseException as e:
        return JsonResponse({"hours":-1,"error":str(e)}, status=500)

    cursor = connection.cursor()
    try:
        if userId == "":
            cursor.execute("SELECT DISTINCT created_at AS timePosted FROM api_tweet ORDER BY timePosted")
        else:
            cursor.execute("SELECT DISTINCT created_at AS timePosted FROM api_tweet WHERE user_id_id ='"+ str(userId)+"'ORDER BY timePosted")
    except BaseException as e: # No data in DB
        print("API - hours()\nError : ", e)
        return JsonResponse({"hours":-1,"error":str(e)}, status=400)
    res = cursor.fetchall()

    hours =[0]*24
    for (time,) in res:
        hours[time.time().hour]+=1

    # JSON Formating
    return JsonResponse({"hours":hours}, status=200)

@require_GET
def wordCount(request):
    userId = request.GET.get("id", "")

    # tokenArray is stored as a string : we need to get the list back
    try:
        if userId == "":
            allTokenArray = Tweet.objects.values('tokenArray')
        else:
            allTokenArray = Tweet.objects.filter(user_id=userId).values('tokenArray')
    except BaseException as e:
        print("API - wordCount()\nError : ", e)
        return JsonResponse({"words":-1,"error":str(e)}, status=500)

    words = [ast.literal_eval(t["tokenArray"]) for t in allTokenArray]
    words = toJsonForGraph(countWords(words))

    # words is a JSON list of dict like : {"word":"foo", "occur":42}
    return JsonResponse({"words":words}, status=200)

@require_GET
def lemmeCount(request):
    userId = request.GET.get("id", "")

    # lemmaArray is stored as a string : we need to get the list back
    try:
        if userId == "":
            allLemmaArray = Tweet.objects.values('lemmaArray')
        else:
            allLemmaArray = Tweet.objects.filter(user_id=userId).values('lemmaArray')
    except BaseException as e:
        print("API - lemmeCount()\nError : ", e)
        return JsonResponse({"lemmes":-1,"error":str(e)}, status=500)

    lemmes = [ast.literal_eval(t["lemmaArray"]) for t in allLemmaArray]
    lemmes = toJsonForGraph(countWords(lemmes))

    # lemmes is a JSON list of dict like : {"word":"foo", "occur":42}
    return JsonResponse({"lemmes":lemmes}, status=200)


@require_GET
def ldaTopics(request):
    # GET user and check if he exist
    userId = request.GET.get("id", 0)

    # Get LDA topics distribution for table
    try :
        ldamodel = pickle.loads(LdaModel.objects.get(user_id=userId).ldamodel)
    except BaseException as e:
        print("API - ldaTopics()\nError : ", e)
        return JsonResponse({"ldaTopics":-1,"error":str(e)}, status=500)

    topics = ldamodel.show_topics(num_topics=-1, num_words=10, log=False, formatted=False)
    tableJson = {"label":"ldaTopics","topics":[]}
    for index, topic in enumerate(topics):
        tableJson["topics"].append({"label":topic[0],"words":[]})
        for word in topic[1]:
            tableJson["topics"][index]["words"].append({"label":word[0],"weight":math.floor(300*word[1])})

    return JsonResponse(tableJson, status=200)


@require_GET
def netTweets(request):
    # Get users and link them to semantic fields
    try:
        semanticField_db = semanticField.objects.all().values()
        users = User.objects.all().values("screen_name", "name")
        cursor = connection.cursor()
        cursor.execute("SELECT u.screen_name, COUNT(t.id) AS nbTweets FROM api_tweet t, api_user u WHERE u.id = t.user_id_id GROUP BY u.screen_name")
    except BaseException as e:
        print("API - netTweets()\nError : ", e)
        return JsonResponse({"error":str(e)}, status=500)

    tweetCount = dict(cursor.fetchall())
    # tweetCount['total'] = sum(tweetCount.values())

    network = {"nodes":[], "edges":[]}
    nodeId = 1
    edgeId = 1
    appendedNodes = dict()
    appendedThemes = dict()
    maxScore = 0

    # User nodes
    for user in users:
        network["nodes"].append({"id":nodeId,"label":user["name"],"screen_name":user["screen_name"],"size":50,"color":"#ff9800"})
        appendedNodes[user["screen_name"]] = nodeId
        nodeId += 1

    # Semantic theme nodes
    for semanticLine in semanticField_db:
        if semanticLine["baseWord"] not in appendedThemes:
            network["nodes"].append({"id":nodeId,"label":semanticLine["baseWord"],"weight":0,"size":50,"color":"#2196f3"})
            network["nodes"].append({"id":nodeId+1,"label":semanticLine["baseWord"],"size":10,"color":"#607d8b"})
            network["edges"].append({"id":edgeId,"source":nodeId,"target":nodeId+1,"weight":50,"color":"rgba(96,125,139,0.1)"})
            appendedThemes[semanticLine["baseWord"]] = nodeId
            appendedNodes[semanticLine["baseWord"]] = nodeId+1
            nodeId += 2
            edgeId += 1

        uScores = ast.literal_eval(semanticLine["usersScores"])
        for screen_name,score in uScores.items():
            if (score/tweetCount[screen_name]) > maxScore:
                maxScore = score/tweetCount[screen_name]

    # Associated semantic words nodes + links all those nodes together
    for semanticLine in semanticField_db:
        uScores = ast.literal_eval(semanticLine["usersScores"])
        if not all(score == 0 for score in uScores.values()):
            if semanticLine["word"] not in appendedNodes:
                network["nodes"].append({"id":nodeId,"label":semanticLine["word"],"size":10,"color":"#607d8b"})
                network["edges"].append({"id":edgeId,"source":appendedThemes[semanticLine["baseWord"]],"target":nodeId,"weight":50,"color":"rgba(96,125,139,0.1)"})
                appendedNodes[semanticLine["word"]] = nodeId
                nodeId += 1
            else:
                network["edges"].append({"id":edgeId,"source":appendedThemes[semanticLine["baseWord"]],"target":appendedNodes[semanticLine["word"]],"weight":50,"color":"rgba(96,125,139,0.1)"})
            edgeId += 1

            for screen_name,score in uScores.items():
                if score != 0:
                    computedWeigth = (score/tweetCount[screen_name]*90/maxScore)+10
                    network["edges"].append({"id":edgeId,"source":appendedNodes[screen_name],"target":appendedNodes[semanticLine["word"]],"weight":computedWeigth,"color":"rgba(255,152,0,0.02)"})
                    edgeId += 1

    return JsonResponse({"network":network}, status=200)


#==============================#
#===========  DATA  ===========#
#==============================#

def getData(request):
    """Save the latest tweets from all the users defined in screen_nameToExtract
     and stores info about a users in the database not already done"""
    global screen_nameToExtract
    global semanticWords

    # SAVING USERS
    for screen_name in screen_nameToExtract:
        print ("GET User info : "+screen_name)
        userInfo = returnUser(screen_name,toClean=True)

        if not(userInfo): #If the user doesn't exist
            success = False
            error = "The user doesn't exist"
            return JsonResponse({"res":{"success":success,"error":error}}, status=500)

        # Saving the user
        success = saveUser(userInfo)
        if not(success):
            error = "Error during saving in DB"
            return JsonResponse({"res":{"success":success,"error":error}}, status=500)

    # SAVING TWEETS
    lastId = 0
    nbTweets = 0 # number of extracted tweets

    for screen_name in screen_nameToExtract:
        print ("GET USER TWEETS : "+screen_name)
        try:
            idUser = User.objects.filter(screen_name=screen_name).values('id')[0]["id"]
        except BaseException as e : # If the user does not exist
            continue # continue with the next user

        try: # We try to get the id of the user's last tweet
            lastTweet = Tweet.objects.filter(user_id=idUser).aggregate(Max('id'))
            lastId = lastTweet["id__max"]
            if lastId == None: # No tweet in the data base
                lastId = 0
        except BaseException as e :
            return JsonResponse({"res":{"success":success,"error":error}}, status=500)

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
            print ("SAVING {1} TWEETS FROM {0} ; {2:0.2f} %".format(screen_name,lenghtTweets,nbTweetsSaved/lenghtTweets*100))
            success = saveTweet(t,userFrom) and success
            nbTweetsSaved += 1;

    # MAKING LDA MODELS
    for screen_name in screen_nameToExtract:
        print ("MAKING LDA MODEL FOR : "+screen_name)
        try:
            idUser = User.objects.filter(screen_name=screen_name).values('id')[0]["id"]
        except BaseException as e : # If the user does not exist or table not present
            return JsonResponse({"res":{"success":success,"error":error}}, status=500)

        makeLdaModel(idUser)
    print("MAKING GLOBAL LDA MODEL")
    makeLdaModel(0)

    # POPULATING SEMANTIC FIELDS
    print("MAKING SEMANTIC FIELDS")
    semanticField.objects.all().delete()
    globalLemmesOccurences = {}
    # Pour chaque candidat, on compte l'occurence de ses lemmes à l'avance
    for screen_name in screen_nameToExtract:
        try:
            idUser = User.objects.filter(screen_name=screen_name).values('id')[0]["id"]
            allLemmaArray = Tweet.objects.filter(user_id=idUser).values("lemmaArray")
        except BaseException: # If the user does not exist or table to present
            continue # continue with the next user
        allLemmaArray = [ast.literal_eval(t["lemmaArray"]) for t in allLemmaArray]
        userLemmesOccurences = defaultdict(lambda: 0)
        for lemmaArray in allLemmaArray:
            currentOccurences = dict(Counter(lemmaArray))
            for k in list(currentOccurences.keys()):
                userLemmesOccurences[k] += currentOccurences[k]
        globalLemmesOccurences[screen_name] = userLemmesOccurences
    # Pour chaque mot de base, on cherche le champs lexical associé
    for baseWord in semanticWords:
        semanticFieldTable = getSemanticField(baseWord)
        # Pour chaque mot du champ lexical, on regarde le nombre d'occurence pour chaque candidat et on sauvegarde
        for word in semanticFieldTable:
            wordOccur = {}
            for screen_name in screen_nameToExtract:
                wordOccur[screen_name] = globalLemmesOccurences[screen_name][word]
            semanticField_db = semanticField()
            semanticField_db.baseWord = baseWord
            semanticField_db.word = word
            semanticField_db.usersScores = wordOccur
            try:
                semanticField_db.save()
            except BaseException as e:
                print("getData() ; error in making semantic fields : ", e)

    print("\nEVERYTHING DONE !")
    return JsonResponse({"res":{"success":success,"error":0}}, status=200)
