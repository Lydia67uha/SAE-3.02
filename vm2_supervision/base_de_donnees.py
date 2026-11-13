import os
import sqlite3


# Base SQLite : le fichier carrefour.db est créé à côté de ce fichier.
# Table etats : l'état du carrefour à chaque tour (mode, nombre de véhicules).
# Table vehicules : chaque véhicule sorti de la simulation. Pour un véhicule
# prioritaire (VP), duree_passage donne le temps (en secondes) entre sa
# détection et sa sortie du carrefour.

FICHIER_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "carrefour.db")

# Les requêtes SQL affichées dans la fenêtre "Statistiques"
VUES = {
    "Passages des véhicules prioritaires": """
        SELECT numero AS "N° véhicule", type_vehicule AS "Type", entree AS "Entrée",
               manoeuvre AS "Manoeuvre", duree_passage AS "Durée de passage (s)",
               date_heure AS "Date"
        FROM vehicules
        WHERE prioritaire = 1
        ORDER BY id DESC LIMIT 200
    """,
    "Durée moyenne par type de VP": """
        SELECT type_vehicule AS "Type", COUNT(*) AS "Passages",
               ROUND(AVG(duree_passage), 1) AS "Durée moyenne (s)",
               MIN(duree_passage) AS "Minimum (s)", MAX(duree_passage) AS "Maximum (s)"
        FROM vehicules
        WHERE prioritaire = 1
        GROUP BY type_vehicule
    """,
    "Tous les véhicules": """
        SELECT numero AS "N° véhicule", type_vehicule AS "Type", entree AS "Entrée",
               manoeuvre AS "Manoeuvre", prioritaire AS "Prioritaire",
               duree_passage AS "Durée de passage (s)", date_heure AS "Date"
        FROM vehicules
        ORDER BY id DESC LIMIT 200
    """,
    "États du carrefour": """
        SELECT tour AS "Tour", mode AS "Mode", nombre_vehicules AS "Véhicules"
        FROM etats
        ORDER BY id DESC LIMIT 200
    """
}


def ouvrir():
    # Ouvre la base et crée les tables si elles n'existent pas encore
    bdd = sqlite3.connect(FICHIER_BASE)

    bdd.execute("""
        CREATE TABLE IF NOT EXISTS etats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tour INTEGER,
            mode VARCHAR(30),
            nombre_vehicules INTEGER
        )
    """)

    bdd.execute("""
        CREATE TABLE IF NOT EXISTS vehicules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero INTEGER,
            type_vehicule VARCHAR(30),
            entree VARCHAR(10),
            manoeuvre VARCHAR(12),
            prioritaire INTEGER,
            duree_passage REAL,
            date_heure TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    return bdd


def enregistrer_etat(tour, mode, nombre_vehicules):
    bdd = ouvrir()
    bdd.execute(
        "INSERT INTO etats (tour, mode, nombre_vehicules) VALUES (?, ?, ?)",
        (tour, mode, nombre_vehicules)
    )
    bdd.commit()
    bdd.close()


def enregistrer_vehicule(numero, type_vehicule, entree, manoeuvre, prioritaire, duree_passage):
    # duree_passage vaut None (NULL dans la base) pour un véhicule normal
    bdd = ouvrir()
    bdd.execute(
        "INSERT INTO vehicules (numero, type_vehicule, entree, manoeuvre, prioritaire, duree_passage)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        (numero, type_vehicule, entree, manoeuvre, int(prioritaire), duree_passage)
    )
    bdd.commit()
    bdd.close()


def statistiques_vp():
    # Retourne (nombre de passages, durée moyenne, minimum, maximum) des VP
    bdd = ouvrir()
    resultat = bdd.execute(
        "SELECT COUNT(duree_passage), AVG(duree_passage), MIN(duree_passage), MAX(duree_passage)"
        " FROM vehicules WHERE prioritaire = 1"
    ).fetchone()
    bdd.close()
    return resultat


def lire_vue(nom):
    # Retourne les noms des colonnes et les lignes d'une des requêtes de VUES
    bdd = ouvrir()
    curseur = bdd.execute(VUES[nom])
    colonnes = [colonne[0] for colonne in curseur.description]
    lignes = curseur.fetchall()
    bdd.close()
    return colonnes, lignes


def effacer_la_base():
    bdd = ouvrir()
    bdd.execute("DELETE FROM etats")
    bdd.execute("DELETE FROM vehicules")
    bdd.commit()
    bdd.close()
