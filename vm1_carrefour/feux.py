class Feux:

    def __init__(self):
        self.phase = 0

        self.nord_sud = "VERT"
        self.est_ouest = "ROUGE"

        self.durees = [8, 2, 1, 8, 2, 1]
        self.axe_prioritaire = None


    def phase_suivante(self):

        self.phase += 1

        if self.phase > 5:
            self.phase = 0


        if self.phase == 0:
            self.nord_sud = "VERT"
            self.est_ouest = "ROUGE"

        elif self.phase == 1:
            self.nord_sud = "ORANGE"
            self.est_ouest = "ROUGE"

        elif self.phase == 2:
            self.nord_sud = "ROUGE"
            self.est_ouest = "ROUGE"

        elif self.phase == 3:
            self.nord_sud = "ROUGE"
            self.est_ouest = "VERT"

        elif self.phase == 4:
            self.nord_sud = "ROUGE"
            self.est_ouest = "ORANGE"

        elif self.phase == 5:
            self.nord_sud = "ROUGE"
            self.est_ouest = "ROUGE"


    def tous_rouges(self):
        self.nord_sud = "ROUGE"
        self.est_ouest = "ROUGE"

    def donner_priorite(self, axe):

        if axe == "NORD" or axe == "SUD":
            self.nord_sud = "VERT"
            self.est_ouest = "ROUGE"

        else:
            self.nord_sud = "ROUGE"
            self.est_ouest = "VERT"


    def afficher(self):
        print("Nord/Sud :", self.nord_sud)
        print("Est/Ouest :", self.est_ouest)

    def duree_phase(self):
        return self.durees[self.phase]

    def activer_priorite(self, axe):
        self.axe_prioritaire = axe

    def desactiver_priorite(self):
        self.axe_prioritaire = None

    def couleur_pour_axe(self, axe):

        # Priorité active :
        # seule l'entrée du VP reçoit le vert
        if self.axe_prioritaire is not None:

            if axe == self.axe_prioritaire:
                return "VERT"

            return "ROUGE"

        # Fonctionnement normal
        if axe == "NORD" or axe == "SUD":
            return self.nord_sud

        return self.est_ouest

    def reinitialiser_cycle_normal(self):

        self.axe_prioritaire = None

        self.phase = 0

        self.nord_sud = "VERT"
        self.est_ouest = "ROUGE"