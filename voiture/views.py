from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Vehicule
from conducteur.models import Conducteur
from django.contrib.auth.decorators import login_required

def mes_voitures(request):
    conducteur_id = request.session.get('user_id')
    conducteur = get_object_or_404(Conducteur, utilisateur=conducteur_id)
    voitures = Vehicule.objects.filter(conducteur=conducteur)
    return render(request, 'conducteur/mes_voitures.html', {'voitures': voitures})

def ajouter_voiture(request):
    conducteur_id = request.session.get('user_id')
    conducteur = get_object_or_404(Conducteur, utilisateur=conducteur_id)

    if request.method == 'POST':
        matricule = request.POST.get('matricule')
        marque = request.POST.get('marque')
        modele = request.POST.get('modele')
        couleur = request.POST.get('couleur')

        Vehicule.objects.create(
            matricule=matricule,
            marque=marque,
            modele=modele,
            couleur=couleur,
            conducteur=conducteur
        )
        messages.success(request, 'Véhicule ajouté avec succès !')
        return redirect('mes_voitures')

    return render(request, 'conducteur/ajouter_voiture.html')

def modifier_voiture(request, pk):
    voiture = get_object_or_404(Vehicule, pk=pk)

    if request.method == 'POST':
        voiture.matricule = request.POST.get('matricule')
        voiture.marque = request.POST.get('marque')
        voiture.modele = request.POST.get('modele')
        voiture.couleur = request.POST.get('couleur')
        voiture.save()
        messages.success(request, 'Véhicule modifié avec succès !')
        return redirect('mes_voitures')

    return render(request, 'vehicule/modifier_voiture.html', {'voiture': voiture})

def supprimer_voiture(request, pk):
    voiture = get_object_or_404(Vehicule, pk=pk)
    if request.method == 'POST':
        voiture.delete()
        messages.success(request, 'Véhicule supprimé avec succès !')
        return redirect('mes_voitures')

    return render(request, 'vehicule/supprimer_voiture.html', {'voiture': voiture})
