from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Reservation
from trajet.models import Trajet
from conducteur.models import Conducteur
from passager.models import Passager
from notifications.views import send_notification

def mes_reservations(request):
    passager_id = request.session.get('user_id')
    passager = get_object_or_404(Passager, utilisateur=passager_id)
    reservations = Reservation.objects.filter(passager=passager)
    return render(request, 'passager/mes-reservations.html', {'reservations': reservations})

def creer_reservation(request, trajet_id):
    passager_id = request.session.get('user_id')
    passager = get_object_or_404(Passager, utilisateur=passager_id)
    trajet = get_object_or_404(Trajet, pk=trajet_id)

    # Vérification si déjà réservé
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

        # Création réservation
        reservation = Reservation.objects.create(
            passager=passager,
            trajet=trajet,
            nbr_place_reserve=nbr_place_reserve,
            statut='en_attente'
        )

        # Notification conducteur
        conducteur_user = trajet.conducteur.utilisateur
        title = "Nouvelle demande de réservation"
        message = (
            f"Le passager {passager.utilisateur.firstName} {passager.utilisateur.lastName} "
            f"a réservé {nbr_place_reserve} place(s) sur votre trajet "
            f"{trajet.villeDep} → {trajet.villeArr}."
        )
        send_notification(conducteur_user, title, message, "nouvelle_reservation")

        messages.success(request, "Votre réservation a été créée et est en attente de confirmation du conducteur.")
        return redirect('mes_reservations')

    return render(request, 'passager/reserver.html', {'trajet': trajet})

def mes_demandes_reservations(request):
    conducteur_id = request.session.get('user_id')
    if not conducteur_id:
        messages.error(request, "Vous devez être connecté en tant que conducteur.")
        return redirect('login')

    conducteur = get_object_or_404(Conducteur, utilisateur=conducteur_id)
    trajets = Trajet.objects.filter(conducteur=conducteur)
    reservations = Reservation.objects.filter(trajet__in=trajets).select_related('trajet', 'passager')

    if request.method == 'POST':
        reservation_id = request.POST.get('reservation_id')
        statut = request.POST.get('statut')

        if reservation_id and statut in ['accepte', 'refuse']:
            reservation = get_object_or_404(Reservation, pk=reservation_id, trajet__conducteur=conducteur)
            
            # Sauvegarder l'ancien statut pour la gestion des places
            ancien_statut = reservation.statut

            # Gestion des places disponibles
            if statut == 'accepte' and ancien_statut != 'accepte':
                # On accepte une réservation qui n'était pas acceptée
                if reservation.nbr_place_reserve <= reservation.trajet.nbrPlaceDispo:
                    reservation.trajet.nbrPlaceDispo -= reservation.nbr_place_reserve
                    reservation.trajet.save()
                else:
                    messages.error(request, "Pas assez de places disponibles.")
                    return redirect('mes_demandes_reservations')

            elif ancien_statut == 'accepte' and statut == 'refuse':
                # On refuse une réservation qui était acceptée -> libérer les places
                reservation.trajet.nbrPlaceDispo += reservation.nbr_place_reserve
                reservation.trajet.save()

            # Mettre à jour le statut
            reservation.statut = statut
            reservation.save()

            # Notification au passager avec email
            passager_user = reservation.passager.utilisateur
            
            if statut == 'accepte':
                title = "Réservation acceptée ✅"
                message = (
                    f"Bonne nouvelle ! Votre réservation pour le trajet "
                    f"{reservation.trajet.villeDep} → {reservation.trajet.villeArr} "
                    f"du {reservation.trajet.dateHeureDepart.strftime('%d/%m/%Y à %H:%M')} "
                    f"a été acceptée par le conducteur.\n\n"
                    f"Nombre de places réservées : {reservation.nbr_place_reserve}\n"
                    f"Prix : {reservation.trajet.prix} DT"
                )
            else:
                title = "Réservation refusée ❌"
                message = (
                    f"Votre réservation pour le trajet "
                    f"{reservation.trajet.villeDep} → {reservation.trajet.villeArr} "
                    f"du {reservation.trajet.dateHeureDepart.strftime('%d/%m/%Y à %H:%M')} "
                    f"a été refusée par le conducteur.\n\n"
                    f"Vous pouvez rechercher d'autres trajets disponibles."
                )
            
            # Envoi de la notification (base de données + email)
            print(f"🔔 Envoi notification à {passager_user.email}: {title}")
            send_notification(passager_user, title, message, "changement_statut")

            messages.success(request, f"Réservation {statut}e avec succès. Le passager a été notifié par email.")
            return redirect('mes_demandes_reservations')

    return render(request, 'conducteur/mes-demandes-reservations.html', {'reservations': reservations})

