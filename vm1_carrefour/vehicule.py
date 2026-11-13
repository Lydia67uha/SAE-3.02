import copy


# La route va de 0 à 100 : le milieu du carrefour est en 50, la ligne de
# feu à 15 avant le milieu. Un véhicule est repéré par (x, y) = son AVANT.

LONGUEUR = 6       # longueur d'un véhicule
LARGEUR_X = 2.3    # largeur d'un véhicule qui roule verticalement
LARGEUR_Y = 3.1    # largeur d'un véhicule qui roule horizontalement
PAS = 5            # distance parcourue par tour par un véhicule normal
MARGE = 2          # distance de sécurité devant un véhicule

# "Presque au feu" : il reste moins de 25 avant le milieu du carrefour.
# A partir de là, un véhicule ne change plus de voie pour laisser passer un VP :
# sa manoeuvre (tourner à gauche...) passe avant.
DISTANCE_AU_FEU = 25

# Un VP qui doit tourner ne double que s'il est encore loin du feu (au moins 40),
# pour avoir le temps de revenir dans sa voie.
DISTANCE_DEPASSEMENT_VIRAGE = 40


# 2 voies par sens, donc 4 voies par route :
#   "EXT" = voie de droite (côté trottoir) : tout droit ou tourner à droite
#   "INT" = voie de gauche (côté ligne centrale) : tourner à gauche
# Position des deux voies de chaque route (x pour les routes verticales,
# y pour les routes horizontales)

VOIES = {
    "NORD":  {"EXT": 45.5, "INT": 48.5},
    "SUD":   {"EXT": 54.5, "INT": 51.5},
    "OUEST": {"EXT": 56,   "INT": 52},
    "EST":   {"EXT": 44,   "INT": 48}
}

# Sens de roulage des véhicules qui arrivent de chaque entrée
SENS_ENTREE = {"NORD": "BAS", "SUD": "HAUT", "OUEST": "DROITE", "EST": "GAUCHE"}

# Direction de chaque sens : (déplacement en x, déplacement en y)
DIRECTIONS = {"BAS": (0, 1), "HAUT": (0, -1), "DROITE": (1, 0), "GAUCHE": (-1, 0)}

# Route où l'on arrive après un virage : (entrée, manoeuvre) -> route
DESTINATION = {
    ("NORD", "DROITE"): "EST",   ("NORD", "GAUCHE"): "OUEST",
    ("SUD", "DROITE"): "OUEST",  ("SUD", "GAUCHE"): "EST",
    ("OUEST", "DROITE"): "NORD", ("OUEST", "GAUCHE"): "SUD",
    ("EST", "DROITE"): "SUD",    ("EST", "GAUCHE"): "NORD"
}

AXE_OPPOSE = {"NORD": "SUD", "SUD": "NORD", "OUEST": "EST", "EST": "OUEST"}


def voie_pour(manoeuvre):
    # Voie de gauche pour tourner à gauche, voie de droite sinon
    if manoeuvre == "GAUCHE":
        return "INT"

    return "EXT"


def voie_entree(axe, manoeuvre):
    return VOIES[axe][voie_pour(manoeuvre)]


