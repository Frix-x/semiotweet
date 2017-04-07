from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',views.home,name='home'),
    url(r'^user/?$',views.user,name='user'),
    url(r'^general/?$',views.general,name='general'),
    url(r'^methodology/?$',views.methodology,name='methodology'),
    url(r'^comparison/?$',views.comparison,name='comparison'),
#    url(r'^network/?$',views.displayNetwork,name='displayNetwork'),
    url(r'(?P<typed>.+)$',views.handler404,name='handler404')
]
