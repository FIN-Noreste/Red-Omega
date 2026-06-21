<template>
  <div class="settings-container view-container">
    <div class="toolbar">
      <h2 class="view-title">PANEL DE CONTROL LOCAL</h2>
    </div>

    <div class="settings-layout">
      <nav class="settings-sidebar">
        <button @click="activeTab = 'general'" :class="{ active: activeTab === 'general' }">GENERAL</button>
        <button @click="activeTab = 'networks'" :class="{ active: activeTab === 'networks' }">FRECUENCIAS (REDES)</button>
        <button @click="activeTab = 'custom'" :class="{ active: activeTab === 'custom' }">PERSONALIZAR UI</button>
        <button @click="activeTab = 'panic'" :class="{ active: activeTab === 'panic' }" class="nav-danger">OPSEC / PÁNICO</button>
      </nav>

      <div class="settings-content">
        <!-- GENERAL -->
        <div v-if="activeTab === 'general'" class="tab-pane">
          <h3 class="section-header">AJUSTES DE NODO</h3>
          <div class="setting-item">
            <label>IDENTIDAD LOCAL ASIGNADA</label>
            <input type="text" :value="'@' + currentUser" disabled class="disabled-input" />
          </div>
        </div>

        <!-- FRECUENCIAS / REDES -->
        <div v-if="activeTab === 'networks'" class="tab-pane">
          <h3 class="section-header">GESTIÓN DE COLECTIVOS (ZERO-KNOWLEDGE)</h3>
          
          <div class="split-view">
            <!-- Columna Izquierda: Formulario para crear NUEVA red -->
            <div class="split-left">
              <h4 class="sub-header">FORJAR NUEVA FRECUENCIA</h4>
              <p class="doc-text">Crea un nuevo canal seguro. Deberás compartir manualmente la llave maestra con otros investigadores.</p>
              
              <div class="network-form">
                <div class="input-group">
                  <label>ID RED (ej: cybernetics_lab)</label>
                  <input v-model="createNetId" type="text" placeholder="Identificador corto único" />
                </div>
                <div class="input-group">
                  <label>NOMBRE MOSTRADO</label>
                  <input v-model="createNetName" type="text" placeholder="Laboratorio de Cibernética" />
                </div>
                <div class="input-group">
                  <label>LLAVE MAESTRA (GENERADA/CUSTOM)</label>
                  <div class="key-input-row">
                    <input v-model="createNetKey" type="text" placeholder="Llave criptográfica compartida" />
                    <button @click="generateRandomKey" class="action-btn small-btn" title="Generar llave segura">GEN</button>
                  </div>
                </div>
                <button @click="handleCreateNetwork" class="action-btn">FORJAR Y SINTONIZAR</button>
                <div v-if="createNetMsg" class="status-msg">{{ createNetMsg }}</div>
              </div>
            </div>

            <!-- Columna Derecha: Formulario para SINTONIZAR red existente -->
            <div class="split-right">
              <h4 class="sub-header">SINTONIZAR FRECUENCIA EXISTENTE</h4>
              <p class="doc-text">Inyecte los datos de una red creada por otro investigador para acceder a su contenido.</p>
              
              <div class="network-form">
                <div class="input-group">
                  <label>ID RED EXACTO</label>
                  <input v-model="netId" type="text" placeholder="Identificador corto" />
                </div>
                <div class="input-group">
                  <label>NOMBRE MOSTRADO (LOCAL)</label>
                  <input v-model="netName" type="text" placeholder="Alias local para la red" />
                </div>
                <div class="input-group">
                  <label>LLAVE MAESTRA PROVISTA</label>
                  <input v-model="netKey" type="password" placeholder="Pegue la llave aquí" />
                </div>
                <button @click="saveNetwork" class="action-btn">SINTONIZAR FRECUENCIA</button>
              </div>
            </div>
          </div>

          <!-- Tabla de Redes Sintonizadas -->
          <div class="tuned-networks">
            <h4 class="sub-header">FRECUENCIAS SINTONIZADAS ACTIVAS</h4>
            <table class="simple-table">
              <thead>
                <tr><th>ID</th><th>NOMBRE</th><th>LLAVE (COMPARTIR)</th><th>ACCIONES</th></tr>
              </thead>
              <tbody>
                <tr v-for="n in privateNetworks" :key="n.id">
                  <td>{{ n.id }}</td>
                  <td>{{ n.name }}</td>
                  <td>
                    <!-- Mostrar llave ofuscada con opción de copiar -->
                    <div class="key-display">
                      <span class="obfuscated-key">{{ maskKey(n.key) }}</span>
                      <button @click="copyToClipboard(n.key)" class="action-btn very-small-btn">COPIAR</button>
                    </div>
                  </td>
                  <td><button @click="deleteNetwork(n.id)" class="action-btn text-danger">BORRAR</button></td>
                </tr>
                <tr v-if="!privateNetworks.length">
                  <td colspan="4" class="empty-row">SIN FRECUENCIAS PRIVADAS REGISTRADAS</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- PERSONALIZAR UI -->
        <div v-if="activeTab === 'custom'" class="tab-pane">
          <h3 class="section-header">INYECCIÓN DE ESTILOS CSS</h3>
          <textarea v-model="customCssInput" class="css-editor" spellcheck="false"></textarea>
          <div class="action-row">
            <button @click="applyCss" class="action-btn">APLICAR CAMBIOS</button>
            <button @click="resetCss" class="action-btn text-danger">RESTAURAR DEFECTO</button>
          </div>
          <div v-if="cssMsg" class="status-msg">{{ cssMsg }}</div>
        </div>

        <!-- OPSEC / PÁNICO -->
        <div v-if="activeTab === 'panic'" class="tab-pane panic-zone">
          <h3 class="section-header text-danger">DIRECTIVA DE TIERRA ARRASADA</h3>
          <div class="panic-box">
            <button @click="triggerPanic" class="huge-panic-btn" :disabled="isPanicking">
              {{ isPanicking ? 'TX SOS...' : 'COMPROMISO DETECTADO' }}
            </button>
          </div>
          <div v-if="panicMsg" :class="['status-msg', { 'error-msg': panicMsg.includes('[ERR]') }]">{{ panicMsg }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { signChallenge } from '../utils/crypto';
import { useNetworks } from '../composables/useNetworks';

const props = defineProps(['currentUser']);

const API_URL = 'http://127.0.0.1:5000/api';
const API_PANIC_URL = `${API_URL}/network/panic`;

const activeTab = ref('networks');

const { privateNetworks, addNetwork, removeNetwork } = useNetworks();

// Sintonizar Existente
const netId = ref('');
const netName = ref('');
const netKey = ref('');

// Crear Nueva
const createNetId = ref('');
const createNetName = ref('');
const createNetKey = ref('');
const createNetMsg = ref('');

const customCssInput = ref('');
const cssMsg = ref('');

const isPanicking = ref(false);
const panicMsg = ref('');

const getAuthHeaders = () => {
  const token = localStorage.getItem('omega_jwt');
  return { Authorization: `Bearer ${token}` };
};

const saveNetwork = () => {
  if (!netId.value || !netKey.value) return;
  addNetwork(props.currentUser, { id: netId.value.toLowerCase(), name: netName.value || netId.value, key: netKey.value });
  netId.value = '';
  netName.value = '';
  netKey.value = '';
};

const handleCreateNetwork = () => {
  if (!createNetId.value || !createNetKey.value) {
      createNetMsg.value = "[-] ID y Llave son obligatorios.";
      return;
  }
  addNetwork(props.currentUser, { 
      id: createNetId.value.toLowerCase(), 
      name: createNetName.value || createNetId.value, 
      key: createNetKey.value 
  });
  createNetMsg.value = "[+] Frecuencia Forjada. Comparta la llave con otros nodos.";
  createNetId.value = '';
  createNetName.value = '';
  createNetKey.value = '';
  setTimeout(() => createNetMsg.value = '', 5000);
};

const generateRandomKey = () => {
    // Generar una llave aleatoria segura (64 chars hex) simulada
    const array = new Uint8Array(32);
    window.crypto.getRandomValues(array);
    createNetKey.value = Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
};

const deleteNetwork = (id) => {
    removeNetwork(props.currentUser, id);
};

const maskKey = (key) => {
    if(!key) return '';
    if(key.length <= 8) return '********';
    return `${key.substring(0, 4)}...${key.substring(key.length - 4)}`;
};

const copyToClipboard = async (text) => {
    try {
        await navigator.clipboard.writeText(text);
        alert("Llave copiada al portapapeles.");
    } catch (err) {
        console.error('Error al copiar: ', err);
    }
};

// CSS Management
const injectCss = (css) => {
  let styleEl = document.getElementById('omega-custom-css');
  if (!styleEl) {
    styleEl = document.createElement('style');
    styleEl.id = 'omega-custom-css';
    document.head.appendChild(styleEl);
  }
  styleEl.innerHTML = css;
};

const applyCss = () => {
  injectCss(customCssInput.value);
  localStorage.setItem('omega_custom_css', customCssInput.value);
  cssMsg.value = '[+] Estilos inyectados.';
  setTimeout(() => (cssMsg.value = ''), 3000);
};

const resetCss = () => {
  injectCss('');
  customCssInput.value = '';
  localStorage.removeItem('omega_custom_css');
  cssMsg.value = '[-] Estilos purgados.';
  setTimeout(() => (cssMsg.value = ''), 3000);
};

const triggerPanic = async () => {
  if (!confirm('¿CONFIRMAR ORDEN DE COMPROMISO A LA RED?')) return;

  isPanicking.value = true;
  panicMsg.value = '';

  try {
    const signature = signChallenge('EMERGENCY_ALERT');
    const res = await axios.post(API_PANIC_URL, { signature }, { headers: getAuthHeaders() });
    panicMsg.value = `[!!!] ${res.data.message}`;
  } catch (err) {
    panicMsg.value = `[ERR] Falla de transmisión: ${err.response?.data?.error || 'Red apagada.'}`;
  } finally {
    isPanicking.value = false;
  }
};

onMounted(() => {
  const savedCss = localStorage.getItem('omega_custom_css');
  if (savedCss) {
    customCssInput.value = savedCss;
    injectCss(savedCss);
  }
});
</script>

<style scoped>
/* HEREDA VARIABLES DE DASHBOARD */
.settings-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  font-family: var(--font-display);
}

