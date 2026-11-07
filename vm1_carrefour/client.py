import socket
import json


IP_SERVEUR = "127.0.0.1"
PORT = 5000

client = None


def connecter():

    global client

    client = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    client.connect(
        (IP_SERVEUR, PORT)
    )

    print("Connexion au serveur réussie.")


def envoyer(message):

    message_json = json.dumps(message)

    client.sendall(
        (message_json + "\n").encode()
    )


def fermer():

    client.close()

    print("Connexion au serveur fermée.")