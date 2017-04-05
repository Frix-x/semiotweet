from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^user/?$',views.user,name='user'),
    url(r'^user/exist?$',views.userExist,name='userExist'),
    url(r'^user/sources/?$',views.sources,name='sources'),
    url(r'^user/nbtweets/?$',views.nbTweets,name='nbTweets'),
    url(r'^user/hours/?$',views.hours,name='hours'),
#    url(r'^getData/?$',views.getData,name='getData'),
    url(r'^user/wordcount/?$',views.wordCount,name='wordCount'),
    url(r'^user/lemmecount/?$',views.lemmeCount,name='lemmeCount'),
    url(r'^tweet/last/?$',views.lastTweet,name='lastTweet'),
    url(r'^nlp/lda/topics/?$',views.ldaTopics,name='ldaTopics'),
    url(r'(?P<typed>.+)$',views.handler404,name='handler404')
]
