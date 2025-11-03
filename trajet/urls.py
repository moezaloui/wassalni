from django.contrib import admin
from django.urls import path, include
from . import views  # Assurez-vous que 'views' est importé

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),

    path('liste/', views.trajets_by_conducteur, name='list'),

    path('create/', views.ajouter_trajet, name='ajouter_trajet'),
    path('update/<int:pk>/', views.trajet_update, name='trajet_update'),
    path('delete/<int:pk>/', views.trajet_delete, name='trajet_delete'),
    path('reservations/', include('reserver.urls')),

    ]