class Vehicule:

    def __init__(self, identifiant, type_vehicule, axe, x, y, prioritaire, manoeuvre="TOUT_DROIT"):
        self.identifiant = identifiant
        self.type_vehicule = type_vehicule
        self.axe = axe                    # entrée par laquelle il est arrivé
        self.x = x
        self.y = y
        self.prioritaire = prioritaire    # vrai pour un véhicule prioritaire (VP)
        self.manoeuvre = manoeuvre        # "TOUT_DROIT", "DROITE" ou "GAUCHE"

        self.sens = SENS_ENTREE[axe]
        self.sens_sortie = self.sens      # sens après le virage
        self.route = axe                  # route sur laquelle il roule
        self.voie = voie_pour(manoeuvre)  # "EXT" ou "INT"
        self.a_tourne = False
        self.attente = 0                  # nombre de tours passés bloqué

        if manoeuvre != "TOUT_DROIT":
            self.sens_sortie = SENS_ENTREE[DESTINATION[(axe, manoeuvre)]]

        self.calculer_coin()

    # Déplacement et virage

    def calculer_coin(self):
        """Le "coin" est le point où le véhicule tourne : il roule dans sa voie
        jusqu'à arriver à la hauteur de la voie de la route où il va."""

        if self.manoeuvre == "TOUT_DROIT":
            self.coin = None
            return

        route = DESTINATION[(self.axe, self.manoeuvre)]
        position = VOIES[route][voie_pour(self.manoeuvre)]

        if self.axe == "NORD" or self.axe == "SUD":
            self.coin = (self.x, position)
        else:
            self.coin = (position, self.y)

    def avancer(self, distance):
        self.attente = 0

        dx, dy = DIRECTIONS[self.sens]
        self.x += dx * distance
        self.y += dy * distance

        # A-t-il atteint (ou dépassé) le coin ? Alors il tourne.
        if not self.a_tourne and self.coin is not None:

            if (self.x - self.coin[0]) * dx + (self.y - self.coin[1]) * dy >= 0:
                self.a_tourne = True
                self.x, self.y = self.coin
                self.sens = self.sens_sortie

                # Il roule maintenant sur la route où il est entré, dans sa voie de sortie
                self.route = DESTINATION[(self.axe, self.manoeuvre)]
                self.voie = voie_pour(self.manoeuvre)

    def distance_du_centre(self):
        # Distance qu'il reste avant le milieu du carrefour (négative s'il l'a dépassé)
        if self.axe == "NORD":
            return 50 - self.y

        if self.axe == "SUD":
            return self.y - 50

        if self.axe == "OUEST":
            return 50 - self.x

        return self.x - 50

    def progression(self):
        # Position le long de la route, dans le sens de roulage
        dx, dy = DIRECTIONS[self.sens]
        return self.x * dx + self.y * dy

    def peut_avancer(self, feux):
        if feux.couleur_pour_axe(self.axe) == "VERT":
            return True

        # Feu rouge ou orange : il avance seulement s'il a déjà franchi la ligne
        # de feu (il doit dégager le carrefour) ou s'il n'y est pas encore arrivé
        distance = self.distance_du_centre()

        return distance <= 10 or distance > 15

    def est_sorti(self):
        # Marge de 10 : on le supprime quand il est entièrement hors de l'écran
        return not (-10 <= self.x <= 110 and -10 <= self.y <= 110)

    def dans_le_carrefour(self):
        return 38 <= self.x <= 62 and 38 <= self.y <= 62

    def vitesse(self, vehicules):
        # Un véhicule normal avance de 5 par tour. Un VP accélère (10) quand la
        # route est libre devant lui, loin du feu ou après l'avoir franchi.
        if not self.prioritaire or self.devant_dans_la_voie(vehicules, 30):
            return PAS

        distance = self.distance_du_centre()

        if self.a_tourne or distance > 30 or distance < 10:
            return 2 * PAS

        return PAS

    # Collisions

    def boite(self, avant=0, arriere=0):
        """Rectangle occupé par le véhicule : (x_min, x_max, y_min, y_max).
        L'avant du véhicule est en (x, y), le reste est derrière lui.
        "avant" et "arriere" agrandissent le rectangle dans le sens de roulage
        (pour garder une distance de sécurité)."""

        dx, dy = DIRECTIONS[self.sens]

        x1, y1 = self.x + dx * avant, self.y + dy * avant
        x2, y2 = self.x - dx * (LONGUEUR + arriere), self.y - dy * (LONGUEUR + arriere)

        # Demi-largeur du véhicule, sur l'axe perpendiculaire à son sens de roulage
        demi_x = LARGEUR_X / 2 if dy != 0 else 0
        demi_y = LARGEUR_Y / 2 if dx != 0 else 0

        return min(x1, x2) - demi_x, max(x1, x2) + demi_x, min(y1, y2) - demi_y, max(y1, y2) + demi_y

    def touche(self, autre, avant=0, arriere=0):
        # Deux véhicules se touchent si leurs rectangles se recouvrent
        a = self.boite(avant, arriere)
        b = autre.boite()

        return a[0] < b[1] and b[0] < a[1] and a[2] < b[3] and b[2] < a[3]

    def vehicule_devant(self, vehicules):
        """Vrai si le prochain déplacement toucherait un autre véhicule.

        On simule le déplacement sur une copie du véhicule, pas par pas de 5 :
        un véhicule rapide ne doit pas "sauter" par-dessus un autre.
        Cela marche partout : dans la file, dans le carrefour, dans un virage."""

        # Sécurité anti-blocage : un véhicule coincé plus de 8 tours dans le
        # carrefour repart quand même, pour ne jamais figer la simulation.
        if self.attente >= 8 and self.dans_le_carrefour():
            return False

        # Après quelques tours d'attente, on réduit la distance de sécurité
        marge = MARGE if self.attente < 3 else 0

        copie = copy.copy(self)

        for pas in range(PAS, self.vitesse(vehicules) + 1, PAS):

            copie.avancer(PAS)

            for autre in vehicules:

                if autre is self or self.touche(autre):
                    continue    # déjà en contact : on le laisse avancer pour se dégager

                if copie.touche(autre, marge):
                    self.attente += 1
                    return True

        return False

    # Virage à gauche : les véhicules qui vont tout droit passent d'abord

    def vehicule_en_face(self, vehicules, feux=None):
        """Vrai si un véhicule qui tourne à gauche doit attendre.

        Il laisse passer les véhicules d'en face qui vont tout droit, s'ils
        arrivent avant qu'il ait fini son virage. Un véhicule d'en face arrêté
        à son feu rouge ne compte pas (sinon tout serait bloqué).
        Un VP ne s'arrête pas pour ça."""

        if self.manoeuvre != "GAUCHE" or self.a_tourne or self.prioritaire:
            return False

        if self.distance_du_centre() > 12:    # pas encore près du carrefour
            return False

        for autre in vehicules:

            if autre.axe != AXE_OPPOSE[self.axe]:
                continue

            # Deux véhicules qui tournent à gauche face à face se croisent au
            # milieu du carrefour : le plus ancien passe d'abord
            if autre.manoeuvre == "GAUCHE":
                if autre.identifiant < self.identifiant and autre.dans_le_carrefour():
                    return True
                continue

            if autre.manoeuvre != "TOUT_DROIT":
                continue

            reste = autre.distance_du_centre()

            # Il attend à son feu rouge sans être engagé : il ne gêne pas
            if feux is not None and feux.couleur_pour_axe(autre.axe) != "VERT" and reste > 10:
                continue

            if -LONGUEUR <= reste <= 25:
                return True

        return False

    # Changement de voie (pour doubler ou laisser passer un VP)

    def devant_dans_la_voie(self, vehicules, distance, voie=None):
        # Un véhicule est-il devant moi, dans ma voie (ou dans la voie "voie"),
        # à moins de "distance" ?
        voie = voie or self.voie

        for autre in vehicules:

            if autre is self or autre.route != self.route:
                continue

            if autre.voie != voie or autre.sens != self.sens:
                continue

            if 0 < autre.progression() - self.progression() <= distance:
                return True

        return False

    def vp_derriere(self, vehicules, distance, toutes_les_voies=False):
        # Un VP arrive-t-il derrière moi (dans ma voie, ou dans n'importe laquelle) ?
        for autre in vehicules:

            if autre is self or not autre.prioritaire:
                continue

            if autre.route != self.route or autre.sens != self.sens:
                continue

            if not toutes_les_voies and autre.voie != self.voie:
                continue

            if 0 < self.progression() - autre.progression() <= distance:
                return True

        return False

    def placer_dans_la_voie(self, voie):
        position = VOIES[self.route][voie]

        if self.sens == "BAS" or self.sens == "HAUT":
            self.x = position
        else:
            self.y = position

        self.voie = voie

        if not self.a_tourne:
            self.calculer_coin()    # avant le virage, le coin se décale avec le véhicule

        elif self.coin is not None:
            # Après le virage, l'interface dessine le véhicule par rapport au coin :
            # le coin se décale donc aussi
            if self.sens == "BAS" or self.sens == "HAUT":
                self.coin = (position, self.coin[1])
            else:
                self.coin = (self.coin[0], position)

    def voie_libre(self, vehicules, voie, marge=10):
        # Peut-on passer dans l'autre voie ? Il ne doit y avoir personne à côté,
        # ni juste devant, ni juste derrière ("marge" = distance vérifiée)
        copie = copy.copy(self)
        copie.placer_dans_la_voie(voie)

        for autre in vehicules:
            if autre is not self and copie.touche(autre, marge, marge):
                return False

        return True

    def voie_necessaire(self):
        # La voie de sa manoeuvre. Après son virage, toutes les voies conviennent.
        if self.a_tourne:
            return None

        return voie_pour(self.manoeuvre)

    def peut_changer_de_voie(self):
        # Possible avant ou après le feu. Au milieu du carrefour, seulement pour
        # aller tout droit ou une fois le virage terminé.
        if self.dans_le_carrefour():
            return self.manoeuvre == "TOUT_DROIT" or self.a_tourne

        return True

    def changer_de_voie(self, vehicules):
        """Gère les changements de voie autour des véhicules prioritaires (VP).

        Chaque véhicule a une voie "nécessaire" selon sa manoeuvre. Il peut la
        quitter temporairement, puis il y revient dès que c'est possible :
        - un VP ralenti par un véhicule devant lui le double par l'autre voie,
          si personne n'y est (devant, derrière ou à côté) ;
        - un véhicule normal dans la voie de gauche se décale à droite quand un
          VP arrive derrière lui, si la voie de droite est libre.
        Presque au feu, la manoeuvre passe avant : le véhicule normal reste dans
        sa voie (le VP le double par l'autre voie)."""

        if not self.peut_changer_de_voie():
            return

        presque_au_feu = not self.a_tourne and self.distance_du_centre() < DISTANCE_AU_FEU
        necessaire = self.voie_necessaire()

        if necessaire is not None and self.voie != necessaire:
            self.retourner_dans_sa_voie(vehicules, necessaire, presque_au_feu)

        elif self.prioritaire:
            self.doubler(vehicules)

        elif self.voie == "INT" and not presque_au_feu:
            # Un VP arrive derrière lui : il se décale à droite pour le laisser passer
            if self.vp_derriere(vehicules, 30) and self.voie_libre(vehicules, "EXT"):
                self.placer_dans_la_voie("EXT")

    def retourner_dans_sa_voie(self, vehicules, necessaire, presque_au_feu):
        # Un véhicule normal laisse d'abord passer le VP qui arrive derrière lui
        # (sauf presque au feu : sa manoeuvre passe avant)
        if not self.prioritaire and not presque_au_feu:
            if self.vp_derriere(vehicules, 30, True):
                return

        # Un VP reste dans l'autre voie tant qu'il n'a pas fini de doubler
        # (sauf presque au feu : il doit alors retourner dans sa voie)
        if self.prioritaire and not presque_au_feu:
            if self.devant_dans_la_voie(vehicules, 16, necessaire):
                return

        marge = 4 if presque_au_feu else 10

        if self.voie_libre(vehicules, necessaire, marge):
            self.placer_dans_la_voie(necessaire)

    def doubler(self, vehicules):
        # Un VP ralenti par le véhicule devant lui le double par l'autre voie.
        # S'il doit tourner, il doit avoir le temps de revenir dans sa voie.
        if not self.devant_dans_la_voie(vehicules, 16):
            return

        a_le_temps = self.manoeuvre == "TOUT_DROIT" or self.distance_du_centre() >= DISTANCE_DEPASSEMENT_VIRAGE

        autre_voie = "EXT" if self.voie == "INT" else "INT"

        if a_le_temps and self.voie_libre(vehicules, autre_voie):
            self.placer_dans_la_voie(autre_voie)
