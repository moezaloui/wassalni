from django.db import models
from conducteur.models import Conducteur
from passager.models import Passager
from trajet.models import Trajet

class Reservation(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('accepte', 'Accepté'),
        ('refuse', 'Refusé'),
        ('annule', 'Annulé'),
    ]

    passager = models.ForeignKey(
        Passager,
        on_delete=models.CASCADE,
        related_name='reservations_passager'
    )
    trajet = models.ForeignKey(
        Trajet,
        on_delete=models.CASCADE,
        related_name='reservations_trajet'
    )
    nbr_place_reserve = models.PositiveIntegerField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_reservation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.passager} -> {self.trajet} ({self.nbr_place_reserve} place(s))"