def annuler_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id)
    passager_id = request.session.get('user_id')

    if reservation.passager.utilisateur.id != passager_id:
        messages.error(request, "Vous n'êtes pas autorisé à annuler cette réservation.")
        return redirect('mes_reservations')

    if request.method == 'POST':
        # Libérer les places si la réservation était acceptée
        if reservation.statut == 'accepte':
            reservation.trajet.nbrPlaceDispo += reservation.nbr_place_reserve
            reservation.trajet.save()

        # Notification conducteur
        conducteur_user = reservation.trajet.conducteur.utilisateur
        title = "Réservation annulée 🚫"
        message = (
            f"La réservation du passager {reservation.passager.utilisateur.firstName} "
            f"{reservation.passager.utilisateur.lastName} pour le trajet "
            f"{reservation.trajet.villeDep} → {reservation.trajet.villeArr} "
            f"du {reservation.trajet.dateHeureDepart.strftime('%d/%m/%Y à %H:%M')} "
            f"a été annulée.\n\n"
            f"Nombre de places libérées : {reservation.nbr_place_reserve}"
        )
        
        print(f"🔔 Envoi notification à {conducteur_user.email}: {title}")
        send_notification(conducteur_user, title, message, "annulation_reservation")

        reservation.delete()
        messages.success(request, "Réservation annulée avec succès. Le conducteur a été notifié.")
        return redirect('mes_reservations')

    return render(request, 'reservations/annuler_reservation.html', {'reservation': reservation})

def modifier_statut_reservation(request, reservation_id):
    """
    Vue pour modifier le statut d'une réservation (alternative)
    """
    conducteur_id = request.session.get('user_id')
    if not conducteur_id:
        messages.error(request, "Vous devez être connecté en tant que conducteur.")
        return redirect('login')

    conducteur = get_object_or_404(Conducteur, utilisateur=conducteur_id)
    reservation = get_object_or_404(Reservation, pk=reservation_id, trajet__conducteur=conducteur)

    if request.method == 'POST':
        statut = request.POST.get('statut')

        if statut in ['accepte', 'refuse']:
            ancien_statut = reservation.statut

            # Gestion des places
            if statut == 'accepte' and ancien_statut != 'accepte':
                if reservation.nbr_place_reserve <= reservation.trajet.nbrPlaceDispo:
                    reservation.trajet.nbrPlaceDispo -= reservation.nbr_place_reserve
                    reservation.trajet.save()
                else:
                    messages.error(request, "Pas assez de places disponibles.")
                    return redirect('mes_demandes_reservations')

            elif ancien_statut == 'accepte' and statut == 'refuse':
                reservation.trajet.nbrPlaceDispo += reservation.nbr_place_reserve
                reservation.trajet.save()

            reservation.statut = statut
            reservation.save()

            # Notification passager
            passager_user = reservation.passager.utilisateur
            if statut == 'accepte':
                title = "Réservation acceptée ✅"
                message = f"Votre réservation pour le trajet {reservation.trajet.villeDep} → {reservation.trajet.villeArr} a été acceptée."
            else:
                title = "Réservation refusée ❌"
                message = f"Votre réservation pour le trajet {reservation.trajet.villeDep} → {reservation.trajet.villeArr} a été refusée."
            
            print(f"🔔 Envoi notification à {passager_user.email}: {title}")
            send_notification(passager_user, title, message, "changement_statut")
            messages.success(request, f"Réservation {statut}e avec succès. Le passager a été notifié.")

        return redirect('mes_demandes_reservations')

    return render(request, 'reservations/modifier_statut.html', {'reservation': reservation})