from django.contrib import admin
from .models import Utilisateur

@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display = ('firstName', 'lastName', 'email', 'phone', 'adresse')  # Colonnes visibles dans la liste
    search_fields = ('firstName', 'lastName', 'email', 'phone')  # Barre de recherche
    list_filter = ('firstName', 'lastName')  # Filtres latéraux
    ordering = ('lastName', 'firstName')  # Tri par défaut
