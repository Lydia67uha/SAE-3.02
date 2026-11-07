# Fichier de test pour vérifier le contenu de la base SQLite
import sqlite3

bdd = sqlite3.connect("carrefour.db")

resultats = bdd.execute("SELECT * FROM etats")

for ligne in resultats:
    print(ligne)

bdd.close()