.view-header {
  display: flex;
  align-items: center;
  padding: 0.3rem 0.7rem;
  background: var(--border-color);
  color: #fff;
}

.view-title {
  margin: 0;
  font-family: var(--font-display);
  font-size: 0.9rem;
  font-weight: bold;
  text-transform: uppercase;
}

.settings-layout { display: flex; flex: 1; min-height: 0; }

.settings-sidebar {
  width: 200px;
  flex-shrink: 0;
  background: var(--bg-main);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
}

.settings-sidebar button {
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 0.78rem;
  text-align: left;
  background: transparent;
  border: none;
  border-left: 3px solid transparent;
  border-bottom: 1px solid var(--hairline);
  padding: 0.6rem 0.8rem;
  color: var(--accent-blue);
  cursor: pointer;
}

.settings-sidebar button:hover { background: var(--bg-panel); }
.settings-sidebar button.active { background: var(--bg-panel); border-left-color: var(--border-color); color: var(--text-main); }
.settings-sidebar button.nav-danger { color: var(--highlight); }
.settings-sidebar button.nav-danger.active { border-left-color: var(--highlight); }

.settings-content { flex: 1; min-width: 0; padding: 1.5rem; background: var(--bg-panel); overflow-y: auto; }

.section-header {
  margin-top: 0;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.2rem;
  font-size: 1rem;
  text-transform: uppercase;
}

