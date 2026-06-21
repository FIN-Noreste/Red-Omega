import { ed25519 } from '@noble/curves/ed25519';

// ==========================================
// HELPERS CRIPTOGRÁFICOS NATIVOS (ZERO DEPENDENCIES)
// ==========================================
const utf8ToBytes = (str) => new TextEncoder().encode(str);

const bytesToHex = (bytes) => 
  Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');

const hexToBytes = (hex) => {
  const bytes = new Uint8Array(hex.length / 2);
  for (let i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = parseInt(hex.substring(i, i + 2), 16);
  }
  return bytes;
};

// ==========================================
// MOTOR DE IDENTIDAD
// ==========================================

// Genera una nueva identidad y la guarda en el navegador
export function generateIdentity() {
    const privateKey = ed25519.utils.randomPrivateKey();
    const publicKey = ed25519.getPublicKey(privateKey);
    
    const privHex = bytesToHex(privateKey);
    const pubHex = bytesToHex(publicKey);

    // ATENCIÓN OPSEC: Guardar en localStorage
    localStorage.setItem('omega_priv_key', privHex);
    localStorage.setItem('omega_pub_key', pubHex);

    return pubHex;
}

// Firma un challenge del servidor
export function signChallenge(challengeString) {
    const privHex = localStorage.getItem('omega_priv_key');
    if (!privHex) throw new Error("No hay identidad criptográfica en este dispositivo");

    const challengeBytes = utf8ToBytes(challengeString);
    const signature = ed25519.sign(challengeBytes, hexToBytes(privHex));
    
    return bytesToHex(signature);
}

// Recupera la clave pública almacenada
export function getPublicKey() {
    return localStorage.getItem('omega_pub_key');
}