from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',views.home,name='home'),
    url(r'^displayInfo/(?P<screen_name>.+)$',views.displayInfo,name='displayInfo'),
    url(r'^getTweets/(?P<screen_name>.+)/(?P<nbTweetToExtract>.+)$',views.getTweets,name='getTweets'),
    url(r'^getUser/(?P<screen_name>.+)/$',views.getUser,name='getUser')
]
