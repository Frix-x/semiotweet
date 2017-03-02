from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',views.home,name='home'),
    url(r'^displayInfo/(?P<screen_name>.+)$',views.displayInfo,name='displayInfo'),
    url(r'^getData/$',views.getData,name='getData'),
    url(r'^getWords/$',views.getWords,name='getWords'),
    url(r'^displayNetwork/$',views.displayNetwork,name='displayNetwork'),
]
