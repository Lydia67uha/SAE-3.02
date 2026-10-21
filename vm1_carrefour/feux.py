class Feux:

    def __init__(self):
        self.phase = 0

        self.nord_sud = "VERT"
        self.est_ouest = "ROUGE"

        self.durees = [8, 2, 1, 8, 2, 1]


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


    def afficher(self):
        print("Nord/Sud :", self.nord_sud)
        print("Est/Ouest :", self.est_ouest)

    def duree_phase(self):
        return self.durees[self.phase]