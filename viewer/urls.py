from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^displayAll/(?P<screen_name>.+)$',views.displayAll,name='displayAll'),
    url(r'^getTweets/(?P<screen_name>.+)/(?P<nbTweetToExtract>.+)$',views.getTweets,name='getTweets'),
    url(r'^getUser/(?P<screen_name>.+)/$',views.getUser,name='getUser')
]
