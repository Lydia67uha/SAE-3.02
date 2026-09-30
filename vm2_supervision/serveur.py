import socket
import json
import time

serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serveur.bind(("192.168.50.2", 5000))
serveur.listen()

print("Serveur en attente...")

client, adresse = serveur.accept()

print("VM1 connectée :", adresse)

# 1. Réception de la détection du VP
donnees = client.recv(1024).decode()
message = json.loads(donnees)

print("Type :", message["type"])
print("Axe :", message["axe"])


# 2. VM2 ordonne la sécurisation
reponse = {
    "type": "COMMANDE",
    "action": "TOUS_ROUGES"
}

client.send(json.dumps(reponse).encode())

print("Commande envoyée :", reponse["action"])


# 3. VM2 attend que la zone soit libre
donnees = client.recv(1024).decode()
message_zone = json.loads(donnees)

print("Message reçu :", message_zone["type"])


# 4. Si la zone est libre, on accorde la priorité
if message_zone["type"] == "ZONE_LIBRE":

    reponse = {
        "type": "COMMANDE",
        "action": "PRIORITE_ACCORDEE",
        "axe": message["axe"]
    }

    client.send(json.dumps(reponse).encode())

    print("Priorité accordée à l'axe :", message["axe"])


# 5. VM2 attend que le VP ait traversé
donnees = client.recv(1024).decode()
message_passage = json.loads(donnees)

print("Message reçu :", message_passage["type"])


# 6. Le VP est passé
if message_passage["type"] == "VP_PASSE":

    print("Le véhicule prioritaire a traversé.")

    print("Retour progressif vers le mode normal...")

    time.sleep(2)

    reponse = {
        "type": "COMMANDE",
        "action": "RETOUR_NORMAL"
    }

    client.send(json.dumps(reponse).encode())

    print("Commande envoyée : RETOUR_NORMAL")


client.close()
serveur.close()
