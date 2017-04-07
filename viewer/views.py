#-*- coding: utf-8 -*-
from __future__ import print_function, absolute_import # For Py2 retrocompatibility
from django.http import HttpResponse,Http404
from django.shortcuts import render,redirect

from api.models import User

import requests
import json

def handler404(request,typed):
    """A basic 404 error handler"""
    response = render(request,'404.html', {"typed":typed})
    response.status_code = 404
    return response

def home(request):
    """Redirect to the home page : global statistics"""
    return render(request,'home.html',{})

def general(request):
    """Redirect to the words page : analysis around words used by politics"""
    return render(request,'generalOverview.html',{})

def methodology(request):
    """Redirects to the methodology page"""
    return render(request,'methodology.html',{})

def comparison(request):
    """Redirect to the comparison form page : compare two politics"""
    candidat1 = request.GET.get("candidat1", "")
    candidat2 = request.GET.get("candidat2", "")
    if candidat1 == "" or candidat2 == "":
        return render(request,'comparison.html', {})

def user(request):
    """Display all the tweets for a user
    Requests the Twitter API directly and search for the most common words"""
    userId = request.GET.get("id", "")
    return render(request,'displayInfo.html',{"userId":userId})

def displayNetwork(request):
    """Display a force network with users linked to their matching keywords"""
    return render(request,'displayNetwork.html',{})
