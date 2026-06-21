# backend/routes/vault.py
import os
import requests
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from config import LOCAL_IPFS_API
from core.database import save_archive, get_all_archives
from network.ipfs_client import upload_to_local_node, broadcast_to_swarm
from network.chat import EPHEMERAL_MEMORY, broadcast_ghost_message

vault_bp = Blueprint('vault', __name__)

@vault_bp.route("/upload", methods=["POST"])
@jwt_required()
def upload_file():
    current_user = get_jwt_identity()
    signature = request.form.get('signature', '')
    tags_raw = request.form.get('tags', '').strip()
    network_id = request.form.get('network_id', 'public')
    
    if 'file' not in request.files: 
        return jsonify({"error": "Payload vacío"}), 400
        
    file = request.files['file']
    real_filename = file.filename
    
    # PARCHE OPSEC: Si el archivo está encriptado, el nombre es Base64 y contiene '/'
    # IPFS colapsa si ve un '/', así que le pasamos un nombre genérico plano.
    safe_ipfs_name = "omega_block.bin" if network_id != 'public' else real_filename
    
    # Asignamos una extensión estática si está encriptado para no corromper la tabla
    _, ext = os.path.splitext(real_filename.lower())
    if network_id != 'public':
        ext = "ENC" 
    
    try:
        # 1. Inyectamos en IPFS usando el nombre seguro
        cid = upload_to_local_node(file.read(), safe_ipfs_name)
        
        # 2. Guardamos en SQLite usando el nombre encriptado REAL
        save_archive(cid, real_filename, current_user, ext, tags_raw, network_id)
        
        # 3. Transmitimos al enjambre
        payload_msg = {
            "author": current_user, "cid": cid, "filename": real_filename,
            "file_type": ext, "tags": tags_raw, "signature": signature,
            "network_id": network_id
        }
        broadcast_to_swarm(payload_msg)
        return jsonify({"message": "Transmitido a la red", "cid": cid}), 201
        
    except Exception as e:
        print(f"[!] ERROR CRÍTICO EN TRANSMISIÓN: {str(e)}") # Log visible en terminal
        return jsonify({"error": f"Fallo interno: {str(e)}"}), 500

@vault_bp.route("/files", methods=["GET"])
@jwt_required()
def get_files():
    return jsonify({"archivos": get_all_archives()}), 200

@vault_bp.route("/chat", methods=["GET"])
@jwt_required()
def get_chat():
    return jsonify(list(EPHEMERAL_MEMORY)), 200

@vault_bp.route("/chat", methods=["POST"])
@jwt_required()
def send_chat():
    payload_cifrado = request.json.get("payload")
    if not payload_cifrado: return jsonify({"error": "Payload vacío"}), 400
    broadcast_ghost_message(payload_cifrado)
    return jsonify({"status": "Transmitido al vacío"}), 200

@vault_bp.route("/ghost_drop", methods=["POST"])
@jwt_required()
def ghost_drop():
    if 'file' not in request.files:
        return jsonify({"error": "Payload vacío"}), 400
        
    file = request.files['file']
    
    try:
        files = {'file': ("ghost_drop.bin", file.read())} # Parcheado igual que arriba
        response = requests.post(f"{LOCAL_IPFS_API}/add", files=files)
        response.raise_for_status()
        
        cid = response.json().get("Hash")
        return jsonify({"message": "Drop inyectado", "cid": cid}), 201
    except Exception as e:
        return jsonify({"error": "Fallo en motor IPFS"}), 500