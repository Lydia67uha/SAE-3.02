class Capteur:

    def detecter(self, vehicule):

        if vehicule.axe == "NORD":
            if 20 <= vehicule.y < 35:
                return True

        elif vehicule.axe == "SUD":
            if 65 < vehicule.y <= 80:
                return True

        elif vehicule.axe == "OUEST":
            if 20 <= vehicule.x < 35:
                return True

        elif vehicule.axe == "EST":
            if 65 < vehicule.x <= 80:
                return True

        return False


    def est_prioritaire(self, vehicule):
        return vehicule.prioritaire
    .