from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password

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
            # Récupération des champs communs
            firstName = request.POST.get("firstName")
            lastName = request.POST.get("lastName")
            adresse = request.POST.get("adresse")
            phone = request.POST.get("phone")
            email = request.POST.get("email")
            print("email", email)
            password = request.POST.get("password")
            role = request.POST.get("user_type")  # 'conducteur' ou 'passager'

            # Création de l'utilisateur
            user = Utilisateur.objects.create(
                firstName=firstName,
                lastName=lastName,
                adresse=adresse,
                phone=phone,
                email=email,
                password=make_password(password)
            )

            # Création du profil selon rôle
            if role == "conducteur":
                print("conducteur")
                permisID = request.POST.get("permisID")
                vehiculeMat = request.POST.get("vehiculeMat")
                Conducteur.objects.create(
                    utilisateur=user,
                    permisID=permisID,
                    vehiculeMat=vehiculeMat
                )
            elif role == "passager":                                
                print("passager")
                Passager.objects.create(utilisateur=user)

            messages.success(request, "Compte créé avec succès !")
            return redirect("login")

        except IntegrityError:
            messages.error(request, "Cet email existe déjà.")
        except Exception as e:
            messages.error(request, "Erreur lors de l'inscription")
            import traceback
            print(traceback.format_exc())


    return render(request, "register.html")












def login_views(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        print("DATA =>", email, password)

        try:
            user = Utilisateur.objects.get(email=email)

            if check_password(password, user.password):
                print("logged  #######")

                # 🔹 Infos communes à tous les rôles
                request.session['user_id'] = user.id
                request.session['user_name'] = f"{user.firstName} {user.lastName}"
                request.session['user_role'] = None
                request.session['conducteur_id'] = None
                request.session['passager_id'] = None

                # 🔹 Vérifie le rôle et stocke l'ID spécifique
                if hasattr(user, 'conducteur_profile'):
                    conducteur = user.conducteur_profile
                    request.session['user_role'] = 'conducteur'
                    request.session['conducteur_id'] = conducteur.id
                    redirect_url = '/conducteur/home'
                elif hasattr(user, 'passager_profile'):
                    passager = user.passager_profile
                    request.session['user_role'] = 'passager'
                    request.session['passager_id'] = passager.id
                    redirect_url = '/passager'
                else:
                    messages.error(request, "Aucun profil conducteur ou passager associé à ce compte.")
                    return redirect('login')

                messages.success(request, f"Bienvenue {user.firstName} !")
                print("SESSION =>", dict(request.session))
                return redirect(redirect_url)

            else:
                messages.error(request, "Mot de passe incorrect !")

        except Utilisateur.DoesNotExist:
            messages.error(request, "Email non trouvé !")

    return render(request, "login.html")


# ====== Déconnexion ======
def logout_view(request):
    if 'user_id' in request.session:
        request.session.flush()  # supprime toutes les données de session
        messages.success(request, "Vous êtes maintenant déconnecté.")
    return redirect('login')
    
# ====== Profil ======
def profile(request):
    print("prof")
    user_id = request.session.get('user_id')
    if user_id:
        user = Utilisateur.objects.get(id=user_id)
        return render(request, 'mon-espace.html', {'user': user})
    return redirect('login')


# ====== Édition profil ======
def profile_edite(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = Utilisateur.objects.get(id=user_id)

    if request.method == "POST":
        user.firstName = request.POST.get("firstName")
        user.lastName = request.POST.get("lastName")
        user.adresse = request.POST.get("adresse")
        user.phone = request.POST.get("phone")
        user.email = request.POST.get("email")
        user.save()
        messages.success(request, "Profil mis à jour !")
        return redirect("profile")

    return render(request, 'edite-mon-espace.html', {'user': user})


# ====== Changer mot de passe ======
def change_password(request):
    user_id = request.session.get('user_id')
    user = Utilisateur.objects.get(id=user_id)

    if request.method == 'POST':
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password == confirm_password:
            user.password = make_password(new_password)
            user.save()
            messages.success(request, "Mot de passe mis à jour avec succès !")
            return redirect("profile")
        else:
            messages.error(request, "Les mots de passe ne correspondent pas.")

    return render(request, "change-password.html")


    