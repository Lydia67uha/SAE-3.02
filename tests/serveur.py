import socket

serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serveur.bind(("192.168.50.2", 5000))

serveur.listen()

print("Serveur en attente d'une connexion...")

client, adresse = serveur.accept()

message = client.recv(1024).decode()

print("Message reçu :", message)
client.send("Message bien reçu par VM2".encode())

client.close()
serveur.close()
