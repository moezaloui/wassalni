from django.urls import path
from . import views  # Ensure views.py exists in utilisateur app


urlpatterns = [
    path('login', views.login_views, name='login'),           # page login
    path('register/', views.register_views, name='register'),
    path('logout/', views.logout_view, name='logout'),
    # path('profile/', views.profile, name='profile'),
    # path('profile/edite/', views.profile_edite, name='edite_profile'),
]