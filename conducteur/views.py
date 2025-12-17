from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from trajet.models import Trajet

from conducteur.models import Conducteur
from passager.models import Passager   
from utilisateur.models import Utilisateur 
from django.contrib.auth.decorators import login_required


def home(request):
    user_id = request.session.get('user_id')  # Récupère l'ID de session (ou None)

    if user_id:  
        return render(request, 'conducteur/acceuil.html')
    else:
        # Redirige vers la page de login si non connecté
        messages.success(request, "404 Il faut connecter d'abord.")
        return redirect('/login')

from django.shortcuts import render, redirect
from django.contrib import messages





