.sub-header {
    margin-top: 0;
    font-size: 0.85rem;
    text-transform: uppercase;
    border-bottom: 1px dashed var(--border-color);
    padding-bottom: 0.2rem;
}

.doc-text { color: var(--text-muted); font-size: 0.85rem; margin-bottom: 1.5rem; font-style: italic; }

.setting-item { margin-bottom: 1rem; font-family: var(--font-mono); }
.setting-item label { display: block; font-weight: 700; margin-bottom: 0.2rem; font-size: 0.75rem; text-transform: uppercase; }
.disabled-input {
  width: 100%;
  max-width: 400px;
  padding: 0.4rem;
  font-family: var(--font-mono);
  background: var(--bg-main);
  border: 1px solid var(--hairline);
  color: var(--text-muted);
  cursor: not-allowed;
}

/* REDES: VISTA DIVIDIDA */
.split-view {
    display: flex;
    gap: 2rem;
    margin-bottom: 2rem;
}
.split-left, .split-right {
    flex: 1;
    background: #f9f9f6;
    border: 1px solid var(--border-color);
    padding: 1rem;
    box-shadow: 2px 2px 0 0 rgba(0,0,0,0.1);
}

.network-form { max-width: 100%; }
.input-group { margin-bottom: 1rem; font-family: var(--font-mono); }
.input-group label { display: block; font-weight: 700; margin-bottom: 0.2rem; font-size: 0.75rem; text-transform: uppercase; }
.input-group input {
  width: 100%;
  padding: 0.4rem;
  border: 1px solid var(--border-color);
  font-family: inherit;
  font-size: 0.85rem;
  box-sizing: border-box;
  outline: none;
}
.input-group input:focus { border-color: var(--accent-blue); }

