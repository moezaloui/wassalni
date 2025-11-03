from django.contrib import admin
from django.urls import path, include
from . import views  # Assurez-vous que 'views' est importé

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('trajet/', include('trajet.urls')),
    path('reservations/', include('reserver.urls')),

#    path('search/', views.search, name='search'),  # La vue par défaut, page d'accueil
]
