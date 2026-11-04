import time

from feux import Feux
from zone_conflit import ZoneConflit
from capteur import Capteur

from generateur_trafic import (
    doit_creer_vehicule,
    creer_vehicule,
    creer_vehicule_prioritaire,
    axe_aleatoire,
    manoeuvre_aleatoire,
    type_vp_aleatoire,
    entree_libre,
    doit_creer_vp
)


# --------------------------------------------------
# FONCTION : savoir si un véhicule est devant le VP
# --------------------------------------------------

def est_devant_vp(vehicule, vp):

    # Il doit venir de la même entrée que le VP
    if vehicule.axe != vp.axe:
        return False

    # Le VP ne peut pas être devant lui-même
    if vehicule == vp:
        return False

    # Si le véhicule a déjà tourné,
    # c'est qu'il était déjà passé devant le VP
    if vehicule.a_tourne:
        return True

    # VP venant du NORD : il descend
    if vp.axe == "NORD":
        return vehicule.y > vp.y

    # VP venant du SUD : il monte
    elif vp.axe == "SUD":
        return vehicule.y < vp.y

    # VP venant de l'OUEST : il va vers la droite
    elif vp.axe == "OUEST":
        return vehicule.x > vp.x

    # VP venant de l'EST : il va vers la gauche
    elif vp.axe == "EST":
        return vehicule.x < vp.x

    return False


# --------------------------------------------------
# CREATION DES OBJETS
# --------------------------------------------------

capteur = Capteur()

feux = Feux()

zone = ZoneConflit(
    40,
    60,
    40,
    60
)

vehicules = []

prochain_id = 1

densite = "MOYENNE"

compteur_phase = 0
compteur_retour = 0

# --------------------------------------------------
# ETAT DU SYSTEME
# --------------------------------------------------

mode = "NORMAL"

vp_en_cours = None

vp_en_attente = []

vp_deja_detectes = []

def est_avant_ligne_feu(vehicule):

    if vehicule.axe == "NORD":
        return vehicule.y < 35

    elif vehicule.axe == "SUD":
        return vehicule.y > 65

    elif vehicule.axe == "OUEST":
        return vehicule.x < 35

    elif vehicule.axe == "EST":
        return vehicule.x > 65

    return False

def vp_a_franchi_ligne(vp):

    if vp.axe == "NORD":
        return vp.y > 35

    elif vp.axe == "SUD":
        return vp.y < 65

    elif vp.axe == "OUEST":
        return vp.x > 35

    elif vp.axe == "EST":
        return vp.x < 65

    return False
# --------------------------------------------------
# BOUCLE DE SIMULATION
# --------------------------------------------------