.key-input-row {
    display: flex;
    gap: 0.5rem;
}
.key-input-row input { flex-grow: 1; }

.tuned-networks { margin-top: 2rem; }

.simple-table {
  width: 100%;
  border-collapse: collapse;
  font-family: var(--font-mono);
  font-size: 0.8rem;
  margin-top: 0.5rem;
}
.simple-table th {
  text-align: left;
  padding: 0.3rem 0.5rem;
  border-bottom: 1px solid var(--border-color);
  font-weight: 700;
  text-transform: uppercase;
  font-size: 0.72rem;
  background: var(--bg-main);
}
.simple-table td { padding: 0.4rem 0.5rem; border-bottom: 1px solid var(--hairline); vertical-align: middle;}
.simple-table .empty-row { text-align: center; padding: 1.5rem; color: var(--text-muted); font-style: italic; }

.key-display { display: flex; align-items: center; gap: 1rem; }
.obfuscated-key { color: var(--text-muted); background: #eee; padding: 0.1rem 0.3rem; border: 1px solid #ccc; }

.text-green { color: var(--accent-green); font-weight: 700; }
.text-danger { color: var(--highlight); }

.css-editor {
  width: 100%;
  height: 200px;
  background: var(--bg-main);
  color: var(--text-main);
  font-family: var(--font-mono);
  font-size: 0.85rem;
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  box-sizing: border-box;
  outline: none;
}
.css-editor:focus { border-color: var(--accent-blue); }
.action-row { display: flex; gap: 0.5rem; margin-top: 0.5rem; }

/* BOTÓN RETRO */
.action-btn {
  background: #e7e6e0;
  color: var(--text-main);
  border: 1px solid var(--border-color);
  border-right: 2px solid var(--border-color);
  border-bottom: 2px solid var(--border-color);
  padding: 0.4rem 0.8rem;
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 0.78rem;
  cursor: pointer;
  text-transform: uppercase;
}
.action-btn:active {
  border: 1px solid var(--border-color);
  border-top: 2px solid var(--border-color);
  border-left: 2px solid var(--border-color);
  background: #ccc;
}
.action-btn:hover:not(:disabled) { background: #d7d6d0; }
.small-btn { padding: 0.2rem 0.5rem; font-size: 0.7rem; }
.very-small-btn { padding: 0.1rem 0.3rem; font-size: 0.6rem; border-width: 1px; border-right-width: 1px; border-bottom-width: 1px;}

.panic-zone { border: 2px dashed var(--highlight); padding: 1.5rem; background: #fcf6f5; }
.panic-box { text-align: center; margin-top: 1rem; }
.huge-panic-btn {
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-family: var(--font-mono);
  font-weight: 700;
  background: var(--highlight);
  color: #fff;
  border: 2px solid var(--highlight-hover);
  border-right-width: 4px;
  border-bottom-width: 4px;
  cursor: pointer;
  text-transform: uppercase;
}
.huge-panic-btn:active:not(:disabled) {
  border-width: 2px;
  border-top-width: 4px;
  border-left-width: 4px;
  background: var(--highlight-hover);
}
.huge-panic-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.status-msg {
  margin-top: 0.8rem;
  padding: 0.4rem 0.6rem;
  font-family: var(--font-mono);
  font-size: 0.78rem;
  font-weight: 700;
  border: 1px solid var(--accent-green);
  color: var(--accent-green);
}
.error-msg { border-color: var(--highlight); color: var(--highlight); }
</style>