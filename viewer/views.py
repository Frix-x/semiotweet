#-*- coding: utf-8 -*-
from datetime import datetime
from django.http import HttpResponse,Http404
from django.shortcuts import render,redirect
from .models import Tweet,User
from extraction import *
import random
import string
import time

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

def saveTweets(request,screen_name,nbTweetToExtract):
    #NOTE - TODO : Currently working on standard requests
    #              WARNING : this is not a view !
    #              Unit-tests to be developed
    #              Exception handling to be improved
    """Save the last nbTweetToExtract from user 'screen_name'"""

    # Preventing from saving other tweets :
    if not screen_name in screen_nameToExtract:
        return False

    tweets = returnOldTweets(screen_name,credentials,int(nbTweetToExtract))
    # If the user doesn't exist or errors during the request
    if not(tweets):
        return False

    userFrom = User.objects.get(screen_name=screen_name)
    for t in tweets:
        newTweet = Tweet()
        newTweet.id = t['id']
        newTweet.user_id = userFrom
        newTweet.text = t['text']
        newTweet.created_at = t['created_at']
        newTweet.is_quote_status = t['is_quote_status']
        newTweet.in_reply_to_status_id = t['in_reply_to_status_id']
        newTweet.favorite_count = t['favorite_count']
        newTweet.retweet_count = t['retweet_count']
        newTweet.source = t['source']
        newTweet.in_reply_to_user_id = t['in_reply_to_user_id']
        newTweet.lang = t['lang']

        # Formating the date
        newTweet.created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(newTweet.created_at,'%a %b %d %H:%M:%S +0000 %Y'))
        newTweet.save()

        # Saving the tweet
        try:
            newTweet.save()
        except BaseException:
            continue

    return tweets

def getTweets(request,screen_name,nbTweetToExtract):
    """Save latest tweets from a user"""
    tweets = saveTweets(request,screen_name,nbTweetToExtract)
    if tweets:
        success = True
    else:
        success = False
    return render(request,'getTweets.html',locals())


def getAllTweets(request,nbTweetToExtract=5):
    """Save latest tweets from all the users defined in screen_nameToExtract"""
    global screen_nameToExtract
    success = True
    for screen_name in screen_nameToExtract:
        success = True and saveTweets(request,screen_name,nbTweetToExtract)

    return render(request,'getAllTweets.html',locals())



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

    newUser = User()
    remainingFields = [k for k,v in userInfo.items()]


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
    except BaseException:
        success = False
    return render(request,'getUser.html',locals())
