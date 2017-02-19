from __future__ import unicode_literals

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
    in_reply_to_status_id = models.IntegerField(default=-1)
    favorite_count = models.IntegerField(default=-1)
    retweet_count = models.IntegerField(default=-1)
    source = models.URLField(max_length=300,null=True)
    in_reply_to_user_id = models.IntegerField(null=True)
    lang = models.CharField(null=True,max_length=5)

    def __str__(self):
        return "Tweet of "+ self.user_id +' ('+self.created_at+') : '+self.text

class User(models.Model):
    """User class"""

    id = models.IntegerField(primary_key=True)
    name = models.CharField(null=True,max_length=30)
    screen_name = models.CharField(null=True,max_length=30)
    created_at = models.DateTimeField()
    contributors_enabled = models.BooleanField(default=False)
    verified = models.BooleanField(default=True)

    def __str__(self):
        return "User : "+ self.name +' (@'+self.screen_name+' ; if :'+self.id+')'