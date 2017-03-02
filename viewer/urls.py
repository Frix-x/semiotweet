from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',views.home,name='home'),
    url(r'^displayInfo/(?P<screen_name>.+)$',views.displayInfo,name='displayInfo'),
    url(r'^getUser/(?P<screen_name>.+)/$',views.getUser,name='getUser'),
    url(r'^getTweets/(?P<option>.+)/$',views.getTweets,name='getTweets'),
    url(r'^getWords/$',views.getWords,name='getWords'),
    url(r'^displayNetwork/$',views.displayNetwork,name='displayNetwork'),
]
