<template>
  <div class="brutalist-container">
    <div class="nfo-header">
<pre class="ascii-art">
██████╗ ███████╗██████╗     ██████╗ ███╗   ███╗███████╗ ██████╗  █████╗ 
██╔══██╗██╔════╝██╔══██╗   ██╔═══██╗████╗ ████║██╔════╝██╔════╝ ██╔══██╗
██████╔╝█████╗  ██║  ██║   ██║   ██║██╔████╔██║█████╗  ██║  ███╗███████║
██╔══██╗██╔══╝  ██║  ██║   ██║   ██║██║╚██╔╝██║██╔══╝  ██║   ██║██╔══██║
██║  ██║███████╗██████╔╝██╗╚██████╔╝██║ ╚═╝ ██║███████╗╚██████╔╝██║  ██║
╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝
</pre>
      <div class="meta-info">
        <span class="meta-label">PROTOCOLO:</span> <span class="meta-value">ED25519 DESCENTRALIZADO</span>
        <span class="meta-label">ESTADO:</span> <span class="meta-value blink">ESPERANDO IDENTIDAD</span>
      </div>
    </div>

    <div class="tabs">
      <button @click="mode = 'login'" :class="{ active: mode === 'login' }">ENTRAR</button>
      <button @click="mode = 'import'" :class="{ active: mode === 'import' }">INYECCIÓN FÍSICA</button>
    </div>

    <div class="form-wrapper">
      <transition name="fade" mode="out-in">
        <!-- SOLUCIÓN: Agrupar ambos v-if dentro de un div contenedor -->
        <div :key="mode"> 
          <div v-if="mode === 'login'" class="form-block">
            <div class="input-group">
              <label>IDENTIDAD_</label>
              <input v-model="username" type="text" placeholder="Ingrese su alias..." />
            </div>
            <button class="action-btn" @click="handleLogin" :disabled="loading">
              {{ loading ? 'VERIFICANDO FIRMA...' : 'INICIALIZAR CONEXIÓN' }}
            </button>
          </div>

          <div v-if="mode === 'import'" class="form-block">
            <div class="input-group">
              <label>IDENTIDAD_</label>
              <input v-model="username" type="text" placeholder="Ingrese su alias..." />
            </div>
            <div class="input-group file-group">
              <label>LLAVE (.KEY)_</label>
              <div class="file-input-wrapper">
                <span class="file-status">{{ keyImported ? 'LLAVE CARGADA' : 'ESPERANDO ARCHIVO...' }}</span>
                <input type="file" @change="handleKeyUpload" accept=".key,.txt" />
              </div>
            </div>
            <button class="action-btn" @click="handleLogin" :disabled="loading || !keyImported">
              {{ loading ? 'ENCRIPTANDO...' : (keyImported ? 'AUTENTICAR' : 'REQUIERE LLAVE') }}
            </button>
          </div>
        </div>
      </transition>
    </div>

    <div v-if="error" class="error-log">
      <span class="error-prefix">ERR ></span> {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { signChallenge } from '../utils/crypto';

const API_URL = 'http://127.0.0.1:5000/api'; 
const mode = ref('login');
const username = ref(''); 
const error = ref('');
const loading = ref(false);
const keyImported = ref(false);

const emit = defineEmits(['authenticated']);

const handleKeyUpload = (event) => {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    const rawKey = e.target.result.trim();
    if (rawKey.length === 64) {
      localStorage.setItem('omega_priv_key', rawKey);
      keyImported.value = true;
      error.value = '';
    } else {
      error.value = 'LONGITUD DE LLAVE INCORRECTA.';
      keyImported.value = false;
    }
  };
  reader.readAsText(file);
};

