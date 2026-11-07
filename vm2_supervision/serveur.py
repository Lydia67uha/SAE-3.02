import socket
import json
import time
import sqlite3


def envoyer_json(client, message):
    donnees = json.dumps(message) + "\n"
    client.sendall(donnees.encode())


def recevoir_json(fichier_client):
    ligne = fichier_client.readline()

    if ligne == "":
        return None

    return json.loads(ligne)


serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

serveur.bind(("127.0.0.1", 5000))
serveur.listen()

bdd = sqlite3.connect("carrefour.db")

bdd.execute("""
CREATE TABLE IF NOT EXISTS etats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tour INTEGER,
    mode VARCHAR(30),
    nombre_vehicules INTEGER
)
""")

bdd.commit()

print("Serveur en attente...")

client, adresse = serveur.accept()

print("VM1 connectée :", adresse)

fichier_client = client.makefile("r", encoding="utf-8")

axe_courant = None


while True:

    message = recevoir_json(fichier_client)

    if message is None:
        print("VM1 s'est déconnectée.")
        break

    type_message = message["type"]

    print("Message reçu :", message)

    if type_message == "ETAT_CARREFOUR":

        nombre_vehicules = len(message["vehicules"])

        bdd.execute(
            "INSERT INTO etats (tour, mode, nombre_vehicules) VALUES (?, ?, ?)",
            (
                message["tour"],
                message["mode"],
                nombre_vehicules
            )
        )

        bdd.commit()

    if type_message == "VP_DETECTE":

        axe_courant = message["axe"]

        print("VP détecté sur l'axe :", axe_courant)

        reponse = {
            "type": "COMMANDE",
            "action": "TOUS_ROUGES"
        }

        envoyer_json(client, reponse)

        print("Commande envoyée : TOUS_ROUGES")


    elif type_message == "ZONE_LIBRE":

        reponse = {
            "type": "COMMANDE",
            "action": "PRIORITE_ACCORDEE",
            "axe": axe_courant
        }

        envoyer_json(client, reponse)

        print("Priorité accordée à :", axe_courant)


    elif type_message == "VP_PASSE":

        print("Le véhicule prioritaire est passé.")

        print("Retour progressif...")

        time.sleep(2)

        reponse = {
            "type": "COMMANDE",
            "action": "RETOUR_NORMAL"
        }

        envoyer_json(client, reponse)

        print("Retour au mode normal.")

        axe_courant = None


    elif type_message == "ARRET":

        print("Arrêt demandé par VM1.")

        break

bdd.close()
fichier_client.close()
client.close()
serveur.close()

print("Serveur arrêté.")
