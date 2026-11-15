# SAE-3.02

SAE 3.02 - Développer une application communicante

GROUPE : Les Yodas

Participants : Akram FISICHELLA & Lydia KARA

## Le projet

Un carrefour à feux automatisé avec détection des véhicules prioritaires (VP : ambulance, police, pompiers...). Quand un VP arrive, tous les feux passent au rouge sauf celui de sa route. Une fois passé, le carrefour reprend son cycle normal.

Le projet tourne sur **deux machines virtuelles Linux** qui communiquent par un socket TCP (port 5000) :

| VM | Dossier | Rôle |
|---|---|---|
| VM1 | `vm1_carrefour` | La simulation : véhicules, feux, capteur de VP. C'est le **client** réseau. |
| VM2 | `vm2_supervision` | La supervision : interface graphique PyQt6, boutons, base de données SQLite. C'est le **serveur** réseau. |

La VM1 envoie l'état du carrefour à chaque tour. La VM2 envoie les ordres des boutons (VP, densité, réinitialisation).

## Ce qu'il faut avant de commencer

- Deux VM Debian 11, 12 ou 13 (Python 3.9 ou plus). Les deux VM ont un **environnement de bureau** (GNOME, Xfce...). Il est indispensable sur la VM2, car c'est elle qui affiche la fenêtre du carrefour.
- Les deux VM doivent avoir accès à internet pendant l'installation (paquets `apt` et `pip`).
- Dans VirtualBox, réseau de chaque VM en **Accès par pont** (Bridged Adapter), pas en NAT. Sinon les deux VM ne se voient pas.
- Un utilisateur qui a le droit d'utiliser `sudo`. Si `sudo` répond que l'utilisateur n'est pas dans le fichier sudoers :

```
su -
apt install -y sudo
usermod -aG sudo NOM_UTILISATEUR
reboot
```

(`su -` demande le mot de passe root. Il faut redémarrer ou rouvrir la session pour que le groupe soit pris en compte.)

## 1. Mettre le projet sur les deux VM

Il faut copier le projet (le fichier ZIP) sur **chaque** VM. Trois méthodes, au choix.

### Méthode A : télécharger le ZIP depuis Moodle directement dans la VM

Sur la VM, ouvrir le navigateur, se connecter à Moodle, télécharger le ZIP du projet. Il est enregistré dans `~/Téléchargements` (ou `~/Downloads` selon la langue du système).

```
cd ~/Téléchargements
```

Cette méthode demande un bureau et un navigateur sur la VM. Si une VM n'en a pas, utiliser la méthode B, ou copier le ZIP déjà téléchargé sur l'autre VM avec `scp -O` (voir la méthode B, la commande est la même depuis cette VM).

### Méthode B : depuis un PC Windows avec PowerShell (scp)

Sur la VM, installer le serveur SSH et relever son adresse IP :

```
sudo apt update
sudo apt install -y openssh-server openssh-sftp-server
sudo systemctl enable --now ssh
ip a
```

