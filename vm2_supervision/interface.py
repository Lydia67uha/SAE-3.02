import sys
import math
import json
import socket
import threading
import queue
import time

from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, QPushButton
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsItemGroup, QFrame
from PyQt6.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QAbstractItemView, QMessageBox
from PyQt6.QtGui import QColor, QBrush, QPen, QFont, QPainter, QPolygonF
from PyQt6.QtCore import Qt, QTimer, QPointF

from base_de_donnees import enregistrer_etat, enregistrer_vehicule, statistiques_vp
from base_de_donnees import lire_vue, effacer_la_base, VUES


# Supervision du carrefour (VM2). Ce programme :
#   1. dessine le carrefour avec PyQt6 ;
#   2. reçoit l'état du carrefour envoyé par la simulation (VM1) par socket,
#      puis fait avancer les véhicules à l'écran ;
#   3. envoie à la simulation les ordres des boutons (VP, densité, reset).
#
# Vocabulaire PyQt6 : la "scène" est le tableau sur lequel on dessine, la "vue"
# est le widget qui l'affiche, un "item" est une forme dessinée sur la scène.

LARGEUR_SCENE = 1000
HAUTEUR_SCENE = 750

CENTRE_X = LARGEUR_SCENE // 2
CENTRE_Y = HAUTEUR_SCENE // 2

# La simulation utilise des positions de 0 à 100 : ces échelles les
# transforment en pixels dans la scène.
ECHELLE_X = LARGEUR_SCENE / 100
ECHELLE_Y = HAUTEUR_SCENE / 100

# "0.0.0.0" : le serveur accepte la simulation depuis n'importe quelle machine
# (c'est ce qu'il faut pour deux VM). Le port doit être le même dans client.py.
ADRESSE = "0.0.0.0"
PORT = 5000

HERBE = QColor("#78B957")
ROUTE = QColor("#43484E")
TROTTOIR = QColor("#CACACA")
BLANC = QColor("white")
NOIR = QColor("#222222")
GRIS = QColor("#555555")


app = QApplication(sys.argv)

scene = QGraphicsScene()
scene.setSceneRect(0, 0, LARGEUR_SCENE, HAUTEUR_SCENE)
scene.setBackgroundBrush(QBrush(HERBE))


class Vue(QGraphicsView):
    # La scène s'adapte à la taille de la fenêtre et la remplit entièrement
    # (on rogne un peu les bords si besoin) : les routes touchent donc toujours
    # le bord de la fenêtre, sans herbe autour.
    def resizeEvent(self, evenement):
        super().resizeEvent(evenement)
        self.fitInView(scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatioByExpanding)


vue = Vue(scene)
vue.setFrameShape(QFrame.Shape.NoFrame)
vue.setRenderHint(QPainter.RenderHint.Antialiasing)
vue.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
vue.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

fenetre = QWidget()
fenetre.setWindowTitle("Supervision du carrefour intelligent")
fenetre.resize(1200, 680)

disposition = QHBoxLayout(fenetre)       # vue à gauche, panneau à droite
disposition.setContentsMargins(0, 0, 0, 0)
disposition.setSpacing(0)
disposition.addWidget(vue, 1)


def rectangle(x, y, largeur, hauteur, couleur):
    scene.addRect(x, y, largeur, hauteur, QPen(couleur), QBrush(couleur))


def ligne(x1, y1, x2, y2, epaisseur, pointillee):
    stylo = QPen(BLANC)
    stylo.setWidth(epaisseur)

    if pointillee:
        stylo.setStyle(Qt.PenStyle.DashLine)

    scene.addLine(x1, y1, x2, y2, stylo)


