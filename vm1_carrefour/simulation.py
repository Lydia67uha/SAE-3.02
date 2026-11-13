import time

from feux import Feux
from zone_conflit import ZoneConflit
from capteur import Capteur
from client import connecter, envoyer, fermer, lire_commandes

from generateur_trafic import doit_creer_vehicule, doit_creer_vp, creer_vehicule
from generateur_trafic import axe_aleatoire, manoeuvre_aleatoire, type_vp_aleatoire, entree_libre


# Durée d'un tour de simulation, en secondes
DUREE_TOUR = 1

# True : des VP apparaissent aussi au hasard (voir PROBABILITE_VP dans
# generateur_trafic.py), mais seulement s'il n'y en a pas déjà un sur la route.
# Dans tous les cas, le bouton de l'interface peut en déclencher un.
VP_ALEATOIRES = True

# Le feu reste vert pour le VP jusqu'à ce qu'il soit bien engagé dans le carrefour :
# à moins de 5 du milieu, soit 10 après la ligne de feu (située à 15). Sans cela
# le feu repasserait au rouge dès que le VP franchit la ligne, et on ne verrait
# presque pas le vert quand un VP attend au feu.
DISTANCE_FIN_DU_VERT = 5


class Simulation:
    """Le carrefour : les feux, les véhicules et le mode de fonctionnement.

    Le MODE décrit ce que fait le carrefour :
      NORMAL         : cycle normal des feux
      SECURISATION   : un VP est détecté, tout est rouge, on attend que le
                       milieu du carrefour soit vide
      PRIORITE       : feu vert uniquement pour l'entrée du VP
      PASSAGE_VP     : le VP a franchi le feu, tout repasse au rouge
      RETOUR_NORMAL  : un dernier tour tout rouge, puis retour au cycle normal
                       (ou au VP suivant s'il y en a un qui attend)
    """

    def __init__(self):
        self.capteur = Capteur()
        self.zone = ZoneConflit(40, 60, 40, 60)
        self.densite = "MOYENNE"
        self.reinitialiser()

    def reinitialiser(self):
        # Remet le carrefour à zéro (la densité choisie est conservée)
        self.feux = Feux()
        self.vehicules = []
        self.prochain_id = 1
        self.tour = 0
        self.mode = "NORMAL"
        self.compteur_phase = 0

        self.vp_en_cours = None      # le VP qu'on fait passer
        self.vp_groupe = []          # VP de la même entrée : ils passent avec lui
        self.vp_en_attente = []      # VP d'une autre entrée : ils attendent leur tour
        self.vp_a_creer = 0          # demandes de VP faites avec le bouton

        # Statistiques : durée de passage de chaque VP (de sa détection à sa sortie
        # du milieu du carrefour) et véhicules sortis pendant le tour
        self.tour_detection = {}         # identifiant du VP -> tour où il a été détecté
        self.vp_dans_le_carrefour = []   # identifiants des VP qui sont au milieu du carrefour
        self.durees_de_passage = {}      # identifiant du VP -> durée de passage (secondes)
        self.sortis = []                 # véhicules sortis pendant ce tour

    def un_tour(self):
        self.tour += 1
        self.sortis = []
        self.creer_vehicules()
        self.detecter_les_vp()
        self.deplacer_les_vehicules()
        self.mesurer_les_passages()
        self.supprimer_les_vehicules_sortis()
        self.gerer_le_mode()

    def executer(self, commande):
        # Commandes envoyées par les boutons de l'interface
        action = commande["action"]

        if action == "DECLENCHER_VP":
            self.vp_a_creer += 1

        elif action == "DENSITE":
            self.densite = commande["valeur"]

        elif action == "RESET":
            self.reinitialiser()
            print(">>> SIMULATION REINITIALISEE <<<")

    # Création des véhicules

    def creer_vehicules(self):
        # Un VP est créé si on l'a demandé avec le bouton, ou avec un "dé"
        # (seulement s'il n'y a pas déjà un VP sur la route)
        veut_un_vp = self.vp_a_creer > 0

        if VP_ALEATOIRES and not self.il_y_a_un_vp() and doit_creer_vp():
            veut_un_vp = True

        if veut_un_vp and self.ajouter_vehicule(True):
            if self.vp_a_creer > 0:
                self.vp_a_creer -= 1

        if doit_creer_vehicule(self.densite):
            self.ajouter_vehicule(False)

    def il_y_a_un_vp(self):
        for vehicule in self.vehicules:
            if vehicule.prioritaire:
                return True

        return False

    def ajouter_vehicule(self, prioritaire):
        # Retourne False si l'entrée choisie n'est pas libre
        axe = axe_aleatoire()

        if not entree_libre(axe, self.vehicules):
            return False

        type_vehicule = type_vp_aleatoire() if prioritaire else "VOITURE"

        vehicule = creer_vehicule(self.prochain_id, axe, manoeuvre_aleatoire(), type_vehicule)

        self.vehicules.append(vehicule)
        self.prochain_id += 1

        if prioritaire:
            print(">>> NOUVEAU VP :", type_vehicule, "- entrée", axe, "<<<")

        return True

    # Détection des véhicules prioritaires

    def detecter_les_vp(self):
        for vehicule in self.vehicules:

            # On ne traite chaque VP qu'une seule fois
            if vehicule.prioritaire and self.capteur.detecter(vehicule):
                if vehicule.identifiant not in self.tour_detection:
                    self.tour_detection[vehicule.identifiant] = self.tour
                    self.nouveau_vp_detecte(vehicule)

    def nouveau_vp_detecte(self, vp):
        # Premier VP : on lance la procédure de sécurisation
        if self.mode == "NORMAL" and self.vp_en_cours is None:
            self.mode = "SECURISATION"
            self.vp_en_cours = vp
            self.feux.desactiver_priorite()
            self.feux.tous_rouges()
            print(">>> VP DETECTE (", vp.type_vehicule, ") : SECURISATION <<<")

        # Même entrée que le VP en cours : il passe avec lui, pendant le même
        # feu vert (on ne relance pas la procédure)
        elif self.vp_en_cours is not None and vp.axe == self.vp_en_cours.axe and self.mode in ("SECURISATION", "PRIORITE"):
            self.vp_groupe.append(vp)
            print(">>> VP SUPPLEMENTAIRE : il passe avec le premier <<<")

        # Autre entrée : il attend la fin du passage en cours
        else:
            self.vp_en_attente.append(vp)
            print(">>> VP EN ATTENTE <<<")

    # Déplacement des véhicules

    def deplacer_les_vehicules(self):
        for vehicule in self.vehicules:
            vehicule.changer_de_voie(self.vehicules)

        for vehicule in self.vehicules:

            if not self.peut_avancer(vehicule):
                continue

            if vehicule.vehicule_en_face(self.vehicules, self.feux):
                continue

            if vehicule.vehicule_devant(self.vehicules):
                continue

            vehicule.avancer(vehicule.vitesse(self.vehicules))

    def peut_avancer(self, vehicule):
        # Pendant la priorité, les règles sont particulières
        if self.mode == "PRIORITE":

            # Les VP passent
            if vehicule is self.vp_en_cours or vehicule in self.vp_groupe:
                return True

            # Les véhicules devant le VP avancent pour libérer la voie
            if self.est_devant_un_vp(vehicule):
                return True

            # Les autres véhicules de la même entrée s'arrêtent à la ligne de feu
            # (le vert est réservé au VP), mais ceux qui l'ont déjà franchie
            # finissent de traverser le carrefour
            if vehicule.axe == self.vp_en_cours.axe:
                distance = vehicule.distance_du_centre()
                return distance <= 10 or distance > 15

        return vehicule.peut_avancer(self.feux)

    def est_devant_un_vp(self, vehicule):
        # Devant le VP en cours, ou devant un des VP qui passent avec lui
        for vp in [self.vp_en_cours] + self.vp_groupe:

            if vp is None or vp is vehicule or vp.axe != vehicule.axe:
                continue

            if vehicule.a_tourne:
                return True

            if not vp.a_tourne and vehicule.progression() > vp.progression():
                return True

        return False

    def mesurer_les_passages(self):
        # Durée de passage d'un VP : du tour où il est détecté jusqu'au tour où
        # il quitte le milieu du carrefour (en secondes)
        for vp in self.vehicules:

            if not vp.prioritaire or vp.identifiant not in self.tour_detection:
                continue

            if self.zone.contient(vp):
                if vp.identifiant not in self.vp_dans_le_carrefour:
                    self.vp_dans_le_carrefour.append(vp.identifiant)

            elif vp.identifiant in self.vp_dans_le_carrefour:
                self.vp_dans_le_carrefour.remove(vp.identifiant)
                tours = self.tour - self.tour_detection[vp.identifiant]
                self.durees_de_passage[vp.identifiant] = tours * DUREE_TOUR

    def supprimer_les_vehicules_sortis(self):
        restants = []

        for v in self.vehicules:

            if not v.est_sorti():
                restants.append(v)
                continue

            # On prévient l'interface : elle l'enregistre dans la base de données
            self.sortis.append({
                "id": v.identifiant,
                "type": v.type_vehicule,
                "axe": v.axe,
                "manoeuvre": v.manoeuvre,
                "prioritaire": v.prioritaire,
                "duree_passage": self.durees_de_passage.get(v.identifiant)
            })

        self.vehicules = restants

    # Les modes du carrefour (en fin de tour)

    def gerer_le_mode(self):

        if self.mode == "NORMAL":
            self.cycle_normal()

        elif self.mode == "SECURISATION":
            # Tout est rouge : on attend que le milieu du carrefour soit vide
            self.feux.tous_rouges()

            if self.zone.est_libre(self.vehicules):
                self.mode = "PRIORITE"
                print(">>> ZONE LIBRE : PRIORITE AU VP, entrée", self.vp_en_cours.axe, "<<<")

        elif self.mode == "PRIORITE":
            # Feu vert uniquement pour l'entrée du VP, jusqu'à ce que tous
            # les VP du groupe soient engagés dans le carrefour
            self.feux.activer_priorite(self.vp_en_cours.axe)

            if self.tous_les_vp_sont_engages():
                self.mode = "PASSAGE_VP"
                self.feux.desactiver_priorite()
                self.feux.tous_rouges()

        elif self.mode == "PASSAGE_VP":
            # Tout est rouge : on attend que le VP ait quitté le carrefour
            self.feux.tous_rouges()

            if self.zone.est_libre(self.vehicules):
                self.mode = "RETOUR_NORMAL"

        elif self.mode == "RETOUR_NORMAL":
            self.feux.tous_rouges()
            self.vp_suivant_ou_retour_normal()

    def cycle_normal(self):
        self.compteur_phase += 1

        if self.compteur_phase < self.feux.duree_phase():
            return

        # Phases "tout rouge" : on attend que le milieu du carrefour soit vide
        if self.feux.phase in (2, 5) and not self.zone.est_libre(self.vehicules):
            return

        self.feux.phase_suivante()
        self.compteur_phase = 0

    def tous_les_vp_sont_engages(self):
        # Un VP qui a déjà tourné est engagé (il a quitté le milieu du carrefour)
        for vp in [self.vp_en_cours] + self.vp_groupe:

            if vp in self.vehicules and not vp.a_tourne:
                if vp.distance_du_centre() >= DISTANCE_FIN_DU_VERT:
                    return False

        return True

    def vp_suivant_ou_retour_normal(self):
        # Un VP attend : on recommence la procédure pour lui
        if len(self.vp_en_attente) > 0:

            self.vp_en_cours = self.vp_en_attente.pop(0)

            # Les VP en attente de la même entrée passent avec lui
            self.vp_groupe = [vp for vp in self.vp_en_attente if vp.axe == self.vp_en_cours.axe]

            for vp in self.vp_groupe:
                self.vp_en_attente.remove(vp)

            self.mode = "SECURISATION"
            self.feux.desactiver_priorite()
            self.compteur_phase = 0
            print(">>> VP SUIVANT : SECURISATION <<<")

        # Sinon retour au cycle normal (en alternant le groupe qui reprend)
        else:
            self.feux.reinitialiser_cycle_normal()
            self.compteur_phase = 0
            self.mode = "NORMAL"
            self.vp_en_cours = None
            self.vp_groupe = []
            print(">>> RETOUR AU FONCTIONNEMENT NORMAL <<<")

    # État envoyé à l'interface

    def etat(self):
        vehicules = []

        for v in self.vehicules:
            vehicules.append({
                "id": v.identifiant,
                "type": v.type_vehicule,
                "axe": v.axe,
                "x": v.x,
                "y": v.y,
                "prioritaire": v.prioritaire,
                "sens": v.sens,
                "manoeuvre": v.manoeuvre,
                "coin": v.coin,
                "sens_sortie": v.sens_sortie
            })

        feux = {}

        for axe in ["NORD", "SUD", "EST", "OUEST"]:
            feux[axe] = self.feux.couleur_pour_axe(axe)

        return {
            "type": "ETAT_CARREFOUR",
            "tour": self.tour,
            "mode": self.mode,
            "densite": self.densite,
            "duree_tour": DUREE_TOUR,
            "feux": feux,
            "vehicules": vehicules,
            "vehicules_sortis": self.sortis
        }


if __name__ == "__main__":

    simulation = Simulation()

    connecter()

    while True:

        # Les boutons de l'interface (VP, densité, reset)
        for commande in lire_commandes():
            simulation.executer(commande)

        simulation.un_tour()

        time.sleep(DUREE_TOUR)

        if not envoyer(simulation.etat()):
            print("Supervision déconnectée : arrêt de la simulation.")
            break

    fermer()
