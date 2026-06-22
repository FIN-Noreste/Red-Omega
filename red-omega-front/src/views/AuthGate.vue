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
      <button @click="switchMode('login')" :class="{ active: mode === 'login' }">ENTRAR</button>
      <button @click="switchMode('import')" :class="{ active: mode === 'import' }">INYECCIÓN FÍSICA</button>
    </div>

    <div class="form-wrapper">
      <transition name="fade" mode="out-in">
        <div :key="mode">
          <div v-if="mode === 'login'" class="form-block">
            <div class="input-group">
              <label for="username-input">IDENTIDAD_</label>
              <input
                id="username-input"
                v-model="username"
                type="text"
                placeholder="Ingrese su alias..."
                autocomplete="username"
                autofocus
                @keyup.enter="handleLogin"
              />
            </div>
            <button class="action-btn" @click="handleLogin" :disabled="loading || !username.trim()">
              {{ loading ? 'VERIFICANDO FIRMA...' : 'INICIALIZAR CONEXIÓN' }}
            </button>
          </div>

          <div v-if="mode === 'import'" class="form-block">
            <div class="input-group">
              <label for="username-input-import">IDENTIDAD_</label>
              <input
                id="username-input-import"
                v-model="username"
                type="text"
                placeholder="Ingrese su alias..."
                autocomplete="username"
                @keyup.enter="handleLogin"
              />
            </div>
            <div class="input-group file-group">
              <label id="key-upload-label">LLAVE (.KEY)_</label>
              <div class="file-input-wrapper">
                <span class="file-status">{{ keyImported ? 'LLAVE CARGADA' : 'ESPERANDO ARCHIVO...' }}</span>
                <input
                  type="file"
                  @change="handleKeyUpload"
                  accept=".key,.txt"
                  aria-labelledby="key-upload-label"
                />
              </div>
            </div>
            <button class="action-btn" @click="handleLogin" :disabled="loading || !keyImported || !username.trim()">
              {{ loading ? 'ENCRIPTANDO...' : (keyImported ? 'AUTENTICAR' : 'REQUIERE LLAVE') }}
            </button>
          </div>
        </div>
      </transition>
    </div>

    <div v-if="error" class="error-log" role="alert">
      <span class="error-prefix">ERR ></span> {{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '../services/api';
import { signChallenge } from '../utils/crypto';

const mode = ref('login');
const username = ref('');
const error = ref('');
const loading = ref(false);
const keyImported = ref(false);

const emit = defineEmits(['authenticated']);

const switchMode = (target) => {
  mode.value = target;
  error.value = '';
};

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
  reader.onerror = () => {
    error.value = 'NO SE PUDO LEER EL ARCHIVO DE LLAVE.';
    keyImported.value = false;
  };
  reader.readAsText(file);
};

const handleLogin = async () => {
  // Guarda extra: si llegan aquí vía Enter en lugar de clic, el botón
  // pudo no haber bloqueado el envío (un <button disabled> no intercepta
  // el evento "enter" de un <input> hermano).
  if (loading.value) return;
  const trimmedUsername = username.value.trim();
  if (!trimmedUsername) {
    error.value = 'INGRESE UNA IDENTIDAD VÁLIDA.';
    return;
  }
  if (mode.value === 'import' && !keyImported.value) {
    error.value = 'CARGUE UNA LLAVE ANTES DE AUTENTICAR.';
    return;
  }

  error.value = '';
  loading.value = true;
  try {
    const challengeRes = await api.post('/auth/challenge', { username: trimmedUsername });
    const signatureHex = signChallenge(challengeRes.data.challenge);
    const verifyRes = await api.post('/auth/verify', { username: trimmedUsername, signature_hex: signatureHex });
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
/* Hereda tipografía/colores del sistema de skins definido en App.vue.
   Antes este componente traía su propia fuente (Space Mono) y colores
   fijos (#000/#fff/#d00000), así que la pantalla de login nunca cambiaba
   de aspecto aunque el usuario eligiera otro skin desde el Dashboard. */

.brutalist-container {
  max-width: 650px;
  margin: 5vh auto;
  background: var(--bg-panel);
  color: var(--text-main);
  font-family: var(--font-mono);
  box-shadow: var(--panel-shadow, 12px 12px 0px 0px rgba(0,0,0,1));
  border: var(--panel-border, 2px solid var(--border-color));
  border-radius: var(--radius-lg, 0);
  overflow: hidden;
}

.nfo-header {
  border-bottom: 2px solid var(--border-color);
  background: var(--bg-panel);
}

.ascii-art {
  margin: 0;
  font-size: 8px;
  line-height: 1;
  font-weight: bold;
  padding: 1.5rem 1rem;
  overflow-x: hidden;
  text-align: center;
  white-space: pre-wrap;
  color: var(--text-main);
}

.meta-info {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 1.5rem;
  border-top: 2px solid var(--border-color);
  background: var(--bg-main);
  font-size: 0.85rem;
  text-transform: uppercase;
}

.meta-label { font-weight: bold; color: var(--text-muted); }
.meta-value { font-weight: bold; }
.blink { animation: blinker 1.5s linear infinite; color: var(--highlight); }
@keyframes blinker { 50% { opacity: 0; } }

.tabs {
  display: flex;
  border-bottom: 2px solid var(--border-color);
}

.tabs button {
  flex: 1;
  background: var(--bg-panel);
  border: none;
  border-right: 2px solid var(--border-color);
  padding: 1rem;
  font-family: var(--font-mono);
  font-weight: bold;
  font-size: 1rem;
  color: var(--text-main);
  cursor: pointer;
  text-transform: uppercase;
  transition: all 0.2s ease;
}
.tabs button:last-child { border-right: none; }
.tabs button:hover { background: var(--bg-main); }
.tabs button.active { background: var(--highlight); color: #fff; }

.form-wrapper {
  padding: 2rem 1.5rem;
  background: var(--bg-panel);
}

.input-group { margin-bottom: 1.5rem; }

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
  font-family: var(--font-mono);
  font-size: 1rem;
  border: 2px solid var(--border-color);
  background: var(--bg-panel);
  color: var(--text-main);
  box-sizing: border-box;
  outline: none;
  border-radius: var(--radius-sm, 0);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input-group input[type="text"]:focus {
  border-color: var(--highlight);
  box-shadow: 4px 4px 0px 0px var(--highlight);
}

.file-group .file-input-wrapper {
  position: relative;
  border: 2px dashed var(--border-color);
  padding: 1.5rem;
  text-align: center;
  background: var(--bg-main);
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
  border-radius: var(--radius-sm, 0);
}

.file-group .file-input-wrapper:hover {
  background: var(--bg-panel);
  border-color: var(--highlight);
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
  background: var(--border-color);
  color: #fff;
  border: 2px solid var(--border-color);
  padding: 1rem;
  font-family: var(--font-mono);
  font-weight: bold;
  font-size: 1.1rem;
  cursor: pointer;
  text-transform: uppercase;
  transition: all 0.2s ease;
  margin-top: 1rem;
  border-radius: var(--radius-sm, 0);
}

.action-btn:hover:not(:disabled) {
  background: var(--highlight);
  border-color: var(--highlight);
  box-shadow: 6px 6px 0px 0px rgba(0,0,0,0.3);
  transform: translate(-2px, -2px);
}

.action-btn:active:not(:disabled) {
  transform: translate(2px, 2px);
  box-shadow: none;
}

.action-btn:disabled {
  background: var(--hairline);
  border-color: var(--hairline);
  color: var(--text-muted);
  cursor: not-allowed;
}

.error-log {
  background: var(--border-color);
  color: #fff;
  padding: 1rem 1.5rem;
  font-weight: bold;
  font-size: 0.9rem;
  border-top: 2px solid var(--border-color);
}

.error-prefix { color: var(--highlight); margin-right: 0.5rem; }

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-5px);
}

@media (max-width: 700px) {
  .brutalist-container { margin: 0; max-width: 100%; min-height: 100vh; }
  .ascii-art { font-size: 6px; }
}
</style>