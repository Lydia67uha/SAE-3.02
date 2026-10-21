class Vehicule:

    def __init__(self, identifiant, type_vehicule, axe, x, y, prioritaire):
        self.identifiant = identifiant
        self.type_vehicule = type_vehicule
        self.axe = axe
        self.x = x
        self.y = y
        self.prioritaire = prioritaire

    def avancer(self, distance):

        if self.axe == "NORD":
            self.y += distance

        elif self.axe == "SUD":
            self.y -= distance

        elif self.axe == "OUEST":
            self.x += distance

        elif self.axe == "EST":
            self.x -= distance

    def peut_avancer(self, feux):

        if self.axe in ["NORD", "SUD"]:
            couleur = feux.nord_sud
        else:
            couleur = feux.est_ouest

        # Si le feu est vert, le véhicule peut avancer
        if couleur == "VERT":
            return True

        # Si le véhicule a déjà franchi la ligne du carrefour,
        # il doit continuer pour libérer la zone

        if self.axe == "NORD" and self.y >= 40:
            return True

        elif self.axe == "SUD" and self.y <= 60:
            return True

        elif self.axe == "OUEST" and self.x >= 40:
            return True

        elif self.axe == "EST" and self.x <= 60:
            return True

        # Sinon il reste arrêté
        return False