# Trottoirs (150 de large) puis routes (120 de large), verticale et horizontale
for largeur, couleur in [(150, TROTTOIR), (120, ROUTE)]:
    rectangle(CENTRE_X - largeur // 2, -20, largeur, HAUTEUR_SCENE + 40, couleur)
    rectangle(-20, CENTRE_Y - largeur // 2, LARGEUR_SCENE + 40, largeur, couleur)

# Lignes centrales (elles s'arrêtent avant le carrefour)
ligne(CENTRE_X, -20, CENTRE_X, CENTRE_Y - 60, 5, True)
ligne(CENTRE_X, CENTRE_Y + 60, CENTRE_X, HAUTEUR_SCENE + 20, 5, True)
ligne(-20, CENTRE_Y, CENTRE_X - 60, CENTRE_Y, 5, True)
ligne(CENTRE_X + 60, CENTRE_Y, LARGEUR_SCENE + 20, CENTRE_Y, 5, True)

# Passages piétons : des bandes blanches sur les 4 côtés
for decalage in range(-50, 51, 18):
    rectangle(CENTRE_X + decalage, CENTRE_Y - 105, 10, 25, BLANC)
    rectangle(CENTRE_X + decalage, CENTRE_Y + 80, 10, 25, BLANC)
    rectangle(CENTRE_X - 105, CENTRE_Y + decalage, 25, 10, BLANC)
    rectangle(CENTRE_X + 80, CENTRE_Y + decalage, 25, 10, BLANC)

# Lignes qui séparent les deux voies de chaque sens (4 voies par route)
for decalage in [-30, 30]:
    ligne(CENTRE_X + decalage, -20, CENTRE_X + decalage, CENTRE_Y - 112, 3, True)
    ligne(CENTRE_X + decalage, CENTRE_Y + 112, CENTRE_X + decalage, HAUTEUR_SCENE + 20, 3, True)
    ligne(-20, CENTRE_Y + decalage, CENTRE_X - 150, CENTRE_Y + decalage, 3, True)
    ligne(CENTRE_X + 150, CENTRE_Y + decalage, LARGEUR_SCENE + 20, CENTRE_Y + decalage, 3, True)

# Lignes d'arrêt (là où les véhicules s'arrêtent au feu rouge)
ligne(CENTRE_X - 60, CENTRE_Y - 112, CENTRE_X, CENTRE_Y - 112, 5, False)
ligne(CENTRE_X, CENTRE_Y + 112, CENTRE_X + 60, CENTRE_Y + 112, 5, False)
ligne(CENTRE_X - 150, CENTRE_Y, CENTRE_X - 150, CENTRE_Y + 60, 5, False)
ligne(CENTRE_X + 150, CENTRE_Y - 60, CENTRE_X + 150, CENTRE_Y, 5, False)


# Flèches sur les voies. Chaque flèche est une liste de points (x, y), dessinée pointe vers le HAUT.
# On la tourne ensuite pour qu'elle suive le sens de la voie.

FLECHE_DROITE = [(-3, 22), (-3, -8), (8, -8), (8, -14), (18, -5), (8, 4), (8, -2), (3, -2), (3, 22)]
FLECHE_GAUCHE = [(-x, y) for x, y in FLECHE_DROITE]     # la même, en miroir
FLECHE_TOUT_DROIT_ET_DROITE = [(-9, 22), (-9, -10), (-14, -10), (-6, -26), (2, -10), (-3, -10), (-3, -4), (8, -4), (8, -11), (18, -1), (8, 9), (8, 2), (-3, 2), (-3, 22)]


def dessiner_fleche(x, y, angle, points):
    forme = QPolygonF([QPointF(px, py) for px, py in points])
    fleche = scene.addPolygon(forme, QPen(Qt.PenStyle.NoPen), QBrush(QColor(255, 255, 255, 230)))
    fleche.setPos(x, y)
    fleche.setRotation(angle)


# Voie de gauche (près de la ligne centrale) : tourner à gauche.
# Voie de droite (côté trottoir) : tout droit ou tourner à droite.
# Pour chaque entrée : (position voie de gauche, position voie de droite, rotation)
ENTREES = [
    ((CENTRE_X - 15, CENTRE_Y - 182), (CENTRE_X - 45, CENTRE_Y - 182), 180),    # Nord (descend)
    ((CENTRE_X + 15, CENTRE_Y + 182), (CENTRE_X + 45, CENTRE_Y + 182), 0),      # Sud (monte)
    ((CENTRE_X - 220, CENTRE_Y + 15), (CENTRE_X - 220, CENTRE_Y + 45), 90),     # Ouest (va à droite)
    ((CENTRE_X + 220, CENTRE_Y - 15), (CENTRE_X + 220, CENTRE_Y - 45), -90)     # Est (va à gauche)
]

for voie_gauche, voie_droite, rotation in ENTREES:
    dessiner_fleche(voie_gauche[0], voie_gauche[1], rotation, FLECHE_GAUCHE)
    dessiner_fleche(voie_droite[0], voie_droite[1], rotation, FLECHE_TOUT_DROIT_ET_DROITE)


# Feux tricolores
COULEURS_FEU = {"ROUGE": QColor("red"), "ORANGE": QColor("orange"), "VERT": QColor("#00C853")}

# Pour chaque entrée : ses 3 ampoules, et la couleur de chaque ampoule
ampoules = {}
couleurs_ampoules = {}


def dessiner_feu(axe, x, y, vertical, vert_en_premier):
    # Le boîtier noir, puis 3 ampoules grises
    if vertical:
        rectangle(x, y, 18, 50, NOIR)
    else:
        rectangle(x, y, 50, 18, NOIR)

    ampoules[axe] = []

    for i in range(3):
        if vertical:
            ampoule = scene.addEllipse(x + 3, y + 3 + i * 15, 11, 11, QPen(NOIR), QBrush(GRIS))
        else:
            ampoule = scene.addEllipse(x + 3 + i * 15, y + 3, 11, 11, QPen(NOIR), QBrush(GRIS))

        ampoules[axe].append(ampoule)

    if vert_en_premier:
        couleurs_ampoules[axe] = ["VERT", "ORANGE", "ROUGE"]
    else:
        couleurs_ampoules[axe] = ["ROUGE", "ORANGE", "VERT"]


def mettre_feu(axe, couleur):
    # Allume l'ampoule de la bonne couleur, éteint les autres
    for i in range(3):
        if couleurs_ampoules[axe][i] == couleur:
            ampoules[axe][i].setBrush(QBrush(COULEURS_FEU[couleur]))
        else:
            ampoules[axe][i].setBrush(QBrush(GRIS))


dessiner_feu("NORD", CENTRE_X - 90, CENTRE_Y - 145, True, True)
dessiner_feu("SUD", CENTRE_X + 72, CENTRE_Y + 95, True, False)
dessiner_feu("OUEST", CENTRE_X - 145, CENTRE_Y + 72, False, True)
dessiner_feu("EST", CENTRE_X + 95, CENTRE_Y - 90, False, False)

for axe in ["NORD", "SUD", "EST", "OUEST"]:
    mettre_feu(axe, "ROUGE")


# Taille d'un véhicule dans la scène (le dessin fait 32 x 56)
ECHELLE_VOITURE = 0.7
LONGUEUR_VOITURE = 56 * ECHELLE_VOITURE

# Couleurs des voitures normales
PALETTE = ["#3498DB", "#F1C40F", "#9B59B6", "#E74C3C", "#2ECC71"]

# Véhicules prioritaires : (couleur, couleur du marquage, texte)
STYLES_VP = {
    "POLICE": ("white", "#1565C0", "POL"),
    "GENDARMERIE": ("#183B73", "white", "G"),
    "POMPIERS": ("#D32F2F", "#FDD835", "18"),
    "AMBULANCE": ("white", "#D32F2F", "+"),
    "SAMU": ("white", "#E53935", "SAMU"),
    "TRANSPORT_MEDICAL_URGENT": ("white", "#009688", "TMU")
}


def dessiner_vehicule(type_vehicule, couleur):
    """Dessine un véhicule qui roule vers le BAS (on le fait tourner ensuite).
    Toutes ses pièces sont rangées dans un "groupe" : on peut ainsi déplacer
    et tourner le véhicule d'un seul coup."""

    groupe = QGraphicsItemGroup()
    scene.addItem(groupe)

    # Éléments que l'animation modifiera plus tard
    groupe.texte = None
    groupe.gyrophares = []
    groupe.eclairage = None

    def rect(x, y, largeur, hauteur, fond, contour=NOIR):
        piece = scene.addRect(x, y, largeur, hauteur, QPen(QColor(contour)), QBrush(QColor(fond)))
        groupe.addToGroup(piece)

    def rond(x, y, diametre, fond, contour=NOIR):
        piece = scene.addEllipse(x, y, diametre, diametre, QPen(QColor(contour)), QBrush(QColor(fond)))
        groupe.addToGroup(piece)
        return piece

    def lumiere(x, y, largeur, hauteur):
        # Ellipse transparente : sa couleur change quand le gyrophare clignote
        piece = scene.addEllipse(x, y, largeur, hauteur, QPen(Qt.PenStyle.NoPen), QBrush(QColor(0, 0, 0, 0)))
        groupe.addToGroup(piece)
        return piece

    prioritaire = type_vehicule in STYLES_VP

    if prioritaire:
        carrosserie, marquage, texte = STYLES_VP[type_vehicule]

        # Lumière des gyrophares sur la route (dessinée sous la carrosserie)
        groupe.eclairage = lumiere(-52, -30, 136, 116)
        groupe.eclairage.setZValue(-1)
    else:
        carrosserie, marquage, texte = couleur, None, ""

    # Carrosserie et vitres
    rect(0, 0, 32, 56, carrosserie)
    rect(5, 10, 22, 10, "#9FD3E8")
    rect(5, 36, 22, 10, "#9FD3E8")

    if marquage is not None:
        rect(3, 24, 26, 8, marquage, marquage)

    # Phares jaunes devant (en bas), feux rouges derrière (en haut)
    rond(3, 48, 8, "#FFF176")
    rond(21, 48, 8, "#FFF176")
    rond(3, 1, 7, "#F44336")
    rond(22, 1, 7, "#F44336")

    # Deux gyrophares, chacun avec son halo de lumière
    if prioritaire:
        for x in [3, 20]:
            ampoule = rond(x, 23, 9, "#2196F3", "#0D47A1")
            halo = lumiere(x - 8, 15, 25, 25)
            groupe.gyrophares.append((ampoule, halo))

    # Petit texte du type (POL, SAMU...)
    if texte != "":
        etiquette = scene.addText(texte)
        etiquette.setFont(QFont("Arial", 7, QFont.Weight.Bold))
        etiquette.setPos(4, 17)

        if type_vehicule == "GENDARMERIE":
            etiquette.setDefaultTextColor(QColor("white"))
        else:
            etiquette.setDefaultTextColor(QColor("#202020"))

        groupe.addToGroup(etiquette)
        groupe.texte = etiquette

    return groupe


# Où dessiner le véhicule et dans quel sens
DIRECTIONS = {"BAS": (0, 1), "HAUT": (0, -1), "DROITE": (1, 0), "GAUCHE": (-1, 0)}

# Rotation du dessin (dessiné vers le BAS) pour chaque sens, en degrés
ANGLES = {"BAS": 0, "GAUCHE": 90, "HAUT": 180, "DROITE": -90}

# Sens de départ selon l'entrée du carrefour
SENS_ENTREE = {"NORD": "BAS", "SUD": "HAUT", "OUEST": "DROITE", "EST": "GAUCHE"}

# Rayon des virages en pixels (le virage à gauche est plus large)
RAYON_DROITE = 30
RAYON_GAUCHE = 45


def en_pixels(x, y):
    return x * ECHELLE_X, y * ECHELLE_Y


def avancement_virage(x, y, sens, coin):
    """Pour un véhicule qui tourne : distance (en pixels) entre son avant et le
    coin du virage. Négative avant le virage, positive après."""

    nez = en_pixels(x, y)
    point = en_pixels(coin[0], coin[1])
    dx, dy = DIRECTIONS[sens]

    return (nez[0] - point[0]) * dx + (nez[1] - point[1]) * dy


def pose_virage(d, coin, sens_entree, sens_sortie, rayon):
    """Position et rotation d'un point du véhicule qui tourne.

    Pour la simulation, un virage est un angle droit au "coin". Ici on l'arrondit :
    - loin du coin (à plus de "rayon"), le véhicule roule en ligne droite ;
    - près du coin, il suit un quart de cercle (le temps que d passe de
      -rayon à +rayon), et sa rotation change progressivement.
    d est la distance par rapport au coin (voir avancement_virage)."""

    coin_x, coin_y = en_pixels(coin[0], coin[1])

    entree = DIRECTIONS[sens_entree]
    sortie = DIRECTIONS[sens_sortie]

    angle_entree = ANGLES[sens_entree]
    difference = ((ANGLES[sens_sortie] - angle_entree + 180) % 360) - 180    # +90 ou -90

    # Avant le virage : ligne droite dans la voie d'arrivée
    if d <= -rayon:
        return coin_x + entree[0] * d, coin_y + entree[1] * d, angle_entree

    # Après le virage : ligne droite dans la voie de sortie
    if d >= rayon:
        return coin_x + sortie[0] * d, coin_y + sortie[1] * d, angle_entree + difference

    # Pendant le virage : f va de 0 à 1, phi de 0 à 90 degrés
    f = (d + rayon) / (2 * rayon)
    phi = f * math.pi / 2

    centre_x = coin_x - entree[0] * rayon + sortie[0] * rayon
    centre_y = coin_y - entree[1] * rayon + sortie[1] * rayon

    x = centre_x - sortie[0] * rayon * math.cos(phi) + entree[0] * rayon * math.sin(phi)
    y = centre_y - sortie[1] * rayon * math.cos(phi) + entree[1] * rayon * math.sin(phi)

    return x, y, angle_entree + difference * f


def centre_depuis_avant(x, y, angle):
    # Le centre du véhicule est un demi-véhicule derrière son avant
    demi = LONGUEUR_VOITURE / 2
    radians = math.radians(angle)

    return x + math.sin(radians) * demi, y - math.cos(radians) * demi


class VehiculeAffiche:
    """Un véhicule à l'écran.

    La simulation envoie les positions une seule fois par tour. Pour que le
    mouvement soit fluide, on fait glisser le véhicule de sa position
    précédente (depart) vers la nouvelle (arrivee) pendant la durée d'un tour.
    La méthode deplacer() est appelée 60 fois par seconde."""

    def __init__(self, infos, duree):
        self.type = infos["type"]
        self.couleur = PALETTE[infos["id"] % len(PALETTE)]

        self.sens = infos["sens"]
        self.sens_entree = SENS_ENTREE[infos["axe"]]
        self.sens_sortie = infos["sens_sortie"]

        if infos["manoeuvre"] == "GAUCHE":
            self.rayon = RAYON_GAUCHE
        else:
            self.rayon = RAYON_DROITE

        self.coin_depart = infos["coin"]
        self.coin_arrivee = infos["coin"]

        # Un nouveau véhicule part du bord de la scène (hors de l'écran)
        x, y = self.point_de_depart(infos)

        self.depart = self.valeur(x, y, self.coin_depart)
        self.arrivee = self.valeur(infos["x"], infos["y"], self.coin_arrivee)

        self.debut = time.monotonic()
        self.duree = duree
        self.phase_gyrophares = None

        self.sprite = dessiner_vehicule(self.type, self.couleur)
        self.sprite.setScale(ECHELLE_VOITURE)
        self.sprite.setTransformOriginPoint(16, 28)     # on tourne autour du centre (32 x 56)

        self.deplacer()

    def point_de_depart(self, infos):
        x, y = infos["x"], infos["y"]

        # Le bord de la scène par où le véhicule est entré, et sa distance à ce bord
        if self.sens == "BAS":
            bord, distance = (x, 0), y
        elif self.sens == "HAUT":
            bord, distance = (x, 100), 100 - y
        elif self.sens == "DROITE":
            bord, distance = (0, y), x
        else:
            bord, distance = (100, y), 100 - x

        # Vu pour la première fois en plein milieu de la route (interface
        # lancée après la simulation) : il apparaît directement sur place
        if distance > 15:
            return x, y

        return bord

    def valeur(self, x, y, coin):
        # Véhicule qui tourne : distance par rapport au coin.
        # Véhicule qui va tout droit : position de son avant, en pixels.
        if coin is not None:
            return avancement_virage(x, y, self.sens, coin)

        return en_pixels(x, y)

    def avancement(self):
        # 0 = le déplacement commence, 1 = le véhicule est arrivé
        return min((time.monotonic() - self.debut) / self.duree, 1)

    def valeur_actuelle(self):
        # Entre depart et arrivee, selon l'avancement
        t = self.avancement()

        if self.coin_arrivee is not None:
            return self.depart + (self.arrivee - self.depart) * t

        x = self.depart[0] + (self.arrivee[0] - self.depart[0]) * t
        y = self.depart[1] + (self.arrivee[1] - self.depart[1]) * t

        return x, y

    def coin_actuel(self):
        # Le coin se décale quand le véhicule change de voie
        t = self.avancement()

        x = self.coin_depart[0] + (self.coin_arrivee[0] - self.coin_depart[0]) * t
        y = self.coin_depart[1] + (self.coin_arrivee[1] - self.coin_depart[1]) * t

        return x, y

    def pose_actuelle(self):
        # Retourne le CENTRE du véhicule et sa rotation
        valeur = self.valeur_actuelle()

        if self.coin_arrivee is not None:
            # Le centre du véhicule suit l'arc de cercle du virage
            d = valeur - LONGUEUR_VOITURE / 2
            return pose_virage(d, self.coin_actuel(), self.sens_entree, self.sens_sortie, self.rayon)

        angle = ANGLES[self.sens]
        centre = centre_depuis_avant(valeur[0], valeur[1], angle)

        return centre[0], centre[1], angle

    def nouvel_etat(self, infos, duree):
        # Le nouveau déplacement part de là où le véhicule est affiché
        self.depart = self.valeur_actuelle()

        if self.coin_arrivee is not None:
            self.coin_depart = self.coin_actuel()

        self.sens = infos["sens"]
        self.coin_arrivee = infos["coin"]
        self.arrivee = self.valeur(infos["x"], infos["y"], self.coin_arrivee)

        self.debut = time.monotonic()
        self.duree = duree

    def deplacer(self):
        x, y, angle = self.pose_actuelle()

        # Le point (16, 28) du dessin doit se trouver au centre du véhicule
        self.sprite.setPos(x - 16, y - 28)
        self.sprite.setRotation(angle)

        # Le texte (POL, SAMU...) reste toujours à l'endroit
        if self.sprite.texte is not None:
            texte = self.sprite.texte
            texte.setTransformOriginPoint(texte.boundingRect().center())
            texte.setRotation(-angle)

        self.faire_clignoter()

    def faire_clignoter(self):
        if len(self.sprite.gyrophares) == 0:
            return

        # Les deux gyrophares s'allument à tour de rôle, 4 fois par seconde
        phase = int(time.monotonic() * 4) % 2

        if phase == self.phase_gyrophares:
            return

        self.phase_gyrophares = phase

        # (couleur allumée, couleur éteinte, couleur de la lumière)
        bleu = (QColor("#64B5F6"), QColor("#0D47A1"), QColor(33, 150, 243))
        rouge = (QColor("#FF5252"), QColor("#7F0000"), QColor(255, 23, 68))

        if phase == 0:
            allume, eteint = bleu, rouge
        else:
            allume, eteint = rouge, bleu

        # Un gyrophare allumé (bleu ou rouge), l'autre éteint
        for i in range(2):
            ampoule, halo = self.sprite.gyrophares[i]

            if i == phase:
                lueur = QColor(allume[2])
                lueur.setAlpha(120)
                ampoule.setBrush(QBrush(allume[0]))
                halo.setBrush(QBrush(lueur))
            else:
                ampoule.setBrush(QBrush(eteint[1]))
                halo.setBrush(QBrush(QColor(0, 0, 0, 0)))

        # La route autour du véhicule prend la couleur du gyrophare allumé
        route_eclairee = QColor(allume[2])
        route_eclairee.setAlpha(85)
        self.sprite.eclairage.setBrush(QBrush(route_eclairee))

    def supprimer(self):
        scene.removeItem(self.sprite)


vehicules_affiches = {}     # identifiant du véhicule -> VehiculeAffiche
duree_tour = 1


# Réseau : communication avec la simulation (VM1) par socket TCP.
# La supervision est le SERVEUR : elle attend que la simulation se connecte.
# Les messages sont des textes JSON, un par ligne.
# Problème : attendre un message bloque le programme. Si on le faisait dans le
# programme principal, la fenêtre serait gelée. On utilise donc un THREAD
# (un deuxième fil d'exécution) qui écoute le réseau pendant que la fenêtre
# continue de fonctionner. Il dépose les messages dans une FILE
# (queue) que la fenêtre vide régulièrement : les deux ne se gênent jamais.

messages_recus = queue.Queue()
connexion = None


def enregistrer_dans_la_base(message):
    # Enregistre l'état du carrefour et les véhicules sortis pendant ce tour
    try:
        enregistrer_etat(message["tour"], message["mode"], len(message["vehicules"]))

        for v in message.get("vehicules_sortis", []):
            enregistrer_vehicule(v["id"], v["type"], v["axe"], v["manoeuvre"], v["prioritaire"], v["duree_passage"])
    except Exception as erreur:
        print("Base de données :", erreur)


def ecouter_simulation():
    # Fonction exécutée par le thread réseau
    global connexion

    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        serveur.bind((ADRESSE, PORT))
    except OSError:
        print("Impossible d'utiliser le port", PORT, "(déjà utilisé ?)")
        return

    serveur.listen()
    print("En attente de la simulation sur le port", PORT, "...")

    while True:

        client, adresse = serveur.accept()      # attend la connexion de la simulation
        connexion = client
        print("Simulation connectée :", adresse[0])
        messages_recus.put({"type": "CONNEXION"})

        try:
            # Un message par ligne
            for ligne_recue in client.makefile("r", encoding="utf-8"):

                message = json.loads(ligne_recue)

                if message["type"] == "ETAT_CARREFOUR":
                    enregistrer_dans_la_base(message)

                messages_recus.put(message)

        except OSError:
            pass

        connexion = None
        print("Simulation déconnectée.")
        messages_recus.put({"type": "DECONNEXION"})


def envoyer_commande(commande):
    # Envoie un ordre à la simulation (s'il y en a une de connectée)
    if connexion is None:
        return

    commande["type"] = "COMMANDE"

    try:
        connexion.sendall((json.dumps(commande) + "\n").encode())
    except OSError:
        pass


# Panneau de supervision, à droite de la fenêtre
COULEURS_MODE = {
    "NORMAL": "#4CAF50",
    "SECURISATION": "#FF9800",
    "PRIORITE": "#D32F2F",
    "PASSAGE_VP": "#D32F2F",
    "RETOUR_NORMAL": "#1976D2"
}

panneau = QWidget()
panneau.setFixedWidth(300)

colonne = QVBoxLayout(panneau)      # les éléments sont rangés de haut en bas
colonne.setContentsMargins(20, 20, 20, 20)

titre = QLabel("SUPERVISION")
titre.setAlignment(Qt.AlignmentFlag.AlignCenter)
titre.setFont(QFont("Arial", 18, QFont.Weight.Bold))
colonne.addWidget(titre)
colonne.addSpacing(25)

colonne.addWidget(QLabel("Mode du carrefour"))
etiquette_mode = QLabel("EN ATTENTE")
etiquette_mode.setAlignment(Qt.AlignmentFlag.AlignCenter)
colonne.addWidget(etiquette_mode)
colonne.addSpacing(20)

etiquette_nombre = QLabel("Nombre de véhicules : 0")
colonne.addWidget(etiquette_nombre)
colonne.addSpacing(20)

colonne.addWidget(QLabel("Densité du trafic"))
choix_densite = QComboBox()
choix_densite.addItems(["Faible", "Moyenne", "Forte"])
choix_densite.setCurrentText("Moyenne")
colonne.addWidget(choix_densite)
colonne.addSpacing(25)

bouton_vp = QPushButton("Déclencher un VP")
colonne.addWidget(bouton_vp)
colonne.addSpacing(10)

bouton_reset = QPushButton("Réinitialiser la simulation")
colonne.addWidget(bouton_reset)

colonne.addStretch()

# Résumé des passages de VP, en bas du panneau
colonne.addWidget(QLabel("STATISTIQUES VP"))
etiquette_stats = QLabel("")
colonne.addWidget(etiquette_stats)

bouton_stats = QPushButton("Voir les statistiques...")
colonne.addWidget(bouton_stats)

disposition.addWidget(panneau)


def afficher_mode(texte, couleur):
    etiquette_mode.setText(texte)
    style = "color: white; padding: 10px; font-weight: bold; border-radius: 6px; background-color: "
    etiquette_mode.setStyleSheet(style + couleur)


# Les boutons envoient des commandes à la simulation
def declencher_vp():
    envoyer_commande({"action": "DECLENCHER_VP"})


def changer_densite():
    envoyer_commande({"action": "DENSITE", "valeur": choix_densite.currentText().upper()})


def reinitialiser():
    envoyer_commande({"action": "RESET"})


bouton_vp.clicked.connect(declencher_vp)          # clic sur le bouton -> fonction
bouton_reset.clicked.connect(reinitialiser)
choix_densite.currentTextChanged.connect(changer_densite)


# Statistiques : résumé en bas du panneau et fenêtre détaillée.
# Les données viennent de la base de données (voir base_de_donnees.py).

def afficher_statistiques():
    # Met à jour le petit résumé des passages de VP
    nombre, moyenne, minimum, maximum = statistiques_vp()

    if nombre == 0:
        etiquette_stats.setText("Aucun passage de VP pour l'instant")
    else:
        texte = "Passages : " + str(nombre) + "\n"
        texte += "Durée moyenne : " + str(round(moyenne, 1)) + " s\n"
        texte += "Minimum : " + str(minimum) + " s - Maximum : " + str(maximum) + " s"
        etiquette_stats.setText(texte)

    # Si la fenêtre détaillée est ouverte, on la met à jour aussi
    if dialogue_stats.isVisible():
        remplir_tableau()


# La fenêtre "Statistiques" : on choisit une requête et son résultat s'affiche
dialogue_stats = QDialog(fenetre)
dialogue_stats.setWindowTitle("Statistiques")
dialogue_stats.resize(780, 480)

disposition_stats = QVBoxLayout(dialogue_stats)

choix_vue = QComboBox()
choix_vue.addItems(list(VUES))
disposition_stats.addWidget(choix_vue)

tableau = QTableWidget()
tableau.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)    # lecture seule
disposition_stats.addWidget(tableau)

bouton_effacer = QPushButton("Effacer toutes les statistiques")
disposition_stats.addWidget(bouton_effacer)


def remplir_tableau():
    # Exécute la requête choisie et affiche le résultat dans le tableau
    colonnes, lignes = lire_vue(choix_vue.currentText())

    tableau.setColumnCount(len(colonnes))
    tableau.setHorizontalHeaderLabels(colonnes)
    tableau.setRowCount(len(lignes))

    for i, ligne_resultat in enumerate(lignes):
        for j, valeur in enumerate(ligne_resultat):
            texte = "" if valeur is None else str(valeur)
            tableau.setItem(i, j, QTableWidgetItem(texte))

    tableau.resizeColumnsToContents()


def ouvrir_statistiques():
    remplir_tableau()
    dialogue_stats.show()


def effacer_statistiques():
    question = "Effacer tous les véhicules et tous les états enregistrés ?"
    reponse = QMessageBox.question(dialogue_stats, "Effacer", question)

    if reponse == QMessageBox.StandardButton.Yes:
        effacer_la_base()
        afficher_statistiques()
        remplir_tableau()


bouton_stats.clicked.connect(ouvrir_statistiques)
bouton_effacer.clicked.connect(effacer_statistiques)
choix_vue.currentTextChanged.connect(remplir_tableau)


def simulation_deconnectee():
    # Plus de simulation : on efface tout et on bloque les boutons
    for vehicule in vehicules_affiches.values():
        vehicule.supprimer()

    vehicules_affiches.clear()

    for axe in ["NORD", "SUD", "EST", "OUEST"]:
        mettre_feu(axe, "ROUGE")

    afficher_mode("EN ATTENTE", "#9E9E9E")
    etiquette_nombre.setText("Nombre de véhicules : 0")
    bouton_vp.setEnabled(False)
    bouton_reset.setEnabled(False)


def simulation_connectee():
    afficher_mode("NORMAL", COULEURS_MODE["NORMAL"])
    bouton_vp.setEnabled(True)
    bouton_reset.setEnabled(True)

    # La simulation démarre en densité "Moyenne" : on lui envoie le choix actuel
    changer_densite()


def traiter_etat(message):
    # Met l'écran à jour avec l'état du carrefour envoyé par la simulation
    global duree_tour

    duree_tour = message["duree_tour"]

    for axe, couleur in message["feux"].items():
        mettre_feu(axe, couleur)

    # Créer ou mettre à jour chaque véhicule
    identifiants = []

    for infos in message["vehicules"]:

        identifiants.append(infos["id"])

        if infos["id"] in vehicules_affiches:
            vehicules_affiches[infos["id"]].nouvel_etat(infos, duree_tour)
        else:
            vehicules_affiches[infos["id"]] = VehiculeAffiche(infos, duree_tour)

    # Supprimer ceux qui ont quitté la simulation
    for identifiant in list(vehicules_affiches):
        if identifiant not in identifiants:
            vehicules_affiches[identifiant].supprimer()
            del vehicules_affiches[identifiant]

    afficher_mode(message["mode"].replace("_", " "), COULEURS_MODE.get(message["mode"], "#4CAF50"))
    etiquette_nombre.setText("Nombre de véhicules : " + str(len(message["vehicules"])))

    # Un véhicule est sorti : s'il y a un VP parmi eux, les statistiques changent
    for v in message.get("vehicules_sortis", []):
        if v["prioritaire"]:
            afficher_statistiques()


def rafraichir():
    # Appelée 60 fois par seconde par le minuteur

    # 1) Lire les messages reçus de la simulation
    while not messages_recus.empty():

        message = messages_recus.get()

        if message["type"] == "ETAT_CARREFOUR":
            traiter_etat(message)

        elif message["type"] == "CONNEXION":
            simulation_connectee()

        elif message["type"] == "DECONNEXION":
            simulation_deconnectee()

    # 2) Faire avancer les véhicules en douceur
    for vehicule in vehicules_affiches.values():
        vehicule.deplacer()


simulation_deconnectee()
afficher_statistiques()

threading.Thread(target=ecouter_simulation, daemon=True).start()

minuteur = QTimer()                     # appelle rafraichir() toutes les 16 ms
minuteur.timeout.connect(rafraichir)
minuteur.start(16)

fenetre.show()

sys.exit(app.exec())
