from django.db import models
from django.core.validators import MinLengthValidator

class Utilisateur(models.Model):
    firstName = models.CharField(max_length=20)
    lastName = models.CharField(max_length=20)
    adresse = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    password = models.CharField(
        max_length=128,
        validators=[MinLengthValidator(8)]
    )

    def __str__(self):
        return f"{self.firstName} {self.lastName} | {self.email}"
