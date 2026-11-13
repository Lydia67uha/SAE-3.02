class Capteur:
    """Le capteur détecte les véhicules qui arrivent près du feu
    (entre 20 et 35 avant le milieu pour les entrées Nord et Ouest,
    entre 65 et 80 pour les entrées Sud et Est)."""

    def detecter(self, vehicule):

        if vehicule.axe == "NORD":
            return 20 <= vehicule.y < 35

        elif vehicule.axe == "SUD":
            return 65 < vehicule.y <= 80

        elif vehicule.axe == "OUEST":
            return 20 <= vehicule.x < 35

        elif vehicule.axe == "EST":
            return 65 < vehicule.x <= 80

        return False

    def est_prioritaire(self, vehicule):
        return vehicule.prioritaire
