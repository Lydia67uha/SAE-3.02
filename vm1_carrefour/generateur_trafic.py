import random

from vehicule import Vehicule


def doit_creer_vehicule(densite):

    if densite == "FAIBLE":
        probabilite = 20

    elif densite == "MOYENNE":
        probabilite = 40

    elif densite == "FORTE":
        probabilite = 70

    else:
        probabilite = 40

    nombre = random.randint(1, 100)

    if nombre <= probabilite:
        return True

    return False

def creer_vehicule(identifiant, axe):

    if axe == "NORD":
        x = 47
        y = 0

    elif axe == "SUD":
        x = 53
        y = 100

    elif axe == "OUEST":
        x = 0
        y = 53

    else:
        x = 100
        y = 47

    return Vehicule(identifiant,"VOITURE", axe, x, y,False)

def axe_aleatoire():

    axes = ["NORD","SUD","EST","OUEST"]

    return random.choice(axes)

def entree_libre(axe, vehicules):

    for vehicule in vehicules:

        if vehicule.axe != axe:
            continue

        if axe == "NORD" and vehicule.y <= 10:
            return False

        elif axe == "SUD" and vehicule.y >= 90:
            return False

        elif axe == "OUEST" and vehicule.x <= 10:
            return False

        elif axe == "EST" and vehicule.x >= 90:
            return False

    return True