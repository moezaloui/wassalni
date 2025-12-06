from django.db import models
from conducteur.models import Conducteur

class Vehicule(models.Model):
    matricule = models.CharField(max_length=20, unique=True)
    marque = models.CharField(max_length=20)
    modele = models.CharField(max_length=20)
    nbrPlaces = models.CharField(max_length=4)
    couleur = models.CharField(max_length=20)  # correction de 'coleur' → 'couleur'
    conducteur = models.ForeignKey(
        Conducteur,
        on_delete=models.CASCADE,
        related_name='vehicules'
    )

    def __str__(self):
        return f"{self.marque} {self.modele} ({self.matricule})"
