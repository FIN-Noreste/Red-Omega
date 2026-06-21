# backend/network/chat.py
from collections import deque
import json
import time
from network.ipfs_client import broadcast_to_swarm

EPHEMERAL_MEMORY = deque(maxlen=50)

def handle_ghost_message(msg):
    """Atrapa los mensajes cifrados de la red y los mete en la memoria RAM."""
    payload_cifrado = msg.get("payload")
    if payload_cifrado:
        EPHEMERAL_MEMORY.append({
            "id": str(time.time()),
            "payload": payload_cifrado
        })

def broadcast_ghost_message(payload_cifrado):
    """Grita el mensaje cifrado al enjambre IPFS sin adjuntar identidad."""
    msg = {
        "type": "GHOST_CHAT",
        "payload": payload_cifrado
    }
    broadcast_to_swarm(msg)