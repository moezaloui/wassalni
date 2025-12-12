"""
Script simple pour ajouter des données rapidement
Usage: python manage.py shell < quick_populate.py

Assurez-vous d'adapter les imports selon votre structure de projet
"""

print("🚀 Démarrage du script de remplissage rapide...")

# IMPORTEZ VOS MODÈLES ICI
from utilisateur.models import Utilisateur
from conducteur.models import Conducteur
from passager.models import Passager
from voiture.models import Vehicule
from trajet.models import Trajet
from reserver.models import Reservation
from django.contrib.auth.hashers import make_password
from datetime import datetime, timedelta

print("✅ Imports réussis")

# ============================================
# CRÉER DES UTILISATEURS
# ============================================
print("\n🔵 Création des utilisateurs...")

utilisateurs_data = [
    {"firstName": "Youssef", "lastName": "Karoui", "adresse": "Bizerte", "phone": "+216 25 111 222", "email": "youssef.karoui@email.com"},
    {"firstName": "Amira", "lastName": "Trabelsi", "adresse": "Gabès", "phone": "+216 26 222 333", "email": "amira.trabelsi@email.com"},
    {"firstName": "Riadh", "lastName": "Jlassi", "adresse": "Béja", "phone": "+216 27 333 444", "email": "riadh.jlassi@email.com"},
    {"firstName": "Nour", "lastName": "Hammami", "adresse": "Gafsa", "phone": "+216 28 444 555", "email": "nour.hammami@email.com"},
    {"firstName": "Tarek", "lastName": "Messaoudi", "adresse": "Médenine", "phone": "+216 29 555 666", "email": "tarek.messaoudi@email.com"},
]

utilisateurs = []
for data in utilisateurs_data:
    user, created = Utilisateur.objects.get_or_create(
        email=data['email'],
        defaults={
            'firstName': data['firstName'],
            'lastName': data['lastName'],
            'adresse': data['adresse'],
            'phone': data['phone'],
            'password': make_password('password123')
        }
    )
    utilisateurs.append(user)
    if created:
        print(f"  ✅ {data['firstName']} {data['lastName']} créé")
    else:
        print(f"  ⚠️  {data['firstName']} {data['lastName']} existe déjà")

# ============================================
# CRÉER DES CONDUCTEURS
# ============================================
print("\n🚗 Création des conducteurs...")

# Les 2 premiers utilisateurs deviennent conducteurs
for i, user in enumerate(utilisateurs[:2]):
    conducteur, created = Conducteur.objects.get_or_create(
        utilisateur=user,
        defaults={
            'permisID': f'P{100000 + i}',
            'nbrTrajet': 0,
            'vehiculeMat': f'{200+i} TU {3000+i}'
        }
    )
    if created:
        print(f"  ✅ Conducteur créé pour {user.firstName}")
    else:
        print(f"  ⚠️  Conducteur existe déjà pour {user.firstName}")

# ============================================
# CRÉER DES PASSAGERS
# ============================================
print("\n👤 Création des passagers...")

# Les autres utilisateurs deviennent passagers
for user in utilisateurs[2:]:
    passager, created = Passager.objects.get_or_create(
        utilisateur=user
    )
    if created:
        print(f"  ✅ Passager créé pour {user.firstName}")
    else:
        print(f"  ⚠️  Passager existe déjà pour {user.firstName}")

# ============================================
# CRÉER DES VÉHICULES
# ============================================
print("\n🚙 Création des véhicules...")

conducteurs = Conducteur.objects.all()
vehicules_data = [
    {"matricule": "200 TU 3000", "marque": "Toyota", "modele": "Corolla", "couleur": "Rouge", "nbrPlaces": "4"},
    {"matricule": "201 TU 3001", "marque": "Hyundai", "modele": "i20", "couleur": "Bleu", "nbrPlaces": "3"},
]

for i, conducteur in enumerate(conducteurs):
    if i < len(vehicules_data):
        data = vehicules_data[i]
        vehicule, created = Vehicule.objects.get_or_create(
            matricule=data['matricule'],
            defaults={
                'marque': data['marque'],
                'modele': data['modele'],
                'couleur': data['couleur'],
                'conducteur': conducteur,
                'nbrPlaces': data['nbrPlaces']
            }
        )
        if created:
            print(f"  ✅ Véhicule {data['marque']} {data['modele']} créé")
        else:
            print(f"  ⚠️  Véhicule existe déjà")

# ============================================
# CRÉER DES TRAJETS
# ============================================
print("\n🛣️  Création des trajets...")

vehicules = Vehicule.objects.all()
trajets_data = [
    {
        "villeDep": "Tunis", "villeArr": "Sfax", "prix": 40, "nbrPlaceDispo": 3,
        "bagages": True, "animaux": False, "fumeur": False,
        "jours_futur": 3, "heure": 9
    },
    {
        "villeDep": "Sousse", "villeArr": "Bizerte", "prix": 30, "nbrPlaceDispo": 2,
        "bagages": True, "animaux": True, "fumeur": False,
        "jours_futur": 5, "heure": 14
    },
    {
        "villeDep": "Kairouan", "villeArr": "Monastir", "prix": 20, "nbrPlaceDispo": 4,
        "bagages": False, "animaux": False, "fumeur": False,
        "jours_futur": 7, "heure": 11
    },
]

for i, data in enumerate(trajets_data):
    if i < len(conducteurs) and i < len(vehicules):
        conducteur = list(conducteurs)[i % len(conducteurs)]
        vehicule = list(vehicules)[i % len(vehicules)]
        
        date_depart = datetime.now() + timedelta(days=data['jours_futur'], hours=data['heure'])
        date_arrivee = date_depart + timedelta(hours=2)
        
        trajet = Trajet.objects.create(
            conducteur=conducteur,
            voiture=vehicule,
            villeDep=data['villeDep'],
            villeArr=data['villeArr'],
            prix=data['prix'],
            nbrPlaceDispo=data['nbrPlaceDispo'],
            status='planifie',
            bagages=data['bagages'],
            animaux=data['animaux'],
            fumeur=data['fumeur'],
            dateHeureDepart=date_depart,
            dateHeureArrivee=date_arrivee
        )
        print(f"  ✅ Trajet {data['villeDep']} → {data['villeArr']} créé")

# ============================================
# CRÉER DES RÉSERVATIONS
# ============================================
print("\n📝 Création des réservations...")

passagers = Passager.objects.all()
trajets = Trajet.objects.all()

if passagers.exists() and trajets.exists():
    for passager in passagers:
        for trajet in list(trajets)[:2]:  # Chaque passager réserve 2 trajets
            reservation = Reservation.objects.create(
                passager=passager,
                trajet=trajet,
                nbr_place_reserve=1,
                statut='en_attente',
                date_reservation=datetime.now()
            )
            print(f"  ✅ Réservation créée pour {passager.utilisateur.firstName}")

# ============================================
# RÉSUMÉ
# ============================================
print("\n" + "="*60)
print("✅ REMPLISSAGE TERMINÉ AVEC SUCCÈS!")
print("="*60)
print(f"📊 Résumé des données créées:")
print(f"  - Utilisateurs: {Utilisateur.objects.count()}")
print(f"  - Conducteurs: {Conducteur.objects.count()}")
print(f"  - Passagers: {Passager.objects.count()}")
print(f"  - Véhicules: {Vehicule.objects.count()}")
print(f"  - Trajets: {Trajet.objects.count()}")
print(f"  - Réservations: {Reservation.objects.count()}")
print("="*60)
print("\n💡 Mot de passe pour tous les utilisateurs: password123")
print("="*60)