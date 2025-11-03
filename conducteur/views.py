
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from trajet.models import Trajet

from conducteur.models import Conducteur        # uniquement les modèles de cette app
from passager.models import Passager   # importer depuis passager
from utilisateur.models import Utilisateur  #
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

def login_view(request):
    # Si déjà connecté, redirection
    if request.session.get('user_id'):
        messages.info(request, 'Vous êtes déjà connecté.')
        return redirect('home')

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        password = request.POST.get('password')

        try:
            user = Utilisateur.objects.get(userId=user_id)

            # ⚠️ En production, il faut utiliser make_password/check_password (ici simplifié)
            if user.password == password:
                # Authentification réussie
                request.session['user_id'] = user.id

                # 🔍 Vérifier s’il s’agit d’un conducteur ou d’un passager
                role = None
                if hasattr(user, 'conducteur_profile'):
                    role = 'conducteur'
                elif hasattr(user, 'passager_profile'):
                    role = 'passager'
                else:
                    role = 'utilisateur'

                # Stocker le rôle dans la session
                request.session['role'] = role

                messages.success(request, f"Bienvenue {user.firstName}! Vous êtes connecté en tant que {role}.")
                return redirect('home')

            else:
                messages.error(request, 'Mot de passe incorrect.')

        except Utilisateur.DoesNotExist:
            messages.error(request, 'Identifiant utilisateur introuvable.')

    return render(request, 'login.html')


def view_space(request):
    user_id = request.session.get('user_id')  # Récupère l'ID de session (ou None)

    if user_id:  # Si connecté
        user = Utilisateur.objects.get(id=user_id)
        print("Mon espace =>", user)
        return render(request, 'mon-espace.html', {'user': user})
    else:
        # Redirige vers la page de login si non connecté
        messages.success(request, "404 Il faut connecter d'abord.")
        return redirect('/login')



def search(request):
    # Récupérer les paramètres de recherche
    ville_depart = request.GET.get('ville_depart', '')
    ville_arrivee = request.GET.get('ville_arrivee', '')
    date_depart = request.GET.get('date_depart', '')
    nbr_passagers = request.GET.get('nbr_passagers', 1)
    
    # Initialiser les trajets
    trajets = Trajet.objects.all()
    
    # Appliquer les filtres si des paramètres sont fournis
    if ville_depart:
        trajets = trajets.filter(villeDep__icontains=ville_depart)
    if ville_arrivee:
        trajets = trajets.filter(villeArr__icontains=ville_arrivee)
    if date_depart:
        trajets = trajets.filter(dateHeureDepart__date=date_depart)
    
    # Filtrer par places disponibles
    try:
        nbr_passagers = int(nbr_passagers)
        trajets = trajets.filter(nbrPlaceDispo__gte=nbr_passagers)
    except (ValueError, TypeError):
        pass
    
    # Contexte pour le template
    context = {
        'trajets': trajets,
        'ville_depart': ville_depart,
        'ville_arrivee': ville_arrivee,
        'date_depart': date_depart,
        'nbr_passagers': nbr_passagers,
        'nombre_resultats': trajets.count()
    }
    
    return render(request, 'search.html', context)

def logout_view(request):
    request.session.flush()
    return redirect('/login')



















