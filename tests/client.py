import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect(("192.168.50.2", 5000))

client.send("Bonjour depuis VM1".encode())
reponse = client.recv(1024).decode()
print("Réponse du serveur :", reponse)

client.close()
