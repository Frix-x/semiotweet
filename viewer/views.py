#-*- coding: utf-8 -*-
from datetime import datetime
from django.http import HttpResponse,Http404
from django.shortcuts import render,redirect
from .models import Tweet,User
from extraction import *
import random
import string
import time

#TODO
def displayAll(request,screen_name):
    """Display all the tweets for a user"""
    # idUser = User.objects.get(screen_name=screen_name)
    # tweetList = Tweet.objects.all()
    return HttpResponse(screen_name)
    return render(request,'displayAll.html',locals())

#TODO :
def getTweets(request,screen_name,nbTweetToExtract):
    """Get the last nbTweetToExtract from user 'screen_name'"""
    tweets = returnTweet(screen_name,credentials,int(nbTweetToExtract))
    success = True
    if not(tweets): #If the user doesn't exist
        success = False

    return render(request,'getTweets.html',locals())

#TODO :
def getUser(request,screen_name):
    userInfo = returnProfile(screen_name,credentials)
    success = True
    if not(userInfo): #If the user doesn't exist
        success = False
        return render(request,'getUser.html',locals())

    newUser = User()
    remainingFields = [k for k,v in userInfo.items()]
    string = ""
    for i in remainingFields:
        string += i+":"+str(userInfo[i])+"<br/>"

    newUser.id = userInfo['id']
    newUser.name = userInfo['name']
    newUser.screen_name = userInfo['screen_name']
    newUser.created_at = userInfo['created_at']
    newUser.contributors_enabled = userInfo['contributors_enabled']
    newUser.verified = userInfo['verified']

    # Formating the date
    newUser.created_at = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(newUser.created_at,'%a %b %d %H:%M:%S +0000 %Y'))
    # newUser.save()
    # try:
    #     newUser.save()
    # except BaseException:
    #     string = "Utilisateur deja inscrit <br/>"+ string
    # return HttpResponse(string)
    return render(request,'getUser.html',locals())
