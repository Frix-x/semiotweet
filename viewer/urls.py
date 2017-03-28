from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',views.home,name='home'),
    url(r'^displayInfo/(?P<screen_name>.+)$',views.displayInfo,name='displayInfo'),
#    url(r'^getData/$',views.getData,name='getData'),
    url(r'^generalOverview/$',views.generalOverview,name='generalOverview'),
    url(r'^displayNetwork/$',views.displayNetwork,name='displayNetwork'),
    url(r'^comparison$',views.comparison,name='comparison'),
    url(r'^comparison?candidat1=(?P<candidat1>)&candidat2=(?P<candidat2>)$',views.comparison,name='compare2candidates'),
    url(r'(?P<typed>.+)$',views.handler404,name='handler404')
]
