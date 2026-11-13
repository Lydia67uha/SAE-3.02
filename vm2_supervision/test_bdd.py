# Fichier de test pour vérifier le contenu de la base SQLite (lancer depuis ce dossier)
import sqlite3

bdd = sqlite3.connect("carrefour.db")

print("--- Les 5 derniers états du carrefour (table etats)")
for ligne in bdd.execute("SELECT * FROM etats ORDER BY id DESC LIMIT 5"):
    print(ligne)

print("--- Les 10 derniers véhicules prioritaires (table vehicules)")
for ligne in bdd.execute("SELECT * FROM vehicules WHERE prioritaire = 1 ORDER BY id DESC LIMIT 10"):
    print(ligne)

print("--- Durée moyenne de passage par type de VP")
for ligne in bdd.execute(
    "SELECT type_vehicule, COUNT(*), ROUND(AVG(duree_passage), 1) "
    "FROM vehicules WHERE prioritaire = 1 GROUP BY type_vehicule"
):
    print(ligne)

bdd.close()
