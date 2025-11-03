from django.db import models
from utilisateur.models import Utilisateur  # On importe le modèle Utilisateur

class Passager(models.Model):
    utilisateur = models.OneToOneField(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='passager_profile'
    )

    def __str__(self):
        return f"{self.utilisateur.firstName} {self.utilisateur.lastName}"
