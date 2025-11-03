from django.shortcuts import render, redirect, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Trajet
from conducteur.models import Conducteur
from passager.models import Passager
from voiture.models import Vehicule

import random
import string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from conducteur.models import Conducteur
from trajet.models import Trajet

# Page d'accueil
def home(request):
    return render(request, 'home.html')


# Page de recherche de trajets
def search(request):
    # Récupérer les paramètres de recherche
    ville_depart = request.GET.get('ville_depart', '')
    ville_arrivee = request.GET.get('ville_arrivee', '')
    date_depart = request.GET.get('date_depart', '')
    nbr_passagers = request.GET.get('nbr_passagers', 1)
    
    # Initialiser les trajets
    trajets = Trajet.objects.select_related('conducteur', 'voiture').all()
    print(list(trajets))
    
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
    print("context ", context)
    
    return render(request, 'search.html', context)

def trajets_by_conducteur(request):
    conducteur_id = request.session['user_id']
    conducteur = get_object_or_404(Conducteur, utilisateur=conducteur_id)
    trajets = Trajet.objects.filter(conducteur=conducteur).order_by('-dateHeureDepart')

    context = {
        'conducteur': conducteur,
        'trajets': trajets
    }
    print("context", context)
    return render(request, 'conducteur/mes-trajet.html', context)

def ajouter_trajet(request):
    conducteur_id = request.session.get('user_id')
    conducteur = get_object_or_404(Conducteur, utilisateur=conducteur_id)

    # 🔹 Récupérer toutes les voitures de ce conducteur
    voitures = Vehicule.objects.filter(conducteur=conducteur)

    if request.method == 'POST':
        villeDep = request.POST.get('villeDep')
        villeArr = request.POST.get('villeArr')
        prix = request.POST.get('prix')
        nbrPlaceTotal = request.POST.get('nbrPlaceTotal')
        nbrPlaceTotal = request.POST.get('nbrPlaceTotal')
        voiture = request.POST.get('voiture')
        print("dis ", voiture)
        bagages = request.POST.get('bagages') == 'on'
        animaux = request.POST.get('animaux') == 'on'
        fumeur = request.POST.get('fumeur') == 'on'
        dateHeureDepart = request.POST.get('dateHeureDepart')
        dateHeureArrivee = request.POST.get('dateHeureArrivee')

        # 🔹 Récupérer la voiture choisie
        voiture_id = request.POST.get('voiture')
        voiture = get_object_or_404(Vehicule, pk=voiture_id)

        Trajet.objects.create(
            villeDep=villeDep,
            villeArr=villeArr,
            prix=prix,
            nbrPlaceDispo=nbrPlaceTotal,
            bagages=bagages,
            animaux=animaux,
            fumeur=fumeur,
            voiture=voiture,
            conducteur=conducteur,
            dateHeureDepart=dateHeureDepart,
            dateHeureArrivee=dateHeureArrivee,
        )

        messages.success(request, "Trajet ajouté avec succès !")
        return redirect('list')

    return render(request, 'conducteur/ajouter_trajet.html', {'voitures': voitures})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from trajet.models import Trajet
from conducteur.models import Conducteur
from voiture.models import Vehicule

def trajet_update(request, pk):
    trajet = get_object_or_404(Trajet, pk=pk)

    if request.method == 'POST':
        # Récupération des données du formulaire
        villeDep = request.POST.get('villeDep')
        villeArr = request.POST.get('villeArr')
        prix = request.POST.get('prix')
        nbrPlaceDispo = request.POST.get('nbrPlaceDispo')
        dateHeureDepart = request.POST.get('dateHeureDepart')
        dateHeureArrivee = request.POST.get('dateHeureArrivee')
        voiture_id = request.POST.get('voiture')  # optionnel

        conducteur_id = request.session.get('user_id')

        # Debug facultatif
        print("==== Données reçues ====")
        print(villeDep, villeArr, prix, nbrPlaceDispo, conducteur_id, dateHeureDepart, dateHeureArrivee, voiture_id)

        # Vérifier les champs obligatoires
        if not all([villeDep, villeArr, prix, nbrPlaceDispo, dateHeureDepart, dateHeureArrivee]):
            messages.error(request, "Tous les champs obligatoires doivent être remplis.")
            return redirect('trajet_update', pk=trajet.pk)

        # Conversion sécurisée
        try:
            nbrPlaceDispo = int(nbrPlaceDispo)
            prix = float(prix)
        except ValueError:
            messages.error(request, "Veuillez entrer des valeurs numériques valides pour le prix et le nombre de places.")
            return redirect('trajet_update', pk=trajet.pk)

        # Vérifier le conducteur
        conducteur = get_object_or_404(Conducteur, utilisateur_id=conducteur_id)

        # Si une voiture est sélectionnée
        voiture = None
        if voiture_id:
            voiture = get_object_or_404(Vehicule, pk=voiture_id)

        # Mise à jour du trajet
        trajet.villeDep = villeDep
        trajet.villeArr = villeArr
        trajet.prix = prix
        trajet.nbrPlaceDispo = nbrPlaceDispo
        trajet.bagages = request.POST.get('bagages') == 'on'
        trajet.animaux = request.POST.get('animaux') == 'on'
        trajet.fumeur = request.POST.get('fumeur') == 'on'
        trajet.dateHeureDepart = dateHeureDepart
        trajet.dateHeureArrivee = dateHeureArrivee
        trajet.conducteur = conducteur
        trajet.voiture = voiture  # ✅ cohérent avec ton modèle
        trajet.save()

        messages.success(request, 'Trajet mis à jour avec succès !')
        return redirect('list')

    # GET → afficher le formulaire de modification
    voitures = Vehicule.objects.filter(conducteur__utilisateur_id=request.session.get('user_id'))
    return render(request, 'conducteur/modifier_trajet.html', {
        'trajet': trajet,
        'voitures': voitures,
    })

def trajet_delete(request, pk):
    trajet = get_object_or_404(Trajet, pk=pk)
    if request.method == 'POST':
        trajet.delete()
        messages.success(request, 'Trajet supprimé avec succès !')
        return redirect('/conducteur/trajet/liste/')
    return render(request, 'conducteur/supprimer_trajet.html', {'trajet': trajet})