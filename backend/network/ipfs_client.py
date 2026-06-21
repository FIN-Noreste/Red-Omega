# backend/network/ipfs_client.py
import requests
import json
from config import LOCAL_IPFS_API, PUBSUB_CHANNEL

def upload_to_local_node(file_bytes, filename):
    files = {'file': (filename, file_bytes)}
    response = requests.post(f"{LOCAL_IPFS_API}/add", files=files)
    response.raise_for_status()
    return response.json().get("Hash")

def broadcast_to_swarm(payload_dict):
    msg_str = json.dumps(payload_dict)
    requests.post(f"{LOCAL_IPFS_API}/pubsub/pub?arg={PUBSUB_CHANNEL}", files={'file': msg_str.encode()})