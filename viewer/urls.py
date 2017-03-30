from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',views.home,name='home'),
    url(r'^displayInfo/(?P<screen_name>.+)$',views.displayInfo,name='displayInfo'),
#    url(r'^getData/$',views.getData,name='getData'),
    url(r'^generalOverview/?$',views.generalOverview,name='generalOverview'),
    url(r'^comparison/?$',views.comparison,name='comparison'),
#    url(r'^displayNetwork/?$',views.displayNetwork,name='displayNetwork'),
    url(r'(?P<typed>.+)$',views.handler404,name='handler404')
]
