import random

from vehicule import Vehicule, voie_entree


# Chance (en %) qu'un véhicule apparaisse à chaque tour, selon la densité
PROBABILITES = {"FAIBLE": 20, "MOYENNE": 40, "FORTE": 70}

# Chance (en %) qu'un véhicule prioritaire apparaisse à chaque tour
PROBABILITE_VP = 5

TYPES_VP = ["AMBULANCE", "POLICE", "GENDARMERIE", "POMPIERS", "SAMU", "TRANSPORT_MEDICAL_URGENT"]


def lancer_le_de(pourcentage):
    # Un "dé" de 1 à 100 : vrai si on tombe dans le pourcentage
    return random.randint(1, 100) <= pourcentage


def doit_creer_vehicule(densite):
    return lancer_le_de(PROBABILITES.get(densite, 40))


def doit_creer_vp():
    return lancer_le_de(PROBABILITE_VP)


def axe_aleatoire():
    return random.choice(["NORD", "SUD", "EST", "OUEST"])


def manoeuvre_aleatoire():
    # "TOUT_DROIT" est deux fois plus fréquent
    return random.choice(["TOUT_DROIT", "TOUT_DROIT", "DROITE", "GAUCHE"])


def type_vp_aleatoire():
    return random.choice(TYPES_VP)


def creer_vehicule(identifiant, axe, manoeuvre="TOUT_DROIT", type_vehicule="VOITURE"):
    """Crée un véhicule au bord de la route, dans la voie qui correspond
    à sa manoeuvre. Tout ce qui n'est pas une "VOITURE" est prioritaire."""

    voie = voie_entree(axe, manoeuvre)

    if axe == "NORD":
        x, y = voie, 0
    elif axe == "SUD":
        x, y = voie, 100
    elif axe == "OUEST":
        x, y = 0, voie
    else:
        x, y = 100, voie

    prioritaire = (type_vehicule != "VOITURE")

    return Vehicule(identifiant, type_vehicule, axe, x, y, prioritaire, manoeuvre)


def entree_libre(axe, vehicules):
    # L'entrée est libre si aucun véhicule de cette entrée n'est
    # dans les 10 premières unités de la route
    for vehicule in vehicules:
        if vehicule.axe == axe and vehicule.distance_du_centre() >= 40:
            return False

    return True
