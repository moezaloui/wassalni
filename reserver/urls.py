# reservations/urls.py
from django.urls import path, include
from . import views

urlpatterns = [
    path('mes-reservations', views.mes_reservations, name='mes_reservations'),
    path('creer/<int:trajet_id>/', views.creer_reservation, name='reserver_trajet'),
    path('statut/<int:reservation_id>/', views.modifier_statut_reservation, name='modifier_statut_reservation'),
    path('annuler/<int:reservation_id>/', views.annuler_reservation, name='annuler_reservation'),
    path('mes-demandes/', views.mes_demandes_reservations, name='mes_demandes_reservations'),

]
