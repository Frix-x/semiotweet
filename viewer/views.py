#-*- coding: utf-8 -*-
from datetime import datetime
from django.http import HttpResponse,Http404
from django.shortcuts import render,redirect
from .models import Tweet,User
import extraction

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
