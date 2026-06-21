# backend/routes/auth.py
import secrets
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from config import TRUSTLIST
from core.crypto import verify_ed25519_signature
from network.ipfs_client import broadcast_to_swarm
from config import TRUSTLIST, save_trustlist
from flask_jwt_extended import jwt_required, get_jwt_identity
from network.ipfs_client import broadcast_to_swarm
from network.chat import EPHEMERAL_MEMORY
import time

auth_bp = Blueprint('auth', __name__)
PENDING_CHALLENGES = {}

@auth_bp.route("/system/panic", methods=["POST"])
@jwt_required()
def trigger_panic():
    current_user = get_jwt_identity()
    signature = request.json.get("signature")
    
    # El mensaje de pánico
    alert_text = f"¡ALERTA CRÍTICA! NODO @{current_user} COMPROMETIDO O EN PELIGRO."
    
    payload_msg = {
        "type": "EMERGENCY_ALERT",
        "author": current_user,
        "text": alert_text,
        "signature": signature
    }
    
    # 1. Gritar al enjambre
    broadcast_to_swarm(payload_msg)
    
    # 2. Inyectar directamente en la memoria local del Canal Fantasma para visibilidad inmediata
    EPHEMERAL_MEMORY.append({
        "id": str(time.time()),
        "payload": "SYSTEM_OVERRIDE", # Marcador especial
        "plain_text": alert_text,
        "is_panic": True
    })
    
    return jsonify({"message": "Señal de auxilio transmitida a todos los nodos."}), 200

@auth_bp.route("/challenge", methods=["POST"])
def get_challenge():
    username = request.json.get("username", "").strip()
    if username not in TRUSTLIST:
        return jsonify({"error": "Identidad no autorizada"}), 403

    challenge = secrets.token_hex(32)
    PENDING_CHALLENGES[username] = challenge
    return jsonify({"challenge": challenge})

@auth_bp.route("/verify", methods=["POST"])
def verify():
    data = request.json
    username, signature_hex = data.get("username", "").strip(), data.get("signature_hex", "").strip()

    challenge = PENDING_CHALLENGES.pop(username, None)
    if not challenge or username not in TRUSTLIST:
        return jsonify({"error": "Challenge inválido"}), 400

    if verify_ed25519_signature(TRUSTLIST[username], signature_hex, challenge):
        return jsonify({"token": create_access_token(identity=username), "username": username}), 200
    return jsonify({"error": "Firma rechazada"}), 401

@auth_bp.route("/system/trust/add", methods=["POST"])
@jwt_required()
def add_trusted_node():
    current_user = get_jwt_identity()
    
    if current_user != "admin":
        return jsonify({"error": "Acceso denegado. Se requiere nivel Root."}), 403

    new_user = request.json.get("new_user")
    new_pubkey = request.json.get("new_pubkey")
    signature = request.json.get("signature") # Tu frontend firmará la orden

    payload_msg = {
        "type": "SYSTEM_TRUST_ADD",
        "author": current_user,
        "new_user": new_user,
        "new_pubkey": new_pubkey,
        "signature": signature
    }
    
    broadcast_to_swarm(payload_msg)

    TRUSTLIST[new_user] = new_pubkey
    save_trustlist(TRUSTLIST)

    return jsonify({"message": f"Identidad @{new_user} inyectada en el consenso global."}), 200