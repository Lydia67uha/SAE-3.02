import sys

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QGraphicsScene,
    QGraphicsView,
    QFrame
)

from PyQt6.QtGui import QColor, QBrush, QPen, QFont
from PyQt6.QtCore import Qt


# =========================================================
# APPLICATION
# =========================================================

app = QApplication(sys.argv)

fenetre = QWidget()
fenetre.setWindowTitle("Supervision du carrefour intelligent")
fenetre.resize(1200, 680)

layout_principal = QHBoxLayout(fenetre)
layout_principal.setContentsMargins(0, 0, 0, 0)
layout_principal.setSpacing(0)


# =========================================================
# SCENE
# =========================================================

scene = QGraphicsScene()

scene.setSceneRect(
    0,
    0,
    2400,
    1800
)

vue = QGraphicsView(scene)

vue.setFixedSize(
    900,
    675
)

vue.setFrameShape(
    QFrame.Shape.NoFrame
)

vue.setHorizontalScrollBarPolicy(
    Qt.ScrollBarPolicy.ScrollBarAlwaysOff
)

vue.setVerticalScrollBarPolicy(
    Qt.ScrollBarPolicy.ScrollBarAlwaysOff
)

layout_principal.addWidget(vue)


# =========================================================
# COULEURS
# =========================================================

herbe = QColor("#78B957")
route = QColor("#43484E")
trottoir = QColor("#CACACA")

blanc = QColor("white")
noir = QColor("#222222")

scene.setBackgroundBrush(
    QBrush(herbe)
)


# =========================================================
# POSITION DU CARREFOUR
# =========================================================

centre_x = 1200
centre_y = 900

largeur_route = 120
largeur_trottoir = 150


# =========================================================
# POSITION DES VOIES
# CIRCULATION A DROITE
# =========================================================

# NORD -> SUD ↓
x_voie_nord = centre_x - 46

# SUD -> NORD ↑
x_voie_sud = centre_x + 14

# OUEST -> EST →
y_voie_ouest = centre_y + 14

# EST -> OUEST ←
y_voie_est = centre_y - 46


# =========================================================
# TROTTOIRS
# =========================================================

scene.addRect(
    centre_x - largeur_trottoir // 2,
    -20,
    largeur_trottoir,
    1840,
    QPen(trottoir),
    QBrush(trottoir)
)

scene.addRect(
    -20,
    centre_y - largeur_trottoir // 2,
    2440,
    largeur_trottoir,
    QPen(trottoir),
    QBrush(trottoir)
)


# =========================================================
# ROUTES
# =========================================================

scene.addRect(
    centre_x - largeur_route // 2,
    -20,
    largeur_route,
    1840,
    QPen(route),
    QBrush(route)
)

scene.addRect(
    -20,
    centre_y - largeur_route // 2,
    2440,
    largeur_route,
    QPen(route),
    QBrush(route)
)


# =========================================================
# LIGNES CENTRALES
# =========================================================

ligne = QPen(blanc)
ligne.setWidth(5)

ligne.setStyle(
    Qt.PenStyle.DashLine
)


# Nord
scene.addLine(
    centre_x,
    -20,
    centre_x,
    centre_y - 60,
    ligne
)

# Sud
scene.addLine(
    centre_x,
    centre_y + 60,
    centre_x,
    1820,
    ligne
)

# Ouest
scene.addLine(
    -20,
    centre_y,
    centre_x - 60,
    centre_y,
    ligne
)

# Est
scene.addLine(
    centre_x + 60,
    centre_y,
    2420,
    centre_y,
    ligne
)


# =========================================================
# PASSAGES PIETONS
# =========================================================

# Nord et Sud
for x in range(
    centre_x - 50,
    centre_x + 51,
    18
):

    scene.addRect(
        x,
        centre_y - 105,
        10,
        25,
        QPen(blanc),
        QBrush(blanc)
    )

    scene.addRect(
        x,
        centre_y + 80,
        10,
        25,
        QPen(blanc),
        QBrush(blanc)
    )


# Ouest et Est
for y in range(
    centre_y - 50,
    centre_y + 51,
    18
):

    scene.addRect(
        centre_x - 105,
        y,
        25,
        10,
        QPen(blanc),
        QBrush(blanc)
    )

    scene.addRect(
        centre_x + 80,
        y,
        25,
        10,
        QPen(blanc),
        QBrush(blanc)
    )


# =========================================================
# FEUX VERTICAUX
# =========================================================