for tour in range(80):

    # ==================================================
    # CREATION ALEATOIRE D'UN VEHICULE PRIORITAIRE
    # ==================================================

    if doit_creer_vp():

        axe_vp = axe_aleatoire()

        if entree_libre(
                axe_vp,
                vehicules
        ):
            type_vp = type_vp_aleatoire()

            manoeuvre_vp = manoeuvre_aleatoire()

            nouveau_vp = creer_vehicule_prioritaire(
                prochain_id,
                axe_vp,
                type_vp,
                manoeuvre_vp
            )

            vehicules.append(
                nouveau_vp
            )

            print(
                "\n>>> NOUVEAU VEHICULE PRIORITAIRE :",
                type_vp,
                "- axe",
                axe_vp,
                "- manoeuvre :",
                manoeuvre_vp,
                "<<<"
            )

            prochain_id += 1

    # ==================================================
    # CREATION ALEATOIRE DES VEHICULES NORMAUX
    # ==================================================

    if doit_creer_vehicule(densite):

        axe = axe_aleatoire()

        if entree_libre(
            axe,
            vehicules
        ):

            manoeuvre = manoeuvre_aleatoire()

            nouveau_vehicule = creer_vehicule(
                prochain_id,
                axe,
                manoeuvre
            )

            vehicules.append(
                nouveau_vehicule
            )

            print(
                "Nouveau véhicule",
                prochain_id,
                "créé sur l'axe",
                axe,
                "- manoeuvre :",
                manoeuvre
            )

            prochain_id += 1


    # ==================================================
    # AFFICHAGE
    # ==================================================

    print(
        "\n--- TOUR",
        tour,
        "---"
    )

    print(
        "Mode :",
        mode
    )

    print(
        "Feux :",
        "Nord =",
        feux.couleur_pour_axe("NORD"),
        "| Sud =",
        feux.couleur_pour_axe("SUD"),
        "| Est =",
        feux.couleur_pour_axe("EST"),
        "| Ouest =",
        feux.couleur_pour_axe("OUEST")
    )


    # ==================================================
    # VEHICULES
    # ==================================================

    for vehicule in vehicules:

        print(
            "Véhicule",
            vehicule.identifiant,
            "- axe :",
            vehicule.axe,
            "- position :",
            vehicule.x,
            vehicule.y,
            "- manoeuvre :",
            vehicule.manoeuvre,
            "- sens :",
            vehicule.sens
        )


        # ==================================================
        # CAPTEUR
        # ==================================================

        if capteur.detecter(
            vehicule
        ):

            print(
                "Capteur : véhicule",
                vehicule.identifiant,
                "détecté"
            )


            # ----------------------------------------------
            # VEHICULE PRIORITAIRE
            # ----------------------------------------------

            if capteur.est_prioritaire(
                    vehicule
            ):

                # On ne traite chaque VP qu'une seule fois
                if vehicule.identifiant not in vp_deja_detectes:

                    vp_deja_detectes.append(
                        vehicule.identifiant
                    )

                    # ==========================================
                    # AUCUN VP EN COURS
                    # ==========================================

                    if mode == "NORMAL" and vp_en_cours is None:

                        mode = "SECURISATION"

                        vp_en_cours = vehicule

                        feux.desactiver_priorite()

                        feux.tous_rouges()

                        compteur_phase = 0

                        print(
                            ">>> VEHICULE PRIORITAIRE DETECTE :",
                            vehicule.type_vehicule,
                            "- axe",
                            vehicule.axe,
                            "<<<"
                        )

                        print(
                            ">>> PASSAGE EN MODE SECURISATION <<<"
                        )


                    # ==========================================
                    # UN AUTRE VP EST DEJA EN COURS
                    # ==========================================

                    else:

                        vp_en_attente.append(
                            vehicule
                        )

                        print(
                            ">>> NOUVEAU VP DETECTE :",
                            vehicule.type_vehicule,
                            "- axe",
                            vehicule.axe,
                            "<<<"
                        )

                        print(
                            ">>> VP PLACE EN ATTENTE <<<"
                        )


        # ==================================================
        # MODE PRIORITE
        # ==================================================

        if mode == "PRIORITE":


            # ----------------------------------------------
            # CAS 1 : LE VEHICULE EST LE VP
            # ----------------------------------------------

            if vehicule == vp_en_cours:

                if vehicule.vehicule_devant(
                        vehicules
                ):

                    print(
                        "VP",
                        vehicule.identifiant,
                        "attend que la voie devant lui se libère."
                    )

                else:

                    vehicule.avancer(5)

                    # Le VP vient-il de franchir son feu ?
                    if vp_a_franchi_ligne(
                            vp_en_cours
                    ):
                        mode = "PASSAGE_VP"

                        # Le vert prioritaire est supprimé
                        feux.desactiver_priorite()

                        # Tous les axes repassent immédiatement au rouge
                        feux.tous_rouges()

                        print(
                            ">>> LE VP A FRANCHI LA LIGNE DU FEU <<<"
                        )

                        print(
                            ">>> TOUS LES FEUX REPASSENT AU ROUGE <<<"
                        )


            # ----------------------------------------------
            # CAS 2 : VEHICULE DEVANT LE VP
            # ----------------------------------------------

            elif est_devant_vp(
                vehicule,
                vp_en_cours
            ):
                def est_avant_ligne_feu(vehicule):

                    if vehicule.axe == "NORD":
                        return vehicule.y < 35

                    elif vehicule.axe == "SUD":
                        return vehicule.y > 65

                    elif vehicule.axe == "OUEST":
                        return vehicule.x < 35

                    elif vehicule.axe == "EST":
                        return vehicule.x > 65

                    return False


                def vp_a_franchi_ligne(vp):

                    if vp.axe == "NORD":
                        return vp.y > 35

                    elif vp.axe == "SUD":
                        return vp.y < 65

                    elif vp.axe == "OUEST":
                        return vp.x > 35

                    elif vp.axe == "EST":
                        return vp.x < 65

                    return False

                # Ces véhicules sont autorisés
                # à dégager la voie du VP

                if vehicule.vehicule_devant(
                    vehicules
                ):

                    print(
                        "Véhicule",
                        vehicule.identifiant,
                        "attend le véhicule devant lui."
                    )

                else:

                    vehicule.avancer(5)


            # ----------------------------------------------
            # CAS 3 : TOUS LES AUTRES VEHICULES
            # ----------------------------------------------

            else:

                if vehicule.axe == vp_en_cours.axe:

                    # Le véhicule derrière le VP peut avancer
                    # jusqu'à la ligne du feu
                    if est_avant_ligne_feu(
                            vehicule
                    ):

                        if vehicule.vehicule_devant(
                                vehicules
                        ):

                            print(
                                "Véhicule",
                                vehicule.identifiant,
                                "attend le véhicule devant lui."
                            )

                        else:

                            vehicule.avancer(5)

                    else:

                        print(
                            "Véhicule",
                            vehicule.identifiant,
                            "arrêté à la ligne pendant la priorité."
                        )

                # Véhicules venant des autres entrées
                else:

                    # Ils peuvent seulement avancer
                    # jusqu'à leur feu rouge
                    if vehicule.peut_avancer(
                        feux
                    ):

                        if vehicule.vehicule_devant(
                            vehicules
                        ):

                            print(
                                "Véhicule",
                                vehicule.identifiant,
                                "arrêté derrière un autre véhicule."
                            )

                        else:

                            vehicule.avancer(5)

                    else:

                        print(
                            "Véhicule",
                            vehicule.identifiant,
                            "arrêté pendant le passage prioritaire."
                        )

        elif mode == "PASSAGE_VP":

            # Tous les feux sont rouges.
            #
            # Le VP étant déjà engagé,
            # peut_avancer() lui permet de continuer.
            #
            # Les autres véhicules peuvent seulement
            # approcher de leur ligne rouge.

            if vehicule.peut_avancer(
                    feux
            ):

                if vehicule.vehicule_devant(
                        vehicules
                ):

                    print(
                        "Véhicule",
                        vehicule.identifiant,
                        "arrêté derrière un autre véhicule."
                    )

                else:

                    vehicule.avancer(5)

            else:

                print(
                    "Véhicule",
                    vehicule.identifiant,
                    "arrêté pendant le passage du VP."
                )

        elif mode == "RETOUR_NORMAL":

            # Tous les feux sont encore rouges.
            # Les véhicules peuvent seulement :
            # - terminer leur passage s'ils étaient engagés
            # - ou avancer jusqu'à leur ligne de feu

            if vehicule.peut_avancer(
                    feux
            ):

                if vehicule.vehicule_devant(
                        vehicules
                ):

                    print(
                        "Véhicule",
                        vehicule.identifiant,
                        "arrêté derrière un autre véhicule."
                    )

                else:

                    vehicule.avancer(5)

            else:

                print(
                    "Véhicule",
                    vehicule.identifiant,
                    "attend le retour au fonctionnement normal."
                )


        # ==================================================
        # MODE SECURISATION
        # ==================================================

        elif mode == "SECURISATION":

            # Tous les feux sont rouges.
            #
            # peut_avancer() permet quand même :
            # - aux véhicules déjà engagés de sortir
            # - aux véhicules loin du feu de s'approcher

            if vehicule.peut_avancer(
                feux
            ):

                if vehicule.vehicule_devant(
                    vehicules
                ):

                    print(
                        "Véhicule",
                        vehicule.identifiant,
                        "arrêté derrière un autre véhicule."
                    )

                else:

                    vehicule.avancer(5)

            else:

                print(
                    "Véhicule",
                    vehicule.identifiant,
                    "arrêté pendant la sécurisation."
                )


        # ==================================================
        # MODE NORMAL
        # ==================================================

        else:

            if vehicule.peut_avancer(
                feux
            ):

                # Véhicule qui tourne à gauche :
                # vérifier les véhicules venant en face
                if vehicule.vehicule_en_face(
                    vehicules
                ):

                    print(
                        "Véhicule",
                        vehicule.identifiant,
                        "attend avant de tourner à gauche."
                    )


                # Vérification de la voiture devant
                elif vehicule.vehicule_devant(
                    vehicules
                ):

                    print(
                        "Véhicule",
                        vehicule.identifiant,
                        "arrêté derrière un autre véhicule."
                    )


                # Aucun obstacle
                else:

                    vehicule.avancer(5)


            else:

                print(
                    "Véhicule",
                    vehicule.identifiant,
                    "arrêté au feu."
                )


    # ==================================================
    # SUPPRESSION DES VEHICULES SORTIS
    # ==================================================

    vehicules_restants = []

    for vehicule in vehicules:

        if not vehicule.est_sorti():

            vehicules_restants.append(
                vehicule
            )

    vehicules = vehicules_restants


    # ==================================================
    # TEMPS
    # ==================================================

    time.sleep(1)


    # ==================================================
    # GESTION DU MODE NORMAL
    # ==================================================

    if mode == "NORMAL":

        compteur_phase += 1

        if compteur_phase >= feux.duree_phase():

            # Phases tous rouges
            if feux.phase == 2 or feux.phase == 5:

                if zone.est_libre(
                    vehicules
                ):

                    feux.phase_suivante()

                    compteur_phase = 0

                    print(
                        "\n>>> ZONE LIBRE : CHANGEMENT DE PHASE <<<"
                    )

                else:

                    print(
                        "\n>>> ZONE OCCUPEE : TOUS ROUGES MAINTENUS <<<"
                    )


            # Autres phases
            else:

                feux.phase_suivante()

                compteur_phase = 0

                print(
                    "\n>>> CHANGEMENT DE PHASE <<<"
                )


    # ==================================================
    # GESTION DU MODE SECURISATION
    # ==================================================

    elif mode == "SECURISATION":

        # On maintient tous les axes rouges
        feux.tous_rouges()


        # On vérifie réellement la position
        # des véhicules dans le carrefour
        if zone.est_libre(
            vehicules
        ):

            mode = "PRIORITE"

            feux.activer_priorite(
                vp_en_cours.axe
            )

            print(
                "\n>>> ZONE LIBRE <<<"
            )

            print(
                ">>> PRIORITE ACCORDEE AU VP - axe",
                vp_en_cours.axe,
                "<<<"
            )


        else:

            print(
                "\n>>> SECURISATION : ZONE ENCORE OCCUPEE <<<"
            )


    # ==================================================
    # GESTION DU MODE PRIORITE
    # ==================================================

    elif mode == "PRIORITE":

        # On maintient la priorité
        # uniquement sur l'entrée du VP
        feux.activer_priorite(
            vp_en_cours.axe
        )


    elif mode == "PASSAGE_VP":

        feux.desactiver_priorite()

        feux.tous_rouges()

        # Le VP doit avoir quitté la zone de conflit

        # ET la zone doit être complètement vide

        if (

                not zone.contient(vp_en_cours)

                and zone.est_libre(vehicules)

        ):
            mode = "RETOUR_NORMAL"

            compteur_retour = 0

            print(

                "\n>>> LE VP A LIBERE LA ZONE DE CONFLIT <<<"

            )

            print(

                ">>> PASSAGE EN MODE RETOUR_NORMAL <<<"

            )
    elif mode == "RETOUR_NORMAL":

        feux.desactiver_priorite()

        feux.tous_rouges()

        compteur_retour += 1

        # On garde un tour complet tous rouges
        if compteur_retour >= 1:

            # ==========================================
            # UN AUTRE VP ATTEND
            # ==========================================

            if len(vp_en_attente) > 0:

                vp_en_cours = vp_en_attente.pop(0)

                mode = "SECURISATION"

                compteur_phase = 0

                feux.desactiver_priorite()

                feux.tous_rouges()

                print(
                    "\n>>> LE PREMIER VP EST TERMINE <<<"
                )

                print(
                    ">>> VP EN ATTENTE PRIS EN CHARGE :",
                    vp_en_cours.type_vehicule,
                    "- axe",
                    vp_en_cours.axe,
                    "<<<"
                )

                print(
                    ">>> NOUVELLE SECURISATION <<<"
                )


            # ==========================================
            # AUCUN AUTRE VP
            # ==========================================

            else:

                feux.reinitialiser_cycle_normal()

                compteur_phase = 0

                mode = "NORMAL"

                vp_en_cours = None

                print(
                    "\n>>> RETOUR AU FONCTIONNEMENT NORMAL <<<"
                )