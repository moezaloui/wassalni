from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Reservation
from trajet.models import Trajet
from conducteur.models import Conducteur
from passager.models import Passager

def mes_reservations(request):
    passager_id = request.session.get('user_id')
    passager = get_object_or_404(Passager, utilisateur=passager_id)
    reservations = Reservation.objects.filter(passager=passager)
    return render(request, 'passager/mes-reservations.html', {'reservations': reservations})

def creer_reservation(request, trajet_id):
    passager_id = request.session.get('user_id')
    passager = get_object_or_404(Passager, utilisateur=passager_id)
    trajet = get_object_or_404(Trajet, pk=trajet_id)

    # Vérifier si le passager a déjà réservé ce trajet
    if Reservation.objects.filter(passager=passager, trajet=trajet).exists():
        messages.error(request, "Vous avez déjà réservé ce trajet.")
        return redirect('search')

    if request.method == 'POST':
        try:
            nbr_place_reserve = int(request.POST.get('nbr_place_reserve'))
        except (ValueError, TypeError):
            messages.error(request, "Veuillez entrer un nombre valide de places à réserver.")
            return redirect('reserver_trajet', trajet_id=trajet.id)

        if nbr_place_reserve <= 0:
            messages.error(request, "Le nombre de places doit être supérieur à 0.")
            return redirect('reserver_trajet', trajet_id=trajet.id)

        if nbr_place_reserve > trajet.nbrPlaceDispo:
            messages.error(request, f"Il ne reste que {trajet.nbrPlaceDispo} place(s) disponible(s).")
            return redirect('reserver_trajet', trajet_id=trajet.id)

        # Créer la réservation avec statut "en attente"
        Reservation.objects.create(
            passager=passager,
            trajet=trajet,
            nbr_place_reserve=nbr_place_reserve,
            statut='en_attente'
        )
        messages.success(request, "Votre réservation a été créée et est en attente de confirmation du conducteur.")
        return redirect('mes_reservations')

    return render(request, 'passager/reserver.html', {'trajet': trajet})


def creer_reservationS7i7A(request, trajet_id):
    passager_id = request.session.get('user_id')
    passager = get_object_or_404(Passager, utilisateur=passager_id)
    trajet = get_object_or_404(Trajet, pk=trajet_id)

    if request.method == 'POST':
        try:
            nbr_place_reserve = int(request.POST.get('nbr_place_reserve'))
        except (ValueError, TypeError):
            messages.error(request, "Veuillez entrer un nombre valide de places à réserver.")
            return redirect('reserver_trajet', trajet_id=trajet.id)

        if nbr_place_reserve <= 0:
            messages.error(request, "Le nombre de places doit être supérieur à 0.")
            return redirect('reserver_trajet', trajet_id=trajet.id)

        if nbr_place_reserve > trajet.nbrPlaceDispo:
            messages.error(request, f"Il ne reste que {trajet.nbrPlaceDispo} place(s) disponible(s).")
            return redirect('reserver_trajet', trajet_id=trajet.id)

        # Créer la réservation avec statut "en attente"
        Reservation.objects.create(
            passager=passager,
            trajet=trajet,
            nbr_place_reserve=nbr_place_reserve,
            statut='en_attente'
        )
        messages.success(request, "Votre réservation a été créée et est en attente de confirmation du conducteur.")
        return redirect('mes_reservations')

    return render(request, 'passager/reserver.html', {'trajet': trajet})

def mes_demandes_reservationsX(request):
    
    conducteur_id = request.session.get('user_id')
    if not conducteur_id:
        messages.error(request, "Vous devez être connecté en tant que conducteur.")
        return redirect('login')
    
    # Récupération du conducteur connecté
    conducteur = get_object_or_404(Conducteur, utilisateur=conducteur_id)

    # Récupération des trajets proposés par ce conducteur
    trajets = Trajet.objects.filter(conducteur=conducteur)

    # Récupération de toutes les réservations associées à ces trajets
    reservations = Reservation.objects.filter(trajet__in=trajets).select_related('trajet', 'passager')

    context = {
        'reservations': reservations,
        'trajets': trajets,
    }
    return render(request, 'conducteur/mes-demandes-reservations.html', context)