def feu_vertical(x, y, rouge_en_bas):

    scene.addRect(
        x,
        y,
        18,
        50,
        QPen(noir),
        QBrush(noir)
    )

    if rouge_en_bas:

        couleurs = [
            QColor("#555555"),
            QColor("#555555"),
            QColor("red")
        ]

    else:

        couleurs = [
            QColor("red"),
            QColor("#555555"),
            QColor("#555555")
        ]

    for i in range(3):

        scene.addEllipse(
            x + 3,
            y + 3 + i * 15,
            11,
            11,
            QPen(noir),
            QBrush(couleurs[i])
        )


# =========================================================
# FEUX HORIZONTAUX
# =========================================================

def feu_horizontal(x, y, rouge_a_droite):

    scene.addRect(
        x,
        y,
        50,
        18,
        QPen(noir),
        QBrush(noir)
    )

    if rouge_a_droite:

        couleurs = [
            QColor("#555555"),
            QColor("#555555"),
            QColor("red")
        ]

    else:

        couleurs = [
            QColor("red"),
            QColor("#555555"),
            QColor("#555555")
        ]

    for i in range(3):

        scene.addEllipse(
            x + 3 + i * 15,
            y + 3,
            11,
            11,
            QPen(noir),
            QBrush(couleurs[i])
        )


# =========================================================
# POSITION DES FEUX
# =========================================================

# NORD ↓
feu_vertical(
    centre_x - 90,
    centre_y - 145,
    True
)

# SUD ↑
feu_vertical(
    centre_x + 72,
    centre_y + 95,
    False
)

# OUEST →
feu_horizontal(
    centre_x - 145,
    centre_y + 72,
    True
)

# EST ←
feu_horizontal(
    centre_x + 95,
    centre_y - 90,
    False
)


# =========================================================
# VEHICULE
# =========================================================

