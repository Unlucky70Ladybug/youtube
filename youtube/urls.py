# -*- coding: utf-8 -*-
"""
@author: bluec
"""

from django.urls import path
from . import views

urlpatterns = [
    path('index', views.index, name='index'),
    path('',views.user_login,name='Login'),
    path("logout",views.user_logout,name="Logout"),
    path('register', views.AccountRegistration.as_view(), name='register'),
    path("videos",views.videos,name="videos"),
    path("favorites",views.favorites,name="favorites"),
]