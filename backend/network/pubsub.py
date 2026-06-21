# backend/network/pubsub.py
import base64
import json
import requests
import time
from config import LOCAL_IPFS_API, PUBSUB_CHANNEL, TRUSTLIST
from core.crypto import verify_ed25519_signature
from core.database import save_archive

def pubsub_listener():
    print(f"[+] Hilo Centinela iniciado. Escuchando el canal: {PUBSUB_CHANNEL}")
    
    while True:
        try:
            response = requests.post(f"{LOCAL_IPFS_API}/pubsub/sub?arg={PUBSUB_CHANNEL}", stream=True, timeout=86400)
            for line in response.iter_lines():
                if not line: continue
                
                data = json.loads(line)
                encoded_payload = data.get("data", "")
                if not encoded_payload: continue
                
                decoded_text = base64.b64decode(encoded_payload).decode('utf-8')
                msg = json.loads(decoded_text)
                
                # Identificamos el TIPO de mensaje (Por defecto asumimos que es un archivo)
                msg_type = msg.get("type", "FILE_UPLOAD")
                author = msg.get("author")
                signature = msg.get("signature")

                # ====================================================
                # PROTOCOLO 1: ORDEN DEL SISTEMA (ACTUALIZAR TRUSTLIST)
                # ====================================================
                if msg_type == "SYSTEM_TRUST_ADD":
                    # Solo el root (admin) puede emitir esta orden
                    if author != "admin":
                        print(f"[-] Intento de usurpación bloqueado. @{author} intentó alterar el consenso.")
                        continue
                        
                    new_user = msg.get("new_user")
                    new_pubkey = msg.get("new_pubkey")
                    payload_str = f"SYSTEM_TRUST_ADD|{new_user}|{new_pubkey}"
                    
                    from config import TRUSTLIST, save_trustlist
                    
                    if verify_ed25519_signature(TRUSTLIST[author], signature, payload_str):
                        print(f"[+] ORDEN SUPREMA ACEPTADA: Asimilando nodo @{new_user}...")
                        TRUSTLIST[new_user] = new_pubkey
                        save_trustlist(TRUSTLIST)
                    else:
                        print("[-] ALERTA: Firma falsificada en orden de sistema.")
                    continue # Termina de procesar este mensaje

                elif msg_type == "GHOST_CHAT":
                    from network.chat import handle_ghost_message
                    handle_ghost_message(msg)
                    continue

                elif msg_type == "EMERGENCY_ALERT":
                    text = msg.get("text")
                    # Inyectar a la memoria RAM del chat para que todos lo vean
                    from network.chat import EPHEMERAL_MEMORY
                    EPHEMERAL_MEMORY.append({
                        "id": str(time.time()),
                        "payload": "SYSTEM_OVERRIDE",
                        "plain_text": text,
                        "is_panic": True
                    })
                    print(f"[!] ALERTA RECIBIDA DE @{author}: {text}")
                    continue

                elif msg_type == "FILE_UPLOAD":
                    cid, filename = msg.get("cid"), msg.get("filename")
                    file_type, tags = msg.get("file_type"), msg.get("tags", "")
                    network_id = msg.get("network_id", "public")
                    
                    from config import TRUSTLIST
                    if author not in TRUSTLIST:
                        print(f"[-] Spam bloqueado: {author}")
                        continue
                    
                    payload_str = f"{filename}|{tags}"
                    if verify_ed25519_signature(TRUSTLIST[author], signature, payload_str):
                        print(f"[+] Archivo validado de @{author} en red [{network_id.upper()}]. Indexando...")
                        from core.database import save_archive
                        save_archive(cid, filename, author, file_type, tags, network_id)
                    else:
                        print(f"[-] ALERTA: Firma falsificada detectada para @{author}.")
                        
        except requests.exceptions.RequestException:
            print("[-] Motor IPFS fuera de línea. Reintentando en 5s...")
            time.sleep(5)
        except Exception as e:
            print(f"[-] Error en el Centinela: {e}")
            time.sleep(2)