`ip a` liste les cartes réseau. Repérer la carte de la VM (souvent `enp0s3`, avec l'état `UP`) et lire la ligne `inet`, par exemple `inet 192.168.1.73/24`. L'adresse IP est la partie avant le `/24` : `192.168.1.73`. Ne pas prendre `127.0.0.1` (la carte `lo`) : c'est la VM elle-même.

Sur le PC, dans PowerShell, avec l'IP de la VM (par exemple `192.168.1.73`) :

```
scp -O C:\Users\VOTRE_NOM\Downloads\projet.zip utilisateur@192.168.1.73:~/
```

- Remplacer `projet.zip` par le vrai nom du ZIP et `utilisateur` par le nom d'utilisateur de la VM.
- À la première connexion, répondre `yes` à la question sur l'empreinte, puis taper le mot de passe de la VM.
- L'option `-O` évite l'erreur `subsystem request failed on channel 0` avec les versions récentes de scp.
- Si le message est `Connection refused`, le serveur SSH ne tourne pas : voir la partie Problèmes courants.

### Méthode C : avec git clone (si la VM a accès à GitHub)

```
sudo apt update
sudo apt install -y git
git clone https://github.com/Lydia67uha/SAE-3.02.git
cd SAE-3.02
```

Avec cette méthode, il n'y a pas de ZIP à décompresser : le dossier du projet s'appelle `SAE-3.02` (c'est le `NOM_DU_DOSSIER` de la suite). Passer directement à l'étape 2.

### Décompresser (méthodes A et B)

Dans le dossier où se trouve le ZIP (`~` avec la méthode A) :

```
sudo apt update
sudo apt install -y unzip
unzip projet.zip
ls
```

Le `ls` montre le nom du dossier créé (par exemple `SAE-3.02-main`). Il est appelé `NOM_DU_DOSSIER` dans la suite : le remplacer par le vrai nom.

## 2. VM2 : la supervision (à lancer en premier)

```
sudo apt install -y python3 python3-pip python3-venv libxcb-cursor0 netcat-openbsd
cd NOM_DU_DOSSIER
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
ip a
cd vm2_supervision
python3 interface.py
```

- `libxcb-cursor0` est nécessaire à PyQt6, sinon la fenêtre ne s'ouvre pas.
- L'environnement virtuel (`venv`) garde PyQt6 à part du système. `(venv)` doit apparaître au début de la ligne après le `source`.
- `ip a` donne l'adresse IP de la VM2 (la ligne `inet` de la carte `enp0s3` ou équivalente, sans le `/24`) : **la noter**, la VM1 en a besoin.
- La fenêtre du carrefour s'ouvre et le terminal affiche que la VM2 attend la simulation sur le port 5000. La laisser ouverte.
- Si Debian 13 (Wayland) refuse d'ouvrir la fenêtre, lancer plutôt : `QT_QPA_PLATFORM=xcb python3 interface.py`.
- Pour relancer l'interface plus tard : `cd NOM_DU_DOSSIER`, `source venv/bin/activate`, `cd vm2_supervision`, `python3 interface.py`.

Si un pare-feu est actif sur la VM2 (`ufw`, pas installé par défaut sur Debian) : `sudo ufw allow 5000/tcp`.

## 3. VM1 : la simulation

Rien à installer à part Python, qui est déjà présent sur Debian. La VM1 n'utilise aucune bibliothèque supplémentaire.

```
sudo apt install -y python3 netcat-openbsd
cd NOM_DU_DOSSIER/vm1_carrefour
ping -c 3 IP_DE_LA_VM2
nc -vz IP_DE_LA_VM2 5000
python3 simulation.py IP_DE_LA_VM2
```

- `ping` vérifie que les deux VM se voient.
- `nc -vz ... 5000` vérifie que le port de la VM2 est ouvert (il répond `open` ou `succeeded`). La VM2 doit déjà être lancée.
- Puis `simulation.py` se connecte à la VM2 : les véhicules apparaissent dans la fenêtre de la VM2.
- Si la VM2 n'est pas encore prête, la simulation réessaie toutes les secondes. L'ordre de lancement n'a donc pas d'importance.
- Sans adresse, `127.0.0.1` est utilisée. C'est utile pour tout tester sur **une seule machine** (deux terminaux, l'un avec `interface.py`, l'autre avec `python3 simulation.py`).

## Utilisation

Boutons de l'interface (VM2) :

- **Déclencher un VP** : crée un véhicule prioritaire.
- **Densité du trafic** : faible, moyenne ou forte.
- **Réinitialiser la simulation** : remet le carrefour à zéro si un bug le bloque.

Exemple complet de l'utilisation (la VM2 est lancée en premier, ici avec l'adresse `192.168.1.20`) :

```
# VM2 (supervision)
cd NOM_DU_DOSSIER/vm2_supervision
source ../venv/bin/activate
python3 interface.py

# VM1 (simulation)
cd NOM_DU_DOSSIER/vm1_carrefour
python3 simulation.py 192.168.1.20
```

Des VP apparaissent aussi tout seuls (5 % de chance par tour, et seulement s'il n'y en a pas déjà un sur la route). Les réglages sont en haut de `vm1_carrefour/simulation.py`.

## Base de données et statistiques

L'interface enregistre tout dans une base SQLite, `vm2_supervision/carrefour.db`, créée automatiquement au premier lancement. Elle contient deux tables :

- `etats` : l'état du carrefour à chaque tour (numéro du tour, mode, nombre de véhicules) ;
- `vehicules` : chaque véhicule sorti de la simulation (numéro, type, entrée, manoeuvre, prioritaire, `duree_passage`, date). Pour un VP, `duree_passage` est le temps en secondes entre sa détection par le capteur et sa sortie du carrefour. Elle est vide pour les véhicules normaux.

Les véhicules ne sont enregistrés que quand ils **sortent** de la simulation : au début, la table reste vide un moment.

**Dans l'interface** : le résumé des passages de VP est en bas à droite, et le bouton « Voir les statistiques... » ouvre une fenêtre avec les tableaux. Elle permet aussi d'effacer les statistiques.

**En dehors de l'interface**, sur la VM2, dans `vm2_supervision` :

- le script du projet affiche un extrait des tables : `python3 test_bdd.py` ;
- avec SQLite en ligne de commande :

```
sudo apt install -y sqlite3
sqlite3 carrefour.db
```

puis dans le programme :

```
.tables
.headers on
.mode column
SELECT * FROM vehicules WHERE prioritaire = 1 ORDER BY id DESC LIMIT 10;
SELECT type_vehicule, ROUND(AVG(duree_passage), 1) FROM vehicules WHERE prioritaire = 1 GROUP BY type_vehicule;
.quit
```

- avec une interface graphique : `sudo apt install -y sqlitebrowser`, puis `sqlitebrowser carrefour.db` (onglet « Parcourir les données »).

La date enregistrée est celle de la VM2 : si l'heure est fausse, régler le fuseau avec `timedatectl` puis `sudo timedatectl set-timezone Europe/Paris`. Si on change la table dans le code, supprimer l'ancien `carrefour.db` (interface fermée) pour qu'elle soit recréée.

Pour repartir de zéro : bouton « Effacer toutes les statistiques », ou supprimer `carrefour.db` interface fermée.

## Problèmes courants

| Ce qu'on voit | Ce qu'il faut faire |
|---|---|
| `X is not in the sudoers file` | Ajouter l'utilisateur au groupe sudo (voir plus haut), puis redémarrer la VM. |
| `Connection refused` avec `scp` | Le serveur SSH ne tourne pas : `sudo apt install -y openssh-server`, puis `sudo ssh-keygen -A` et `sudo systemctl restart ssh`. Vérifier avec `sudo systemctl status ssh`. |
| `subsystem request failed on channel 0` avec `scp` | Ajouter `-O` à la commande scp, ou installer `openssh-sftp-server` sur la VM. |
| La simulation répète « Supervision introuvable... nouvel essai » | Vérifier que `interface.py` tourne sur la VM2, que `ping` et `nc -vz IP 5000` marchent depuis la VM1, que les VM sont en Accès par pont, et que l'IP donnée est bien celle de la VM2. |
| `Could not load the Qt platform plugin "xcb"` | `sudo apt install -y libxcb-cursor0`, ou lancer avec `QT_QPA_PLATFORM=xcb python3 interface.py`. Vérifier aussi qu'on est bien sur le bureau de la VM et pas en SSH. |
| `No module named PyQt6` | L'environnement virtuel n'est pas activé : `source venv/bin/activate` (depuis `NOM_DU_DOSSIER`). |
| Le port 5000 est déjà utilisé | Une autre interface est encore ouverte : la fermer, ou redémarrer la VM2. |
| Un clavier QWERTY au lieu d'AZERTY | `setxkbmap fr` dans un terminal. |

## Organisation des fichiers

```
vm1_carrefour/        simulation (VM1)
  simulation.py       programme principal : tours, modes, VP, boutons
  vehicule.py         déplacement des véhicules, voies, virages, collisions
  feux.py             les feux et leur cycle
  generateur_trafic.py   création des véhicules
  capteur.py          détection des VP
  zone_conflit.py     le milieu du carrefour
  client.py           socket vers la VM2
  test_simulation.py  tests de la simulation
vm2_supervision/      supervision (VM2)
  interface.py        interface PyQt6 + serveur socket
  base_de_donnees.py  base SQLite et statistiques
  test_bdd.py         affiche le contenu de la base
tests/                premiers essais de socket du début du projet (ne servent plus)
requirements.txt      bibliothèque Python de la VM2 (PyQt6)
```
