
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Passager
from trajet.models import Trajet, Reservation
from django.contrib.auth.decorators import login_required


def home(request):
   # user_id = request.session.get('user_id')  # Récupère l'ID de session (ou None)

    return render(request, 'home.html')
  

























