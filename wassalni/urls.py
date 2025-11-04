
from django.contrib import admin
from django.urls import path, include
from . import views  # Assurez-vous que 'views' est importé

urlpatterns = [
    
    path('', lambda request: redirect('/user/login')),  
    path('passager/', include('passager.urls')),
    path('conducteur/', include('conducteur.urls')),
    path('admin/', admin.site.urls),

    
]