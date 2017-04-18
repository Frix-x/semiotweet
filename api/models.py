from __future__ import unicode_literals

from builtins import str
from django.db import models

# Create your models here.

#NOTE : for date processing :
#https://docs.djangoproject.com/fr/1.10/ref/models/database-functions/#datetimefield-extracts

class User(models.Model):
    """User class"""

    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(null=True,max_length=30)
    screen_name = models.CharField(null=True,max_length=30)
    created_at = models.DateTimeField()
    contributors_enabled = models.BooleanField(default=False)
    verified = models.BooleanField(default=True)
    description= models.CharField(null=True, max_length=255)
    followers_count = models.IntegerField(default=0)
    profile_image_url = models.CharField(null=True, max_length=255)

    def __str__(self):
        output = "User : "
        if self.name:
            output += self.name

        output += ' ('
        if self.screen_name:
            output += '@'+self.screen_name

        output +=  '; id :'+ str(self.id) + ')'
        return output

class Tweet(models.Model):
    """Tweet Class : we are only using the usefullFields"""

    id = models.BigAutoField(primary_key=True)
    user_id = models.ForeignKey('User')
    text = models.TextField(null=False)
    created_at = models.DateTimeField()
    is_quote_status = models.BooleanField(default=False)
    in_reply_to_status_id = models.BigIntegerField(null=True,default=-1)
    favorite_count = models.IntegerField(default=-1)
    retweet_count = models.IntegerField(default=-1)
    source = models.URLField(max_length=300,null=True)
    in_reply_to_user_id = models.BigIntegerField(null=True)
    lang = models.CharField(null=True,max_length=5)
    tokenArray = models.CharField(null=True,max_length=1000)
    lemmaArray = models.CharField(null=True,max_length=1000)

    def __str__(self):
        output = "Tweet"
        if self.user_id:
            output += " of "+ str(self.user_id)

        if self.created_at:
            output += '; posted at '+str(self.created_at)

        if self.text:
            output += ' : " ' + self.text + ' "'

        return output


class LdaModel(models.Model):
    """LdaModel Class : filled with models of LDA which took time to calculate"""

    id = models.AutoField(primary_key=True)
    user_id = models.BigIntegerField(default=0,null=False) # not a ForeignKey for some "multiple users" computed models
    tweet_id = models.ForeignKey('Tweet')
    ldamodel = models.BinaryField(null=False)

    def __str__(self):
        if (self.user_id):
            return "LdaModel for user "+ str(self.user_id)

        return "General LdaModel"


class semanticWord(models.Model):
    """semanticWord class"""

    word = models.CharField(primary_key=True,max_length=100)
    semanticField = models.CharField(null=False,max_length=10000)
    occurencesNum = models.ManyToManyField(User, through='Occurences')

    def __str__(self):
        return self.word + " (semantic field : "+ self.semanticField +")"

class Occurences(models.Model):
    """Occurences class for user semantic fields storage"""
    occurencesNum = models.IntegerField(default=0)
    user_id = models.ForeignKey(User)
    word = models.ForeignKey(semanticWord)

    def __str__(self):
        return "{0} was said {1} times by the user of id : {2}".format(self.word, self.occurencesNum, self.user_id)
