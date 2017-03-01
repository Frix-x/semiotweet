#-*- coding: utf-8 -*-
from datetime import datetime
from django.http import HttpResponse,Http404
from django.shortcuts import render,redirect
from .models import Tweet,User
from extraction import *
import random
import string
import time
from django.db.models import Max

#==============================#
#=========== OTHERS ===========#
#==============================#

def home(request):
    """Redirect to the home page"""
    return render(request,'home.html',locals())

def displayInfo(request,screen_name):
    #NOTE - TODO : Profile images dont't appear : how about stocking them ?
    #              Front-end to be done
    """Display all the tweets for a user"""
    userInfo = returnUser(screen_name,toClean=False)
    success = True
    if not(userInfo): #If the user doesn't exist
        success = False
    else:
        userInfo["profile_image_url_https"] = userInfo["profile_image_url_https"].replace('_normal.jpg','.jpg')
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

def getTweets(request,option):
    """Save the latest tweets from all the users defined in screen_nameToExtract"""
    global screen_nameToExtract
    success = True
    lastId =0
    for screen_name in screen_nameToExtract:
        if option == "latest": # We get the id of the user's last tweet
            idUser = User.objects.filter(screen_name=screen_name).values('id')[0]["id"]
            lastId = Tweet.objects.filter(user_id=idUser).aggregate(Max('id'))["id__max"]

        tweets = returnTweetsMultiple(screen_name,lastId)
        userFrom = User.objects.get(screen_name=screen_name)

        # Saving tweets in database
        for t in tweets:
            success = saveTweet(t,userFrom) and success

    return render(request,'getTweets.html',{"success" : success, "nbTweets" : len(tweets)})

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
    except BaseException, e:
        print "Error :{0} : {1}".format(e.errno, e.strerror):
        return False

def getUser(request,screen_name):
    #NOTE - TODO :Currently working on standard requests
    #              Unit-tests to be developed
    """ Stores info about a users in the database
    If screen_name == "all" : store all
    Else : only store info of one user"""
    global screen_nameToExtract

    usersToExtract = []
    if screen_name == "all":
        usersToExtract = screen_nameToExtract
    else:
        usersToExtract.append(screen_name)

    for user in usersToExtract:
        userInfo = returnUser(user,toClean=True)

        if not(userInfo): #If the user doesn't exist
            success = False
            error = "The user doesn't exist"
            return render(request,'getUser.html',locals())

        # Saving the user
        success = saveUser(userInfo)

    error = "Error during DB save"
    return render(request,'getUser.html',locals())
