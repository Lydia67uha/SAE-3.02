from vehicule import Vehicule
from capteur import Capteur
from zone_conflit import ZoneConflit
from feux import Feux
import time

capteur = Capteur()

zone = ZoneConflit(
    40,
    60,
    40,
    60
)


voiture = Vehicule(
    1,
    "VOITURE",
    "NORD",
    50,
    20,
    False
)


ambulance = Vehicule(
    2,
    "AMBULANCE",
    "OUEST",
    20,
    50,
    True
)


vehicules = [
    voiture,
    ambulance
]


print("Voiture prioritaire :", capteur.est_prioritaire(voiture))
print("Ambulance prioritaire :", capteur.est_prioritaire(ambulance))

print("Zone libre :", zone.est_libre(vehicules))


print("\nL'ambulance avance...")

ambulance.avancer(25)

print("Position ambulance :", ambulance.x, ambulance.y)
print("Zone libre :", zone.est_libre(vehicules))


print("\nL'ambulance continue...")

ambulance.avancer(20)

print("Position ambulance :", ambulance.x, ambulance.y)
print("Zone libre :", zone.est_libre(vehicules))

'''print("\n--- CYCLE AUTOMATIQUE DES FEUX ---")

feux = Feux()

for i in range(6):

    feux.afficher()

    print(
        "Durée de cette phase :",
        feux.duree_phase(),
        "secondes"
    )

    time.sleep(1)

    print()

    feux.phase_suivante()'''

print("\n--- TEST VEHICULE ET FEUX ---")

feux = Feux()

voiture_test = Vehicule(
    3,
    "VOITURE",
    "OUEST",
    35,
    50,
    False
)

print("Position :", voiture_test.x, voiture_test.y)
print("Feu Est/Ouest :", feux.est_ouest)

if voiture_test.peut_avancer(feux):
    voiture_test.avancer(10)
    print("La voiture avance.")
else:
    print("La voiture s'arrête au feu.")

print("Nouvelle position :", voiture_test.x, voiture_test.y)

print("\n--- TEST AVEC FEU VERT ---")

feux.est_ouest = "VERT"

print("Feu Est/Ouest :", feux.est_ouest)

if voiture_test.peut_avancer(feux):
    voiture_test.avancer(10)
    print("La voiture avance.")
else:
    print("La voiture s'arrête au feu.")

print("Nouvelle position :", voiture_test.x, voiture_test.y)

print("\n--- TEST VOITURE ENGAGEE DANS LA ZONE ---")

feux.est_ouest = "ROUGE"

print("Position actuelle :", voiture_test.x, voiture_test.y)
print("Feu Est/Ouest :", feux.est_ouest)

if voiture_test.peut_avancer(feux):
    voiture_test.avancer(20)
    print("La voiture continue pour libérer le carrefour.")
else:
    print("La voiture s'arrête.")

print("Nouvelle position :", voiture_test.x, voiture_test.y)
print("Zone libre :", zone.est_libre([voiture_test]))

print("\n--- TEST APPROCHE FEU ROUGE ---")

feux = Feux()

voiture_test = Vehicule(
    10,
    "VOITURE",
    "OUEST",
    20,
    50,
    False
)

for i in range(5):

    print("Position :", voiture_test.x)

    if voiture_test.peut_avancer(feux):
        voiture_test.avancer(5)
    else:
        print("La voiture attend au feu.")

from vehicule import Vehicule

voiture = Vehicule(
    1,
    "VOITURE",
    "NORD",
    47,
    0,
    False,
    "DROITE"
)

for i in range(15):
    print(
        "Position :", voiture.x, voiture.y,
        "- axe :", voiture.axe,
        "- sens :", voiture.sens,
        "- tournée :", voiture.a_tourne
    )

    voiture.avancer(5)

print("\n--- TEST DES VIRAGES ---")

tests = [
    ("NORD", "DROITE", 47, 0),
    ("NORD", "GAUCHE", 47, 0),

    ("SUD", "DROITE", 53, 100),
    ("SUD", "GAUCHE", 53, 100),

    ("OUEST", "DROITE", 0, 53),
    ("OUEST", "GAUCHE", 0, 53),

    ("EST", "DROITE", 100, 47),
    ("EST", "GAUCHE", 100, 47)
]

identifiant = 100

for axe, manoeuvre, x, y in tests:

    voiture = Vehicule(
        identifiant,
        "VOITURE",
        axe,
        x,
        y,
        False,
        manoeuvre
    )

    print(
        "\nTest :",
        axe,
        "-",
        manoeuvre
    )

    while not voiture.a_tourne:
        voiture.avancer(5)

    print(
        "Après virage :",
        voiture.x,
        voiture.y,
        "- sens :",
        voiture.sens
    )

    identifiant += 1

print("\n--- TEST VEHICULE DEVANT APRES VIRAGE ---")

# Voiture 1 vient du NORD et tourne à GAUCHE
voiture1 = Vehicule(
    200,
    "VOITURE",
    "NORD",
    47,
    0,
    False,
    "GAUCHE"
)

# On la fait avancer jusqu'à ce qu'elle tourne
while not voiture1.a_tourne:
    voiture1.avancer(5)

print(
    "Voiture 1 :",
    voiture1.x,
    voiture1.y,
    "- axe :", voiture1.axe,
    "- sens :", voiture1.sens
)

# Voiture 2 vient de l'OUEST et roule tout droit
voiture2 = Vehicule(
    201,
    "VOITURE",
    "OUEST",
    57,
    53,
    False,
    "TOUT_DROIT"
)

print(
    "Voiture 2 :",
    voiture2.x,
    voiture2.y,
    "- axe :", voiture2.axe,
    "- sens :", voiture2.sens
)

vehicules_test = [voiture1, voiture2]

if voiture1.vehicule_devant(vehicules_test):
    print("Voiture 1 détecte bien un véhicule devant.")
else:
    print("ERREUR : aucun véhicule détecté devant.")