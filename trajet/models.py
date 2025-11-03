from django.db import models
from conducteur.models import Conducteur
from passager.models import Passager

from django.db import models
from conducteur.models import Conducteur
from voiture.models import Vehicule  # ✅ importer ici

class Trajet(models.Model):
    STATUT_CHOICES = [
        ('planifie', 'Planifié'),
        ('en_cours', 'En Cours'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé'),
    ]

    villeDep = models.CharField(max_length=50)
    villeArr = models.CharField(max_length=50)
    prix = models.DecimalField(max_digits=8, decimal_places=2)
    nbrPlaceDispo = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUT_CHOICES, default='planifie')
    bagages = models.BooleanField(default=True)
    animaux = models.BooleanField(default=False)
    fumeur = models.BooleanField(default=False)
    conducteur = models.ForeignKey(Conducteur, on_delete=models.CASCADE, related_name='trajets')
    voiture = models.ForeignKey(Vehicule, on_delete=models.SET_NULL, null=True, blank=True, related_name='trajets')  # ✅ ajouté
    dateHeureDepart = models.DateTimeField()
    dateHeureArrivee = models.DateTimeField()

    def __str__(self):
        return (
            f"{self.villeDep} → {self.villeArr} | "
            f"Conducteur: {self.conducteur.utilisateur.firstName} {self.conducteur.utilisateur.lastName} | "
            f"Voiture: {self.voiture.marque if self.voiture else 'N/A'} {self.voiture.modele if self.voiture else ''} | "
            f"Places dispo: {self.nbrPlaceDispo} | "
            f"Prix: {self.prix} DT | "
            f"Départ: {self.dateHeureDepart.strftime('%d/%m/%Y %H:%M')} | "
            f"Arrivée: {self.dateHeureArrivee.strftime('%d/%m/%Y %H:%M')} | "
            f"Statut: {self.status} | "
            f"Bagages: {'Oui' if self.bagages else 'Non'} | "
            f"Animaux: {'Oui' if self.animaux else 'Non'} | "
            f"Fumeur: {'Oui' if self.fumeur else 'Non'}"
        )

class Reservation(models.Model):
    STATUT_CHOICES = [
        ('confirme', 'Confirmé'),
        ('en_attente', 'En Attente'),
        ('annule', 'Annulé'),
    ]
    
    idReservation = models.CharField(max_length=8, unique=True)
    dateReservation = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    nbrPlacesReservees = models.IntegerField(default=1)
    passager = models.ForeignKey(
        Passager, 
        on_delete=models.CASCADE, 
        related_name='reservations'
    )
    trajet = models.ForeignKey(
        Trajet, 
        on_delete=models.CASCADE, 
        related_name='reservations'
    )

    def __str__(self):
        return f"Réservation {self.idReservation} | {self.passager.utilisateur.firstName} → {self.trajet.villeDep}-{self.trajet.villeArr}"
