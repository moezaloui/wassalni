
from django.contrib import admin
from django.shortcuts import render, redirect

from django.urls import path, include
from . import views  # Assurez-vous que 'views' est importé

urlpatterns = [
    path('', include('utilisateur.urls')), 
    path('passager/', include('passager.urls')),
    path('conducteur/', include('conducteur.urls')),
    path('admin/', admin.site.urls),

    
]