from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',views.home,name='home'),
    url(r'^displayInfo/(?P<screen_name>.+)$',views.displayInfo,name='displayInfo'),
    url(r'^getLatestTweets/$',views.getLatestTweets,name='getLatestTweets'),
    url(r'^getUser/(?P<screen_name>.+)/$',views.getUser,name='getUser'),
    url(r'^getAllTweets/$',views.getAllTweets,name='getAllTweets')
]
