from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notifications_list, name='list'),
    path('mark-as-read/<int:notif_id>/', views.mark_as_read, name='mark_as_read'),
    path('test-send/', views.example_send_notification, name='test_send'),
]
