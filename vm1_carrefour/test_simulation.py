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