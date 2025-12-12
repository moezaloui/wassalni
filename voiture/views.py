from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError
from .models import Vehicule
from conducteur.models import Conducteur

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

        # Vérifier si le matricule existe déjà
        if Vehicule.objects.filter(matricule=matricule).exists():
            messages.error(request, f'Une voiture avec le matricule "{matricule}" existe déjà !')
            return render(request, 'conducteur/ajouter_voiture.html', {
                'matricule': matricule,
                'marque': marque,
                'modele': modele,
                'couleur': couleur
            })

        # Validation des champs obligatoires
        if not all([matricule, marque, modele, couleur]):
            messages.error(request, 'Tous les champs sont obligatoires !')
            return render(request, 'conducteur/ajouter_voiture.html', {
                'matricule': matricule,
                'marque': marque,
                'modele': modele,
                'couleur': couleur
            })

        try:
            Vehicule.objects.create(
                matricule=matricule.strip().upper(),  # Nettoyer et mettre en majuscules
                marque=marque.strip(),
                modele=modele.strip(),
                couleur=couleur.strip(),
                conducteur=conducteur
            )
            messages.success(request, 'Véhicule ajouté avec succès !')
            return redirect('mes_voitures')
        
        except IntegrityError:
            messages.error(request, f'Erreur : Le matricule "{matricule}" existe déjà dans la base de données !')
            return render(request, 'conducteur/ajouter_voiture.html', {
                'matricule': matricule,
                'marque': marque,
                'modele': modele,
                'couleur': couleur
            })

    return render(request, 'conducteur/ajouter_voiture.html')

def modifier_voiture(request, pk):
    voiture = get_object_or_404(Vehicule, pk=pk)
    conducteur_id = request.session.get('user_id')
    
    # Vérifier que la voiture appartient au conducteur connecté
    if voiture.conducteur.utilisateur.id != conducteur_id:
        messages.error(request, "Vous n'êtes pas autorisé à modifier cette voiture.")
        return redirect('mes_voitures')

    if request.method == 'POST':
        nouveau_matricule = request.POST.get('matricule')
        marque = request.POST.get('marque')
        modele = request.POST.get('modele')
        couleur = request.POST.get('couleur')

        # Vérifier si le nouveau matricule existe déjà (sauf si c'est le même)
        if nouveau_matricule != voiture.matricule:
            if Vehicule.objects.filter(matricule=nouveau_matricule).exists():
                messages.error(request, f'Une voiture avec le matricule "{nouveau_matricule}" existe déjà !')
                return render(request, 'conducteur/modifier_voiture.html', {
                    'voiture': voiture,
                    'nouveau_matricule': nouveau_matricule,
                    'marque': marque,
                    'modele': modele,
                    'couleur': couleur
                })

        # Validation des champs obligatoires
        if not all([nouveau_matricule, marque, modele, couleur]):
            messages.error(request, 'Tous les champs sont obligatoires !')
            return render(request, 'conducteur/modifier_voiture.html', {'voiture': voiture})

        try:
            voiture.matricule = nouveau_matricule.strip().upper()
            voiture.marque = marque.strip()
            voiture.modele = modele.strip()
            voiture.couleur = couleur.strip()
            voiture.save()
            messages.success(request, 'Véhicule modifié avec succès !')
            return redirect('mes_voitures')
        
        except IntegrityError:
            messages.error(request, f'Erreur : Le matricule "{nouveau_matricule}" existe déjà !')
            return render(request, 'conducteur/modifier_voiture.html', {'voiture': voiture})

    return render(request, 'conducteur/modifier_voiture.html', {'voiture': voiture})

def supprimer_voiture(request, pk):
    voiture = get_object_or_404(Vehicule, pk=pk)
    conducteur_id = request.session.get('user_id')
    
    # Vérifier que la voiture appartient au conducteur connecté
    if voiture.conducteur.utilisateur.id != conducteur_id:
        messages.error(request, "Vous n'êtes pas autorisé à supprimer cette voiture.")
        return redirect('mes_voitures')

    if request.method == 'POST':
        matricule = voiture.matricule
        voiture.delete()
        messages.success(request, f'Véhicule {matricule} supprimé avec succès !')
        return redirect('mes_voitures')

    return render(request, 'conducteur/supprimer_voiture.html', {'voiture': voiture})