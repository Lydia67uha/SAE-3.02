import socket
import json
import threading
import time
import sys


# Communication avec la supervision (VM2) par socket TCP.
# La simulation (VM1) est le CLIENT : elle se connecte à la supervision (VM2),
# qui est le serveur. Les messages sont des textes JSON, un par ligne.
# VM1 -> VM2 : l'état du carrefour (feux, véhicules...), à chaque tour
# VM2 -> VM1 : les commandes des boutons (VP, densité, reset)

# Adresse IP de la VM2. On peut aussi la donner au lancement :
#     python3 simulation.py 192.168.1.20
IP_SUPERVISION = "127.0.0.1"
PORT = 5000

client = None

# Commandes reçues de la supervision, en attente d'être lues par la simulation
commandes_recues = []


def connecter():
    global client

    ip = IP_SUPERVISION

    if len(sys.argv) > 1:
        ip = sys.argv[1]

    # On réessaie toutes les secondes tant que la supervision n'est pas lancée
    while True:
        try:
            client = socket.create_connection((ip, PORT), timeout=3)
            client.settimeout(None)
            break
        except OSError:
            print("Supervision introuvable (" + ip + ":" + str(PORT) + "), nouvel essai...")
            time.sleep(1)

    print("Connecté à la supervision :", ip)

    # Un thread écoute les commandes pendant que la simulation continue de tourner
    threading.Thread(target=ecouter, daemon=True).start()


def ecouter():
    # Lit les messages de la supervision, un par ligne
    try:
        for ligne in client.makefile("r", encoding="utf-8"):
            commandes_recues.append(json.loads(ligne))
    except OSError:
        pass


def lire_commandes():
    # Retourne les commandes reçues depuis le dernier appel
    # (on les retire une par une : le thread d'écoute peut en ajouter pendant ce temps)
    commandes = []

    while len(commandes_recues) > 0:
        commandes.append(commandes_recues.pop(0))

    return commandes


def envoyer(message):
    # Retourne False si la supervision a été fermée
    try:
        client.sendall((json.dumps(message) + "\n").encode())
        return True
    except OSError:
        return False


def fermer():
    client.close()
    print("Connexion fermée.")