def vehicule(
    x,
    y,
    sens,
    type_vehicule,
    couleur="#3498DB"
):

    type_minuscule = type_vehicule.lower()

    # Couleur normale
    couleur_carrosserie = QColor(couleur)

    couleur_marque = None
    texte = ""


    # =====================================================
    # APPARENCE SELON LE TYPE
    # =====================================================

    if type_minuscule == "police":

        couleur_carrosserie = QColor("white")
        couleur_marque = QColor("#1565C0")
        texte = "POL"


    elif type_minuscule == "gendarmerie":

        couleur_carrosserie = QColor("#183B73")
        couleur_marque = QColor("white")
        texte = "G"


    elif type_minuscule == "pompiers":

        couleur_carrosserie = QColor("#D32F2F")
        couleur_marque = QColor("#FDD835")
        texte = "18"


    elif type_minuscule == "ambulance":

        couleur_carrosserie = QColor("white")
        couleur_marque = QColor("#D32F2F")
        texte = "+"


    elif type_minuscule == "samu":

        couleur_carrosserie = QColor("white")
        couleur_marque = QColor("#E53935")
        texte = "SAMU"


    elif type_minuscule == "transport médical urgent":

        couleur_carrosserie = QColor("white")
        couleur_marque = QColor("#009688")
        texte = "TMU"


    # Tous les types sauf normal sont prioritaires
    prioritaire = (
        type_minuscule != "normal"
    )


    vitre = QColor("#9FD3E8")

    phares = QColor("#FFF176")

    feux_arriere = QColor("#F44336")


    # =====================================================
    # VEHICULE VERTICAL
    # =====================================================

    if sens == "BAS" or sens == "HAUT":

        largeur = 32
        hauteur = 56

        # Carrosserie
        scene.addRect(
            x,
            y,
            largeur,
            hauteur,
            QPen(noir),
            QBrush(couleur_carrosserie)
        )


        # Vitre avant
        scene.addRect(
            x + 5,
            y + 10,
            22,
            10,
            QPen(noir),
            QBrush(vitre)
        )


        # Vitre arrière
        scene.addRect(
            x + 5,
            y + 36,
            22,
            10,
            QPen(noir),
            QBrush(vitre)
        )


        # Marquage du véhicule spécial
        if couleur_marque is not None:

            scene.addRect(
                x + 3,
                y + 24,
                26,
                8,
                QPen(couleur_marque),
                QBrush(couleur_marque)
            )


        # =====================================
        # VERS LE BAS ↓
        # =====================================

        if sens == "BAS":

            # Phares jaunes DEVANT
            scene.addEllipse(
                x + 3,
                y + 48,
                8,
                8,
                QPen(noir),
                QBrush(phares)
            )

            scene.addEllipse(
                x + 21,
                y + 48,
                8,
                8,
                QPen(noir),
                QBrush(phares)
            )

            # Feux rouges ARRIERE
            scene.addEllipse(
                x + 3,
                y + 1,
                7,
                7,
                QPen(noir),
                QBrush(feux_arriere)
            )

            scene.addEllipse(
                x + 22,
                y + 1,
                7,
                7,
                QPen(noir),
                QBrush(feux_arriere)
            )


        # =====================================
        # VERS LE HAUT ↑
        # =====================================

        else:

            # Phares jaunes DEVANT
            scene.addEllipse(
                x + 3,
                y + 1,
                8,
                8,
                QPen(noir),
                QBrush(phares)
            )

            scene.addEllipse(
                x + 21,
                y + 1,
                8,
                8,
                QPen(noir),
                QBrush(phares)
            )

            # Feux rouges ARRIERE
            scene.addEllipse(
                x + 3,
                y + 48,
                7,
                7,
                QPen(noir),
                QBrush(feux_arriere)
            )

            scene.addEllipse(
                x + 22,
                y + 48,
                7,
                7,
                QPen(noir),
                QBrush(feux_arriere)
            )


        # =====================================
        # GYROPHARES SUR LE TOIT
        # =====================================

        if prioritaire:

            # Gauche
            scene.addEllipse(
                x + 3,
                y + 23,
                9,
                9,
                QPen(QColor("#0D47A1")),
                QBrush(QColor("#2196F3"))
            )

            # Droite
            scene.addEllipse(
                x + 20,
                y + 23,
                9,
                9,
                QPen(QColor("#0D47A1")),
                QBrush(QColor("#2196F3"))
            )


    # =====================================================
    # VEHICULE HORIZONTAL
    # =====================================================

    else:

        largeur = 56
        hauteur = 32

        # Carrosserie
        scene.addRect(
            x,
            y,
            largeur,
            hauteur,
            QPen(noir),
            QBrush(couleur_carrosserie)
        )


        # Vitres
        scene.addRect(
            x + 10,
            y + 5,
            10,
            22,
            QPen(noir),
            QBrush(vitre)
        )

        scene.addRect(
            x + 36,
            y + 5,
            10,
            22,
            QPen(noir),
            QBrush(vitre)
        )


        # Marquage du véhicule spécial
        if couleur_marque is not None:

            scene.addRect(
                x + 24,
                y + 3,
                8,
                26,
                QPen(couleur_marque),
                QBrush(couleur_marque)
            )


        # =====================================
        # VERS LA DROITE →
        # =====================================

        if sens == "DROITE":

            # Phares jaunes DEVANT
            scene.addEllipse(
                x + 48,
                y + 3,
                8,
                8,
                QPen(noir),
                QBrush(phares)
            )

            scene.addEllipse(
                x + 48,
                y + 21,
                8,
                8,
                QPen(noir),
                QBrush(phares)
            )

            # Feux rouges ARRIERE
            scene.addEllipse(
                x + 1,
                y + 3,
                7,
                7,
                QPen(noir),
                QBrush(feux_arriere)
            )

            scene.addEllipse(
                x + 1,
                y + 22,
                7,
                7,
                QPen(noir),
                QBrush(feux_arriere)
            )


        # =====================================
        # VERS LA GAUCHE ←
        # =====================================

        else:

            # Phares jaunes DEVANT
            scene.addEllipse(
                x + 1,
                y + 3,
                8,
                8,
                QPen(noir),
                QBrush(phares)
            )

            scene.addEllipse(
                x + 1,
                y + 21,
                8,
                8,
                QPen(noir),
                QBrush(phares)
            )

            # Feux rouges ARRIERE
            scene.addEllipse(
                x + 48,
                y + 3,
                7,
                7,
                QPen(noir),
                QBrush(feux_arriere)
            )

            scene.addEllipse(
                x + 48,
                y + 22,
                7,
                7,
                QPen(noir),
                QBrush(feux_arriere)
            )


        # =====================================
        # GYROPHARES SUR LE TOIT
        # =====================================

        if prioritaire:

            # Haut
            scene.addEllipse(
                x + 23,
                y + 3,
                9,
                9,
                QPen(QColor("#0D47A1")),
                QBrush(QColor("#2196F3"))
            )

            # Bas
            scene.addEllipse(
                x + 23,
                y + 20,
                9,
                9,
                QPen(QColor("#0D47A1")),
                QBrush(QColor("#2196F3"))
            )


    # =====================================================
    # PETIT TEXTE DU TYPE
    # =====================================================

    if texte != "":

        nom = scene.addText(
            texte
        )

        nom.setFont(
            QFont(
                "Arial",
                7,
                QFont.Weight.Bold
            )
        )

        if type_minuscule == "gendarmerie":
            nom.setDefaultTextColor(
                QColor("white")
            )
        else:
            nom.setDefaultTextColor(
                QColor("#202020")
            )


        if sens == "BAS" or sens == "HAUT":

            nom.setPos(
                x + 4,
                y + 17
            )

        else:

            nom.setPos(
                x + 15,
                y + 5
            )


