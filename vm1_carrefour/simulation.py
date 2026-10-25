import time

from vehicule import Vehicule
from feux import Feux
from generateur_trafic import (doit_creer_vehicule, creer_vehicule, axe_aleatoire, entree_libre, creer_vehicule_prioritaire)
from zone_conflit import ZoneConflit
from capteur import Capteur

capteur = Capteur()

feux = Feux()
zone = ZoneConflit(
    40,
    60,
    40,
    60
)
vehicules = []

prochain_id = 1

ambulance = creer_vehicule_prioritaire(
    prochain_id,
    "NORD",
    "AMBULANCE"
)

vehicules.append(ambulance)

prochain_id += 1

densite = "FORTE"

compteur_phase = 0

voiture_test = creer_vehicule(
    prochain_id,
    "NORD",
    "DROITE"
)

vehicules.append(voiture_test)

prochain_id += 1

for tour in range(10):

    if doit_creer_vehicule(densite):

        axe = axe_aleatoire()

        if entree_libre(axe, vehicules):
            nouveau_vehicule = creer_vehicule(
                prochain_id,
                axe
            )

            vehicules.append(nouveau_vehicule)

            print(
                "Nouveau véhicule",
                prochain_id,
                "créé sur l'axe",
                axe
            )

            prochain_id += 1

    print("\n--- TOUR", tour, "---")

    print(
        "Feux : Nord/Sud =",
        feux.nord_sud,
        "| Est/Ouest =",
        feux.est_ouest
    ).


    for vehicule in vehicules:

        print(
            "Véhicule",
            vehicule.identifiant,
            "- axe :",
            vehicule.axe,
            "- position :",
            vehicule.x,
            vehicule.y
        )

        if capteur.detecter(vehicule):

            print(
                "Capteur : véhicule",
                vehicule.identifiant,
                "détecté"
            )

            if capteur.est_prioritaire(vehicule):
                print(
                    ">>> VEHICULE PRIORITAIRE DETECTE :",
                    vehicule.type_vehicule,
                    "- axe",
                    vehicule.axe,
                    "<<<"
                )

        if vehicule.peut_avancer(feux):

            if not vehicule.vehicule_devant(vehicules):
                vehicule.avancer(5)

            else:
                print(
                    "Véhicule",
                    vehicule.identifiant,
                    "arrêté derrière un autre véhicule."
                )

        else:
            print(
                "Véhicule",
                vehicule.identifiant,
                "arrêté au feu."
            )

        vehicules_restants = []

        for vehicule in vehicules:

            if not vehicule.est_sorti():
                vehicules_restants.append(vehicule)

        vehicules = vehicules_restants


    time.sleep(1)

    compteur_phase += 1

    if compteur_phase >= feux.duree_phase():

        if feux.phase == 2 or feux.phase == 5:

            if zone.est_libre(vehicules):

                feux.phase_suivante()
                compteur_phase = 0

                print("\n>>> ZONE LIBRE : CHANGEMENT DE PHASE <<<")

            else:

                print("\n>>> ZONE OCCUPEE : TOUS ROUGES MAINTENUS <<<")

        else:

            feux.phase_suivante()
            compteur_phase = 0

            print("\n>>> CHANGEMENT DE PHASE <<<").