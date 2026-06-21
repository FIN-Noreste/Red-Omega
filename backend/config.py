# backend/config.py
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "fin_vault.db")
TRUSTLIST_PATH = os.path.join(BASE_DIR, "trustlist.json")

JWT_SECRET_KEY = "omega_bunker_llave_maestra_2026_secreta"
JWT_EXPIRATION = 28800  # 8 horas
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB

LOCAL_IPFS_API = "http://127.0.0.1:5001/api/v0"
PUBSUB_CHANNEL = "omega_dark_channel"

def load_trustlist():
    try:
        with open(TRUSTLIST_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("[-] ALERTA CRÍTICA: Archivo trustlist.json no encontrado.")
        return {}

# Añade esto al final de backend/config.py
def save_trustlist(new_list):
    """Sobreescribe el archivo físico y actualiza la memoria RAM"""
    global TRUSTLIST
    try:
        with open(TRUSTLIST_PATH, "w") as f:
            json.dump(new_list, f, indent=4)
        TRUSTLIST = new_list
        print(f"[+] CONSENSO ACTUALIZADO: {len(TRUSTLIST)} identidades en el enjambre.")
    except Exception as e:
        print(f"[-] ERROR FATAL AL ESCRIBIR TRUSTLIST: {e}")

TRUSTLIST = load_trustlist()