const handleLogin = async () => {
  error.value = '';
  loading.value = true;
  try {
    const challengeRes = await axios.post(`${API_URL}/auth/challenge`, { username: username.value });
    const signatureHex = signChallenge(challengeRes.data.challenge);
    const verifyRes = await axios.post(`${API_URL}/auth/verify`, { username: username.value, signature_hex: signatureHex });
    localStorage.setItem('omega_jwt', verifyRes.data.token);
    emit('authenticated', verifyRes.data.username);
  } catch (err) {
    error.value = err.response?.data?.error || 'FIRMA RECHAZADA O NODO OFFLINE';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* ESTÉTICA BRUTALISTA / RETRO-TECH MINIMALISTA (Inspirado en Gucci Beauty Bamboo / Blood Source / AuctionWeb) */
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap');

.brutalist-container { 
  max-width: 650px; 
  margin: 5vh auto; 
  background: #fff; 
  color: #000;
  font-family: 'Space Mono', monospace;
  box-shadow: 12px 12px 0px 0px rgba(0,0,0,1);
  border: 2px solid #000;
  overflow: hidden;
}

.nfo-header {
  border-bottom: 2px solid #000;
  background: #fff;
}

.ascii-art {
  margin: 0;
  font-size: 8px; /* Ajustado para móviles/ventanas pequeñas */
  line-height: 1;
  font-weight: bold;
  padding: 1.5rem 1rem;
  overflow-x: hidden;
  text-align: center;
  white-space: pre-wrap; /* Permite wrapping si es muy largo */
  color: #000;
}

.meta-info {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 1.5rem;
  border-top: 2px solid #000;
  background: #f4f4f4;
  font-size: 0.85rem;
  text-transform: uppercase;
}

.meta-label { font-weight: bold; color: #555; }
.meta-value { font-weight: bold; }
.blink { animation: blinker 1.5s linear infinite; color: #d00000; }
@keyframes blinker { 50% { opacity: 0; } }

.tabs {
  display: flex;
  border-bottom: 2px solid #000;
}

.tabs button {
  flex: 1;
  background: #fff;
  border: none;
  border-right: 2px solid #000;
  padding: 1rem;
  font-family: 'Space Mono', monospace;
  font-weight: bold;
  font-size: 1rem;
  cursor: pointer;
  text-transform: uppercase;
  transition: all 0.2s ease;
}
.tabs button:last-child { border-right: none; }

.tabs button:hover { background: #f0f0f0; }

.tabs button.active {
  background: #d00000; /* HIGHLIGHT ROJO */
  color: #fff;
}

.form-wrapper {
  padding: 2rem 1.5rem;
  background: #fff;
}

.input-group {
  margin-bottom: 1.5rem;
}

.input-group label {
  display: block;
  font-weight: bold;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  text-transform: uppercase;
}

.input-group input[type="text"] {
  width: 100%;
  padding: 0.8rem;
  font-family: 'Space Mono', monospace;
  font-size: 1rem;
  border: 2px solid #000;
  background: #fff;
  box-sizing: border-box;
  outline: none;
  transition: border-color 0.2s;
}

.input-group input[type="text"]:focus {
  border-color: #d00000;
  box-shadow: 4px 4px 0px 0px #d00000;
}

.file-group .file-input-wrapper {
  position: relative;
  border: 2px dashed #000;
  padding: 1.5rem;
  text-align: center;
  background: #f9f9f9;
  cursor: pointer;
  transition: background 0.2s;
}

.file-group .file-input-wrapper:hover {
  background: #fff;
  border-color: #d00000;
}

.file-status {
  font-weight: bold;
  font-size: 0.9rem;
}

.file-group input[type="file"] {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  opacity: 0;
  cursor: pointer;
}

.action-btn {
  width: 100%;
  background: #000;
  color: #fff;
  border: 2px solid #000;
  padding: 1rem;
  font-family: 'Space Mono', monospace;
  font-weight: bold;
  font-size: 1.1rem;
  cursor: pointer;
  text-transform: uppercase;
  transition: all 0.2s ease;
  margin-top: 1rem;
}

.action-btn:hover:not(:disabled) {
  background: #d00000;
  border-color: #d00000;
  box-shadow: 6px 6px 0px 0px rgba(0,0,0,1);
  transform: translate(-2px, -2px);
}

.action-btn:active:not(:disabled) {
  transform: translate(2px, 2px);
  box-shadow: none;
}

.action-btn:disabled {
  background: #ccc;
  border-color: #999;
  color: #666;
  cursor: not-allowed;
}

.error-log {
  background: #000;
  color: #fff;
  padding: 1rem 1.5rem;
  font-weight: bold;
  font-size: 0.9rem;
  border-top: 2px solid #000;
}

.error-prefix { color: #d00000; margin-right: 0.5rem;}

/* Transiciones suaves */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-5px);
}
</style>
