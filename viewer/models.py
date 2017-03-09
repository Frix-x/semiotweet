from __future__ import unicode_literals

from builtins import str
from django.db import models

# Create your models here.

#NOTE : for date processing :
#https://docs.djangoproject.com/fr/1.10/ref/models/database-functions/#datetimefield-extracts

class Tweet(models.Model):
    """Tweet Class : we are only using the usefullFields (see Tweets.py)"""

    id = models.IntegerField(primary_key=True)
    user_id = models.ForeignKey('User')
    text = models.TextField(null=False)
    created_at = models.DateTimeField()
    is_quote_status = models.BooleanField(default=False)
    in_reply_to_status_id = models.IntegerField(null=True,default=-1)
    favorite_count = models.IntegerField(default=-1)
    retweet_count = models.IntegerField(default=-1)
    source = models.URLField(max_length=300,null=True)
    in_reply_to_user_id = models.IntegerField(null=True)
    lang = models.CharField(null=True,max_length=5)

    def __str__(self):
        return "Tweet of "+ str(self.user_id) +' ('+self.created_at+') : '+self.text

class User(models.Model):
    """User class"""

    id = models.IntegerField(primary_key=True)
    name = models.CharField(null=True,max_length=30)
    screen_name = models.CharField(null=True,max_length=30)
    created_at = models.DateTimeField()
    contributors_enabled = models.BooleanField(default=False)
    verified = models.BooleanField(default=True)

    def __str__(self):
        return "User : "+ self.name +' (@'+self.screen_name+' ; id :'+str(self.id)+')'


class Word(models.Model):
    """Word class"""

    word = models.CharField(primary_key=True,max_length=100)
    semanticField = models.CharField(null=False,max_length=100)
    occurencesNum = models.ManyToManyField(User, through='Occurences')

    def __str__(self):
        return self.word + " (semantic field : "+ self.semanticField +")"

class Occurences(models.Model):
    """Occurences class"""
    occurencesNum = models.IntegerField(default=0)
    user_id = models.ForeignKey(User)
    word = models.ForeignKey(Word)

    def __str__(self):
        return "{0} was said {1} times by the user of id : {2}".format(self.word, self.occurencesNum, self.user_id)
