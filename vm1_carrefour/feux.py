class Feux:
    """Les feux du carrefour.

    Deux groupes de voies : Nord/Sud et Est/Ouest. En fonctionnement normal,
    les feux suivent un cycle de 6 phases. Quand un véhicule prioritaire (VP)
    arrive, on peut forcer le vert sur une seule entrée (axe_prioritaire).
    """

    # Les 6 phases du cycle : (feu Nord/Sud, feu Est/Ouest)
    PHASES = [
        ("VERT", "ROUGE"),
        ("ORANGE", "ROUGE"),
        ("ROUGE", "ROUGE"),
        ("ROUGE", "VERT"),
        ("ROUGE", "ORANGE"),
        ("ROUGE", "ROUGE")
    ]

    # Durée de chaque phase, en tours de simulation
    DUREES = [8, 2, 1, 8, 2, 1]

    def __init__(self):
        self.phase = 0
        self.nord_sud, self.est_ouest = self.PHASES[0]
        self.axe_prioritaire = None

    def phase_suivante(self):
        self.phase = (self.phase + 1) % len(self.PHASES)
        self.nord_sud, self.est_ouest = self.PHASES[self.phase]

    def duree_phase(self):
        return self.DUREES[self.phase]

    def tous_rouges(self):
        self.nord_sud = "ROUGE"
        self.est_ouest = "ROUGE"

    def activer_priorite(self, axe):
        self.axe_prioritaire = axe

    def desactiver_priorite(self):
        self.axe_prioritaire = None

    def couleur_pour_axe(self, axe):
        # Priorité active : vert pour l'entrée du VP, rouge pour les autres
        if self.axe_prioritaire is not None:
            if axe == self.axe_prioritaire:
                return "VERT"
            return "ROUGE"

        # Fonctionnement normal
        if axe == "NORD" or axe == "SUD":
            return self.nord_sud

        return self.est_ouest

    def reinitialiser_cycle_normal(self):
        """Retour au cycle normal après un VP : on alterne. Le vert est donné
        à l'autre groupe que celui servi avant le VP, pour que ce ne soit pas
        toujours le même groupe qui reprenne.
        (phases 0, 1, 2 = Nord/Sud ; phases 3, 4, 5 = Est/Ouest)"""

        self.axe_prioritaire = None

        if self.phase <= 2:
            self.phase = 3
        else:
            self.phase = 0

        self.nord_sud, self.est_ouest = self.PHASES[self.phase]

    def afficher(self):
        print("Nord/Sud :", self.nord_sud)
        print("Est/Ouest :", self.est_ouest)
