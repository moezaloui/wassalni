from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from utilisateur.models import Utilisateur
from .models import Notification

def send_notification(user: Utilisateur, title: str, message: str, notif_type: str):
    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        type=notif_type
    )
    send_mail(
        subject=title,
        message=message,
        from_email=None,  
        recipient_list=[user.email],
        fail_silently=False
    )

@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications/list.html', {'notifications': notifications})

@login_required
def mark_as_read(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.is_read = True
    notif.save()
    return redirect('notifications:list')

@login_required
def example_send_notification(request):
    user = request.user
    send_notification(
        user,
        "Test Notification",
        "Ceci est un message de test pour ta notification.",
        "test"
    )
    return render(request, 'notifications/example.html')
