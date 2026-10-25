class Vehicule:

    def __init__(self, identifiant, type_vehicule, axe, x, y, prioritaire, manoeuvre="TOUT_DROIT"):
        self.identifiant = identifiant
        self.type_vehicule = type_vehicule
        self.axe = axe
        self.x = x
        self.y = y
        self.prioritaire = prioritaire
        self.manoeuvre = manoeuvre
        self.a_tourne = False

        if self.axe == "NORD":
            self.sens = "BAS"

        elif self.axe == "SUD":
            self.sens = "HAUT"

        elif self.axe == "OUEST":
            self.sens = "DROITE"

        elif self.axe == "EST":
            self.sens = "GAUCHE"

    def avancer(self, distance):

        # Déplacement actuel du véhicule
        if self.sens == "BAS":
            self.y += distance

        elif self.sens == "HAUT":
            self.y -= distance

        elif self.sens == "DROITE":
            self.x += distance

        elif self.sens == "GAUCHE":
            self.x -= distance

        # Le véhicule doit-il effectuer son virage ?
        if not self.a_tourne and self.manoeuvre != "TOUT_DROIT":

            # Véhicule venant du NORD
            if self.axe == "NORD" and self.y >= 50:

                self.a_tourne = True

                if self.manoeuvre == "DROITE":
                    self.y = 47
                    self.sens = "GAUCHE"

                elif self.manoeuvre == "GAUCHE":
                    self.y = 53
                    self.sens = "DROITE"


            # Véhicule venant du SUD
            elif self.axe == "SUD" and self.y <= 50:

                self.a_tourne = True

                if self.manoeuvre == "DROITE":
                    self.y = 53
                    self.sens = "DROITE"

                elif self.manoeuvre == "GAUCHE":
                    self.y = 47
                    self.sens = "GAUCHE"


            # Véhicule venant de l'OUEST
            elif self.axe == "OUEST" and self.x >= 50:

                self.a_tourne = True

                if self.manoeuvre == "DROITE":
                    self.x = 47
                    self.sens = "BAS"

                elif self.manoeuvre == "GAUCHE":
                    self.x = 53
                    self.sens = "HAUT"


            # Véhicule venant de l'EST
            elif self.axe == "EST" and self.x <= 50:

                self.a_tourne = True

                if self.manoeuvre == "DROITE":
                    self.x = 53
                    self.sens = "HAUT"

                elif self.manoeuvre == "GAUCHE":
                    self.x = 47
                    self.sens = "BAS"

    def peut_avancer(self, feux):

        if self.axe in ["NORD", "SUD"]:
            couleur = feux.nord_sud
        else:
            couleur = feux.est_ouest

        # Feu vert : le véhicule peut avancer
        if couleur == "VERT":
            return True

        # Le véhicule a déjà franchi le feu :
        # il continue pour quitter le carrefour

        if self.axe == "NORD" and self.y >= 40:
            return True

        elif self.axe == "SUD" and self.y <= 60:
            return True

        elif self.axe == "OUEST" and self.x >= 40:
            return True

        elif self.axe == "EST" and self.x <= 60:
            return True

        # Feu rouge ou orange :
        # le véhicule peut encore avancer jusqu'à la ligne d'arrêt

        if self.axe == "NORD" and self.y < 35:
            return True

        elif self.axe == "SUD" and self.y > 65:
            return True

        elif self.axe == "OUEST" and self.x < 35:
            return True

        elif self.axe == "EST" and self.x > 65:
            return True

        # Il est arrivé à la ligne d'arrêt
        return False

    def est_sorti(self):

        if self.x < 0 or self.x > 100:
            return True

        if self.y < 0 or self.y > 100:
            return True

        return False

    def vehicule_devant(self, vehicules):

        distance_securite = 10

        for autre in vehicules:

            # Ne pas se comparer à soi-même
            if autre == self:
                continue

            # Le véhicule doit rouler dans le même sens
            if autre.sens != self.sens:
                continue

            # Si les véhicules roulent verticalement,
            # ils doivent être sur la même ligne x
            if self.sens == "BAS" or self.sens == "HAUT":
                if autre.x != self.x:
                    continue

            # Si les véhicules roulent horizontalement,
            # ils doivent être sur la même ligne y
            elif self.sens == "DROITE" or self.sens == "GAUCHE":
                if autre.y != self.y:
                    continue

            # Déplacement vers le BAS
            if self.sens == "BAS":

                if autre.y > self.y:
                    distance = autre.y - self.y

                    if distance <= distance_securite:
                        return True


            # Déplacement vers le HAUT
            elif self.sens == "HAUT":

                if autre.y < self.y:
                    distance = self.y - autre.y

                    if distance <= distance_securite:
                        return True


            # Déplacement vers la DROITE
            elif self.sens == "DROITE":

                if autre.x > self.x:
                    distance = autre.x - self.x

                    if distance <= distance_securite:
                        return True


            # Déplacement vers la GAUCHE
            elif self.sens == "GAUCHE":

                if autre.x < self.x:
                    distance = self.x - autre.x

                    if distance <= distance_securite:
                        return True

        return False