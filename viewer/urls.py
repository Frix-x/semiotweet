from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',views.home,name='home'),
    url(r'(?P<typed>.+)$',views.handler404,name='handler404')
]
