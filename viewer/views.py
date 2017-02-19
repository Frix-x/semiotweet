#-*- coding: utf-8 -*-
from datetime import datetime
from django.http import HttpResponse,Http404
from django.shortcuts import render,redirect
from .models import Tweet,User
from extraction import returnProfile,credentials

##
import random
import string

def displayAll(request,screen_name):
    """Display all the tweets for a user"""
    # idUser = User.objects.get(screen_name=screen_name)
    # tweetList = Tweet.objects.all()
    return HttpResponse(screen_name)
    # return render(request,'displayAll.html',locals())

def getTweets(request,screen_name,nbTweetToExtract):

    return HttpResponse(nbTweetToExtract+" tweets to extract from user :"+screen_name)

def getUser(request,screen_name):
    newUser = User()
    userInfo = returnProfile(screen_name,credentials)
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

    #TODO : changing date format
    newUser.save()
    # try:
    #     newUser.save()
    # except BaseException:
    #     string = "Utilisateur deja inscrit <br/>"+ string
    return HttpResponse(string)
