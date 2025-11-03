from django.contrib import admin
from django.urls import path, include
from . import views  # Assurez-vous que 'views' est importé

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.home, name='home'),
    path('trajet/', include('trajet.urls')),
    path('voiture/', include('voiture.urls')),

]
