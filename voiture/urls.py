from django.contrib import admin
from django.urls import path
from . import views  # Assurez-vous que 'views' est importé

from django.urls import path
from . import views

urlpatterns = [
    path('liste/', views.mes_voitures, name='mes_voitures'),
    path('ajouter/', views.ajouter_voiture, name='ajouter_voiture'),
    path('modifier/<int:pk>/', views.modifier_voiture, name='modifier_voiture'),
    path('supprimer/<int:pk>/', views.supprimer_voiture, name='supprimer_voiture'),
]