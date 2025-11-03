from django.db import models
from utilisateur.models import Utilisateur  # On importe le modèle Utilisateur

class Conducteur(models.Model):
    utilisateur = models.OneToOneField(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='conducteur_profile'
    )
    permisID = models.CharField(max_length=20)
    nbrTrajet = models.IntegerField(default=0)
    vehiculeMat = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.utilisateur.firstName} {self.utilisateur.lastName} | Permis: {self.permisID}"