# =========================================================
# VEHICULES NORD -> SUD ↓
# VOIE GAUCHE DE L'ECRAN
# =========================================================

vehicule(
    x_voie_nord,
    150,
    "BAS",
    "normal",
    "#3498DB"
)

vehicule(
    x_voie_nord,
    400,
    "BAS",
    "police"
)

vehicule(
    x_voie_nord,
    650,
    "BAS",
    "normal",
    "#F1C40F"
)


# =========================================================
# VEHICULES SUD -> NORD ↑
# VOIE DROITE DE L'ECRAN
# =========================================================

vehicule(
    x_voie_sud,
    1600,
    "HAUT",
    "ambulance"
)

vehicule(
    x_voie_sud,
    1350,
    "HAUT",
    "normal",
    "#9B59B6"
)

vehicule(
    x_voie_sud,
    1150,
    "HAUT",
    "SAMU"
)


# =========================================================
# VEHICULES OUEST -> EST →
# VOIE DU BAS
# =========================================================

vehicule(
    150,
    y_voie_ouest,
    "DROITE",
    "normal",
    "#3498DB"
)

vehicule(
    500,
    y_voie_ouest,
    "DROITE",
    "pompiers"
)

vehicule(
    850,
    y_voie_ouest,
    "DROITE",
    "transport médical urgent"
)


# =========================================================
# VEHICULES EST -> OUEST ←
# VOIE DU HAUT
# =========================================================

vehicule(
    2200,
    y_voie_est,
    "GAUCHE",
    "gendarmerie"
)

vehicule(
    1900,
    y_voie_est,
    "GAUCHE",
    "normal",
    "#E74C3C"
)

vehicule(
    1650,
    y_voie_est,
    "GAUCHE",
    "normal",
    "#2ECC71"
)


# =========================================================
# PANNEAU DE SUPERVISION
# =========================================================

panneau = QWidget()

panneau.setFixedWidth(
    300
)

layout_panneau = QVBoxLayout(
    panneau
)

layout_panneau.setContentsMargins(
    20,
    20,
    20,
    20
)


# =========================================================
# TITRE
# =========================================================

titre = QLabel(
    "SUPERVISION"
)

titre.setAlignment(
    Qt.AlignmentFlag.AlignCenter
)

titre.setFont(
    QFont(
        "Arial",
        18,
        QFont.Weight.Bold
    )
)

layout_panneau.addWidget(
    titre
)

layout_panneau.addSpacing(
    25
)


# =========================================================
# MODE
# =========================================================

layout_panneau.addWidget(
    QLabel("Mode du carrefour")
)

mode = QLabel(
    "NORMAL"
)

mode.setAlignment(
    Qt.AlignmentFlag.AlignCenter
)

mode.setStyleSheet("""
background-color: #4CAF50;
color: white;
padding: 10px;
font-weight: bold;
border-radius: 6px;
""")

layout_panneau.addWidget(
    mode
)

layout_panneau.addSpacing(
    20
)


# =========================================================
# NOMBRE DE VEHICULES
# =========================================================

nombre_vehicules = QLabel(
    "Nombre de véhicules : 12"
)

layout_panneau.addWidget(
    nombre_vehicules
)

layout_panneau.addSpacing(
    20
)


# =========================================================
# DENSITE
# =========================================================

layout_panneau.addWidget(
    QLabel("Densité du trafic")
)

choix_densite = QComboBox()

choix_densite.addItems([
    "Faible",
    "Moyenne",
    "Forte"
])

choix_densite.setCurrentText(
    "Moyenne"
)

layout_panneau.addWidget(
    choix_densite
)

layout_panneau.addSpacing(
    25
)


# =========================================================
# BOUTON VP
# =========================================================

bouton_vp = QPushButton(
    "Déclencher un VP"
)

bouton_vp.setEnabled(
    False
)

layout_panneau.addWidget(
    bouton_vp
)

layout_panneau.addStretch()

layout_principal.addWidget(
    panneau
)


# =========================================================
# AFFICHAGE
# =========================================================

fenetre.show()

vue.fitInView(
    scene.sceneRect(),
    Qt.AspectRatioMode.KeepAspectRatio
)

sys.exit(app.exec())