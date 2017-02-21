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


def getLatestTweets(request):
    """Save the latest tweets from all the users defined in screen_nameToExtract"""
    global screen_nameToExtract
    success = True
    for screen_name in screen_nameToExtract:
        success = returnTweetsMultiple(screen_name,"latest") and success

    return render(request,'getTweets.html',locals())


def getAllTweets(request):
    """Save all the tweets from all the users defined in screen_nameToExtract"""
    global screen_nameToExtract
    success = True
    for screen_name in screen_nameToExtract:
        success = returnTweetsMultiple(screen_name,"all") and success

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

    # Saving the user
    success = saveUser(userInfo)

    return render(request,'getUser.html',locals())
