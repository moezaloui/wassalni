from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password, check_password

from utilisateur.models import Utilisateur
from conducteur.models import Conducteur
from passager.models import Passager


# ====== Home ======
def home(request):
    return render(request, 'home.html')


# ====== Inscription ======
def register_views(request):
    if request.method == "POST":
        try:
            # Champs communs
            firstName = request.POST.get("firstName")
            lastName = request.POST.get("lastName")
            adresse = request.POST.get("adresse")
            phone = request.POST.get("phone")
            email = request.POST.get("email")
            password = request.POST.get("password")
            role = request.POST.get("user_type")

            # Création utilisateur
            user = Utilisateur.objects.create(
                firstName=firstName,
                lastName=lastName,
                adresse=adresse,
                phone=phone,
                email=email,
                password=make_password(password)
            )

            # Création profil
            if role == "conducteur":
                permisID = request.POST.get("permisID")
                vehiculeMat = request.POST.get("vehiculeMat")
                Conducteur.objects.create(
                    utilisateur=user,
                    permisID=permisID,
                    vehiculeMat=vehiculeMat
                )
            elif role == "passager":
                Passager.objects.create(utilisateur=user)

            messages.success(request, "Compte créé avec succès !")
            return redirect("login")

        except IntegrityError:
            messages.error(request, "Cet email existe déjà.")
        except Exception:
            messages.error(request, "Erreur lors de l'inscription.")
            import traceback
            print(traceback.format_exc())

    return render(request, "register.html")


# ====== Login ======
def login_views(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = Utilisateur.objects.get(email=email)

            if check_password(password, user.password):

                # Reset session
                request.session.flush()

                request.session['user_id'] = user.id
                request.session['user_name'] = f"{user.firstName} {user.lastName}"
                request.session['user_role'] = None

                # Détection rôle
                if hasattr(user, 'conducteur_profile'):
                    request.session['user_role'] = 'conducteur'
                    request.session['conducteur_id'] = user.conducteur_profile.id
                    redirect_url = '/conducteur/home'

                elif hasattr(user, 'passager_profile'):
                    request.session['user_role'] = 'passager'
                    request.session['passager_id'] = user.passager_profile.id
                    redirect_url = '/passager'

                else:
                    messages.error(request, "Aucun profil conducteur ou passager n'est associé.")
                    return redirect('login')

                messages.success(request, f"Bienvenue {user.firstName} !")
                return redirect(redirect_url)

            else:
                messages.error(request, "Mot de passe incorrect !")

        except Utilisateur.DoesNotExist:
            messages.error(request, "Email non trouvé.")

    return render(request, "login.html")


# ====== Logout ======
def logout_view(request):
    request.session.flush()
    messages.success(request, "Vous êtes maintenant déconnecté.")
    return redirect('')


# ====== Profil ======
def profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    try:
        user = Utilisateur.objects.get(id=user_id)
    except Utilisateur.DoesNotExist:
        return redirect('login')

    return render(request, 'mon-espace.html', {'user': user})


# ====== Édition du profil ======
def profile_edite(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    try:
        user = Utilisateur.objects.get(id=user_id)
    except Utilisateur.DoesNotExist:
        messages.error(request, "Utilisateur introuvable.")
        return redirect('login')

    if request.method == "POST":

        # Vérifie email déjà utilisé
        new_email = request.POST.get("email")
        if Utilisateur.objects.filter(email=new_email).exclude(id=user.id).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return render(request, 'mon-espace.html', {'user': user})

        # Mise à jour champs simples
        user.firstName = request.POST.get("firstName")
        user.lastName = request.POST.get("lastName")
        user.adresse = request.POST.get("adresse")
        user.phone = request.POST.get("phone")
        user.email = new_email

        # Mot de passe (si modifié)
        new_password = request.POST.get("password")
        if new_password and new_password.strip() != "":
            if len(new_password) < 8:
                messages.error(request, "Le mot de passe doit faire au moins 8 caractères.")
                return render(request, 'mon-espace.html', {'user': user})
            user.password = make_password(new_password)

        user.save()
        messages.success(request, "Profil mis à jour avec succès !")
        return redirect("profile")

    return render(request, 'mon-espace.html', {'user': user})


# ====== Changer mot de passe ======
def change_password(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = Utilisateur.objects.get(id=user_id)

    if request.method == 'POST':
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # Vérifie ancien mot de passe
        if not check_password(current_password, user.password):
            messages.error(request, "L'ancien mot de passe est incorrect.")
            return redirect("change_password")

        if new_password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect("change_password")

        if len(new_password) < 8:
            messages.error(request, "Le mot de passe doit contenir au moins 8 caractères.")
            return redirect("change_password")

        user.password = make_password(new_password)
        user.save()
        messages.success(request, "Mot de passe mis à jour avec succès !")
        return redirect("profile")

    return render(request, "change-password.html")
