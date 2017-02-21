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

def home(request):
    """Redirect to the home page"""
    return render(request,'home.html',locals())

def displayInfo(request,screen_name):
    #NOTE - TODO : Profile images dont't appear : how about stocking them ?
    #              Front-end to be done
    """Display all the tweets for a user"""
    userInfo = returnProfile(screen_name,credentials,toClean=False)
    success = True
    if not(userInfo): #If the user doesn't exist
        success = False
    else:
        userInfo["profile_image_url_https"] = userInfo["profile_image_url_https"].replace('_normal.jpg','.jpg')
    return render(request,'displayInfo.html',locals())

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
    if option == "latest":
        lastId = Tweet.objects.all().aggregate(Max('id'))
    for screen_name in screen_nameToExtract:
        tweets = returnTweetsMultiple(screen_name,lastId)

        userFrom = User.objects.get(screen_name=screen_name)

        # Saving tweets in database
        for t in tweets:
            success = saveTweet(t,userFrom) and success

    return render(request,'getTweets.html',locals())


def getUser(request,screen_name):
    #NOTE - TODO :Currently working on standard requests
    #              Unit-tests to be developed
    """ Stores info about a user in the database"""
    # toClean to True : saves only the info that matters (see User model)
    userInfo = returnProfile(screen_name,credentials,toClean=True)
    success = True

    if not(userInfo): #If the user doesn't exist
        success = False
        return render(request,'getUser.html',locals())

    # Saving the user
    success = saveUser(userInfo)

    return render(request,'getUser.html',locals())
