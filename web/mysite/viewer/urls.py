from django.urls import path

from . import views
from . import manager

urlpatterns = [
    path('', views.index, name='index'),
    #path('tes', manager.index, name='tes')
]