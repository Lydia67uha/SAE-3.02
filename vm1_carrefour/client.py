import socket
import json
import time

etat_feux = {
    "nord_sud": "VERT",
    "est_ouest": "ROUGE",
    "pietons": "VERT"
}

vehicules_dans_zone = 3

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect(("192.168.50.2", 5000))


# 1. Détection du véhicule prioritaire
message = {
    "type": "VP_DETECTE",
    "axe": "NORD"
}

client.send(json.dumps(message).encode())

print("VP détecté sur l'axe NORD.")


# 2. Réception de TOUS_ROUGES
donnees = client.recv(1024).decode()
reponse = json.loads(donnees)

print("Action reçue :", reponse["action"])


if reponse["action"] == "TOUS_ROUGES":

    etat_feux["nord_sud"] = "ROUGE"
    etat_feux["est_ouest"] = "ROUGE"
    etat_feux["pietons"] = "ROUGE"

    print("Tous les feux sont rouges.")


# 3. Les véhicules déjà engagés quittent le carrefour
while vehicules_dans_zone > 0:

    print(
        "Véhicules encore dans la zone :",
        vehicules_dans_zone
    )

    time.sleep(1)

    vehicules_dans_zone = vehicules_dans_zone - 1


print("Zone libre.")


# 4. On informe VM2
message_zone = {
    "type": "ZONE_LIBRE"
}

client.send(json.dumps(message_zone).encode())


# 5. On attend l'autorisation de priorité
donnees = client.recv(1024).decode()
reponse = json.loads(donnees)

print("Action reçue :", reponse["action"])


# 6. On donne le vert au VP
if reponse["action"] == "PRIORITE_ACCORDEE":

    axe = reponse["axe"]

    if axe == "NORD" or axe == "SUD":

        etat_feux["nord_sud"] = "VERT"
        etat_feux["est_ouest"] = "ROUGE"

    elif axe == "EST" or axe == "OUEST":

        etat_feux["nord_sud"] = "ROUGE"
        etat_feux["est_ouest"] = "VERT"

    etat_feux["pietons"] = "ROUGE"

    print("Priorité accordée.")

    print("Nord/Sud :", etat_feux["nord_sud"])
    print("Est/Ouest :", etat_feux["est_ouest"])
    print("Piétons :", etat_feux["pietons"])


# 7. Simulation du passage du VP
print("Le véhicule prioritaire traverse...")

time.sleep(3)

print("Le véhicule prioritaire est passé.")


# 8. VM1 informe VM2
message_passage = {
    "type": "VP_PASSE"
}

client.send(json.dumps(message_passage).encode())


# 9. VM1 attend le retour normal
donnees = client.recv(1024).decode()
reponse = json.loads(donnees)

print("Action reçue :", reponse["action"])


# 10. Retour au mode normal
if reponse["action"] == "RETOUR_NORMAL":

    etat_feux["nord_sud"] = "VERT"
    etat_feux["est_ouest"] = "ROUGE"
    etat_feux["pietons"] = "VERT"

    print("Retour au mode normal.")

    print("Nord/Sud :", etat_feux["nord_sud"])
    print("Est/Ouest :", etat_feux["est_ouest"])
    print("Piétons :", etat_feux["pietons"])


client.close()