def mes_demandes_reservations(request):
    """Affiche et permet au conducteur de gérer les réservations reçues"""
    
    conducteur_id = request.session.get('user_id')
    if not conducteur_id:
        messages.error(request, "Vous devez être connecté en tant que conducteur.")
        return redirect('login')

    conducteur = get_object_or_404(Conducteur, utilisateur=conducteur_id)
    trajets = Trajet.objects.filter(conducteur=conducteur)
    reservations = Reservation.objects.filter(trajet__in=trajets).select_related('trajet', 'passager')

    # --- GESTION DU FORMULAIRE DE CHANGEMENT DE STATUT ---
    if request.method == 'POST':
        reservation_id = request.POST.get('reservation_id')
        statut = request.POST.get('statut')

        if reservation_id and statut in ['accepte', 'refuse']:
            reservation = get_object_or_404(Reservation, pk=reservation_id, trajet__conducteur=conducteur)
            
            # Si accepté, diminuer le nombre de places
            if statut == 'accepte' and reservation.statut != 'accepte':
                if reservation.nbr_place_reserve <= reservation.trajet.nbrPlaceDispo:
                    reservation.trajet.nbrPlaceDispo -= reservation.nbr_place_reserve
                    reservation.trajet.save()
                else:
                    messages.error(request, "Pas assez de places disponibles.")
                    return redirect('mes_demandes_reservations')
            
            # Si refusé ou re-changement, restaurer les places
            elif reservation.statut == 'accepte' and statut == 'refuse':
                reservation.trajet.nbrPlaceDispo += reservation.nbr_place_reserve
                reservation.trajet.save()

            reservation.statut = statut
            reservation.save()
            messages.success(request, f"Réservation {statut} avec succès.")
            return redirect('mes_demandes_reservations')

    context = {
        'reservations': reservations,
    }
    return render(request, 'conducteur/mes-demandes-reservations.html', context)

def modifier_statut_reservation(request, reservation_id):
    """Permet au conducteur d'accepter ou refuser une réservation"""
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    trajet = reservation.trajet

    # Vérifier que le conducteur est bien le conducteur du trajet
    conducteur_id = request.session.get('user_id')
    if trajet.conducteur.id != conducteur_id:
        messages.error(request, "Vous n'êtes pas autorisé à modifier cette réservation.")
        return redirect('mes_trajets')  # redirection vers liste des trajets du conducteur

    if request.method == 'POST':
        statut = request.POST.get('statut')
        if statut not in ['accepte', 'refuse']:
            messages.error(request, "Statut invalide.")
            return redirect('modifier_statut_reservation', reservation_id=reservation.id)

        reservation.statut = statut
        reservation.save()

        # Si accepté, mettre à jour le nombre de places disponibles
        if statut == 'accepte':
            trajet.nbrPlaceDispo -= reservation.nbr_place_reserve
            trajet.save()

        messages.success(request, f"Réservation {statut} avec succès.")
        return redirect('mes_trajets')

    return render(request, 'reservations/modifier_statut_reservation.html', {'reservation': reservation})


def annuler_reservation(request, reservation_id):
    """Permet au passager d'annuler sa réservation"""
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    passager_id = request.session.get('user_id')

    if reservation.passager.id != passager_id:
        messages.error(request, "Vous n'êtes pas autorisé à annuler cette réservation.")
        return redirect('mes_reservations')

    if request.method == 'POST':
        # Si la réservation était acceptée, remettre les places disponibles
        if reservation.statut == 'accepte':
            reservation.trajet.nbrPlaceDispo += reservation.nbr_place_reserve
            reservation.trajet.save()

        reservation.delete()
        messages.success(request, "Réservation annulée avec succès.")
        return redirect('mes_reservations')

    return render(request, 'reservations/annuler_reservation.html', {'reservation': reservation})
