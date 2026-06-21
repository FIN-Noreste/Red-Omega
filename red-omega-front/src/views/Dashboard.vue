<template>
  <div class="silo-dashboard">
    <!-- BARRA SUPERIOR: solo identidad de sesión -->
    <header class="topbar">
      <div class="topbar-brand">
        <span class="brand-name">RED OMEGA</span>
        <span class="brand-version">v1.1.0</span>
      </div>
      <div class="topbar-session">
        <span class="session-user">@{{ currentUser.toUpperCase() }}</span>
        <button @click="logout" class="link-btn">[ SALIR ]</button>
      </div>
    </header>

    <div class="layout">
      <!-- SIDEBAR: navegación + estado del nodo + FRECUENCIAS EXTENSIBLES -->
      <aside class="sidebar">
        <nav class="sidebar-nav">
          <button @click="viewMode = 'table'" :class="{ active: viewMode === 'table' }">BÓVEDA</button>
          
          <!-- NUEVO: MENÚ EXPANDIBLE DE FRECUENCIAS -->
          <div class="expandable-menu">
            <button @click="toggleNetworks" class="expand-btn">
              FRECUENCIAS <span class="arrow" :class="{ 'arrow-down': showNetworks }">▶</span>
            </button>
            <div v-show="showNetworks" class="expanded-content">
              <button 
                v-for="net in privateNetworks" 
                :key="net.id"
                @click="openNetworkView(net)"
                :class="{ active: viewMode === 'network_hub' && currentNetwork?.id === net.id }"
                class="sub-nav-btn"
              >
                {{ net.name.toUpperCase() }}
              </button>
              <button v-if="!privateNetworks.length" class="sub-nav-btn disabled-btn">Sin sintonizar...</button>
            </div>
          </div>

          <button @click="viewMode = 'graph'" :class="{ active: viewMode === 'graph' }">CARTOGRAFÍA</button>
          <button @click="viewMode = 'editor'" :class="{ active: viewMode === 'editor' }">INTELIGENCIA</button>
          <button
            v-if="currentUser === 'admin'"
            @click="viewMode = 'admin'"
            :class="{ active: viewMode === 'admin' }"
            class="nav-danger"
          >CONSENSO</button>
          <button @click="viewMode = 'settings'" :class="{ active: viewMode === 'settings' }">AJUSTES</button>
          <button @click="viewMode = 'chat'" :class="{ active: viewMode === 'chat' }">GHOST CHAT</button>
        </nav>

        <div class="sidebar-status">
          <div class="status-line"><span class="status-dot"></span>ONLINE</div>
          <div class="status-label">NODE_ID</div>
          <div class="status-value">{{ shortCid(currentUser) }}</div>
          <div class="status-label">FECHA</div>
          <div class="status-value">{{ currentDate }}</div>
        </div>
      </aside>

      <!-- VISTA PRINCIPAL -->
      <main class="main-viewport">
        <transition name="slide-fade" mode="out-in">

          <!-- BÓVEDA GLOBAL: Muestra todos los archivos como antes -->
          <section v-if="viewMode === 'table'" key="table" class="view">
            <div class="view-header">
              <h2 class="view-title">REGISTRO DE BLOQUES GLOBAL</h2>
              <button @click="fetchFiles" class="link-btn">[ RECARGAR ]</button>
            </div>

            <div class="upload-bar">
              <input type="file" @change="handleFileSelect" accept=".pdf,.mp3" id="file-upload" class="hidden-input"/>
              <label for="file-upload" class="upload-label">
                {{ selectedFile ? selectedFile.name : 'SELECCIONAR ARCHIVO...' }}
              </label>

              <input v-model="uploadTags" type="text" placeholder="TAGS (ej: opsec, track)" class="tag-input" />

              <select v-model="selectedNetwork" class="network-selector">
                <option value="public">[ RED PÚBLICA ]</option>
                <option v-for="net in privateNetworks" :key="net.id" :value="net.id">
                  [ PRIVADA: {{ net.name.toUpperCase() }} ]
                </option>
              </select>

              <button class="action-btn upload-btn" @click="uploadFile" :disabled="!selectedFile || uploading">
                {{ uploading ? 'TX...' : 'TRANSMITIR' }}
              </button>
            </div>
            <div v-if="uploadMsg" :class="['status-msg', { 'error-msg': uploadMsg.includes('[-]') }]">{{ uploadMsg }}</div>
            <div v-if="loadingFiles" class="loading-state">ESCANEO DE RED EN PROGRESO...</div>

            <div v-else class="table-wrapper">
              <table class="data-table">
                <thead>
                  <tr>
                    <th class="col-ext">EXT</th>
                    <th class="col-name">IDENTIFICADOR</th>
                    <th class="col-origin">ORIGEN</th>
                    <th class="col-hash">HASH (CID)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="file in globalProcessedFiles" :key="file.cid" class="data-row">
                    <td class="col-ext"><span class="ext-tag">{{ file.ext }}</span></td>
                    <td class="col-name">
                      <span v-if="file.isPrivate" class="priv-tag" :title="file.network_id">PRIV</span>
                      <a @click.prevent="downloadFile(file)" class="filename-link" href="#">{{ file.filename }}</a>
                    </td>
                    <td class="col-origin">@{{ file.uploader }}</td>
                    <td class="col-hash">{{ shortCid(file.cid) }}</td>
                  </tr>
                  <tr v-if="!globalProcessedFiles.length">
                    <td colspan="4" class="empty-row">SIN BLOQUES DETECTADOS</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          <!-- NUEVA VISTA: HUB DE FRECUENCIA -->
          <section v-else-if="viewMode === 'network_hub' && currentNetwork" key="network_hub" class="view">
             <NetworkHub 
                :currentNetwork="currentNetwork" 
                :currentUser="currentUser"
                :files="globalProcessedFiles" 
             />
          </section>

          <!-- CARTOGRAFÍA: grafo 3D -->
          <section v-else-if="viewMode === 'graph'" key="graph" class="view">
            <div class="view-header">
              <h2 class="view-title">ANÁLISIS DE ENLACES ESPACIALES</h2>
            </div>
            <div class="graph-wrapper">
              <NetworkMap />
            </div>
          </section>

          <!-- CONSENSO: solo admin -->
          <section v-else-if="viewMode === 'admin' && currentUser === 'admin'" key="admin" class="view">
            <div class="view-header">
              <h2 class="view-title">PROPAGACIÓN DE IDENTIDADES</h2>
            </div>

            <div class="admin-panel">
              <div class="admin-card">
                <h3>INYECTAR NODO</h3>
                <p class="doc-text">Autoriza una nueva identidad matemática en la red P2P.</p>

                <div class="input-group">
                  <label>ALIAS_</label>
                  <input v-model="newUserName" type="text" placeholder="Ej: investigador_03" />
                </div>

                <div class="input-group">
                  <label>LLAVE PÚBLICA (HEX)_</label>
                  <input v-model="newUserPubKey" type="text" placeholder="String de 64 caracteres" />
                </div>

                <button class="action-btn" @click="addNodeToTrustlist" :disabled="addingNode">
                  {{ addingNode ? 'FIRMANDO ORDEN...' : 'DIFUNDIR AL ENJAMBRE' }}
                </button>
                <div v-if="consensusMsg" :class="['status-msg', { 'error-msg': consensusMsg.includes('[-]') }]">
                  {{ consensusMsg }}
                </div>
              </div>

              <div class="admin-card stats-card">
                <h3>MÉTRICAS DEL NODO</h3>
                <ul class="stats-list">
                  <li><span class="stat-label">BLOQUES LOCALES</span> <span class="stat-value">{{ files.length }}</span></li>
                  <li><span class="stat-label">PROTOCOLOS</span> <span class="stat-value">Ed25519 / Gossipsub</span></li>
                  <li><span class="stat-label">ESTADO RED</span> <span class="stat-value ok">ONLINE</span></li>
                </ul>
              </div>
            </div>
          </section>

          <section v-else-if="viewMode === 'editor'" key="editor" class="view">
            <Editor :currentUser="currentUser" />
          </section>

          <section v-else-if="viewMode === 'settings'" key="settings" class="view">
            <Settings :currentUser="currentUser" />
          </section>

          <section v-else-if="viewMode === 'chat'" key="chat" class="view">
            <GhostChat :currentUser="currentUser" />
          </section>

        </transition>
      </main>
    </div>
  </div>
</template>

<script setup>
import CryptoJS from 'crypto-js';
import { ref, onMounted, computed, watch } from 'vue';
import axios from 'axios';
import { signChallenge } from '../utils/crypto';
import NetworkMap from './NetworkMap.vue';
import Editor from './Editor.vue';
import Settings from './Settings.vue';
import GhostChat from './GhostChat.vue';
import NetworkHub from './NetworkHub.vue';
import { useNetworks } from '../composables/useNetworks';

const props = defineProps(['currentUser']);
const emit = defineEmits(['logout']);

const API_URL = 'http://127.0.0.1:5000/api';

// --- Estado: archivos ---
const files = ref([]);
const loadingFiles = ref(true);
const selectedFile = ref(null);
const uploading = ref(false);
const uploadTags = ref('');
const uploadMsg = ref('');

// --- Estado: panel admin ---
const newUserName = ref('');
const newUserPubKey = ref('');
const addingNode = ref(false);
const consensusMsg = ref('');

// --- Estado: redes y vista ---
const { privateNetworks, loadNetworksForUser } = useNetworks();
const selectedNetwork = ref('public');

// --- Control del Menú Expandible de Redes ---
const viewMode = ref('table');
const showNetworks = ref(false);
const currentNetwork = ref(null); 

const toggleNetworks = () => {
    showNetworks.value = !showNetworks.value;
};

const openNetworkView = (net) => {
    currentNetwork.value = net;
    viewMode.value = 'network_hub';
};

const currentDate = new Date()
  .toLocaleDateString('es-ES', { year: 'numeric', month: '2-digit', day: '2-digit' })
  .replace(/\//g, '.');

const getAuthHeaders = () => {
  const token = localStorage.getItem('omega_jwt');
  return { Authorization: `Bearer ${token}` };
};

const getExtension = (filename) => {
  const dotIndex = filename ? filename.lastIndexOf('.') : -1;
  if (dotIndex <= 0) return '???';
  return filename.slice(dotIndex + 1).toUpperCase();
};

// Computador Global: Procesa todos los archivos para la vista principal de la Bóveda y se lo pasa al Hub
const globalProcessedFiles = computed(() => {
  const visibleFiles = [];

  files.value.forEach((f) => {
    const isPrivate = f.network_id !== 'public';
    let decFilename = f.filename;
    let decTags = f.tags;

    if (!isPrivate) {
      visibleFiles.push({
        ...f,
        isPrivate: false,
        filename: decFilename,
        tagsDecrypted: decTags,
        ext: getExtension(decFilename),
      });
      return; 
    }

    const net = privateNetworks.value.find((n) => n.id === f.network_id);
    if (!net) return; 

    try {
      decFilename = CryptoJS.AES.decrypt(f.filename, net.key).toString(CryptoJS.enc.Utf8);
      decTags = CryptoJS.AES.decrypt(f.tags, net.key).toString(CryptoJS.enc.Utf8);
      
      if (!decFilename) throw new Error('Descifrado vacío');
      
      visibleFiles.push({
        ...f,
        isPrivate: true,
        filename: decFilename,
        tagsDecrypted: decTags,
        ext: getExtension(decFilename),
      });
    } catch (e) {
      return; 
    }
  });

  return visibleFiles;
});


const uploadFile = async () => {
  if (!selectedFile.value) return;
  uploading.value = true;

  const fileData = await new Promise((resolve) => {
    const reader = new FileReader();
    reader.readAsDataURL(selectedFile.value);
    reader.onload = (e) => resolve(e.target.result);
  });

  let uploadFilename = selectedFile.value.name;
  
  let uploadTagsString = uploadTags.value;
  if (typeof uploadTagsString !== 'string') {
      uploadTagsString = ''; 
  }
  let finalTags = uploadTagsString.trim().toLowerCase();
  
  let finalFileData = fileData;

  if (selectedNetwork.value !== 'public') {
    const net = privateNetworks.value.find((n) => n.id === selectedNetwork.value);
    if (net) {
      uploadFilename = CryptoJS.AES.encrypt(uploadFilename, net.key).toString();
      finalTags = CryptoJS.AES.encrypt(finalTags, net.key).toString();
      finalFileData = CryptoJS.AES.encrypt(fileData, net.key).toString();
    }
  }

  const formData = new FormData();
  formData.append('file', new Blob([finalFileData]), uploadFilename);
  formData.append('tags', finalTags);
  formData.append('network_id', selectedNetwork.value);
  
  try {
      const digitalSignature = signChallenge(`${uploadFilename}|${finalTags}`);
      formData.append('signature', digitalSignature);
  } catch (e) {
      uploadMsg.value = "[-] Error OpSec: Llave privada no encontrada.";
      uploading.value = false;
      return;
  }

  try {
    const res = await axios.post(`${API_URL}/network/upload`, formData, { headers: getAuthHeaders() });
    uploadMsg.value = `[+] TX OK. CID: ${shortCid(res.data.cid)}`;
    selectedFile.value = null;
    uploadTags.value = '';
    fetchFiles();
  } catch (err) {
    uploadMsg.value = '[-] Rechazado';
  } finally {
    uploading.value = false;
  }
};

const downloadFile = async (file) => {
  if (!file.isPrivate) {
    window.open(`http://127.0.0.1:8080/ipfs/${file.cid}`, '_blank');
    return;
  }

  const net = privateNetworks.value.find((n) => n.id === file.network_id);
  try {
    const res = await axios.get(`http://127.0.0.1:8080/ipfs/${file.cid}`, { responseType: 'text' });
    const decryptedBase64 = CryptoJS.AES.decrypt(res.data, net.key).toString(CryptoJS.enc.Utf8);

    const a = document.createElement('a');
    a.href = decryptedBase64;
    a.download = file.filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  } catch (e) {
    alert('Interferencia: La llave criptográfica es incorrecta o el bloque está corrupto.');
  }
};

const fetchFiles = async () => {
  loadingFiles.value = true;
  try {
    const res = await axios.get(`${API_URL}/network/files`, { headers: getAuthHeaders() });
    files.value = res.data.archivos;
  } catch (err) {
    console.error('Fallo al leer la red', err);
  } finally {
    loadingFiles.value = false;
  }
};

const handleFileSelect = (event) => {
  selectedFile.value = event.target.files[0];
};

const addNodeToTrustlist = async () => {
  if (!newUserName.value || !newUserPubKey.value) {
    consensusMsg.value = '[-] Faltan datos.';
    return;
  }

  addingNode.value = true;
  consensusMsg.value = '';

  try {
    const payloadToSign = `SYSTEM_TRUST_ADD|${newUserName.value.trim()}|${newUserPubKey.value.trim()}`;
    const signature = signChallenge(payloadToSign);

    const res = await axios.post(
      `${API_URL}/auth/system/trust/add`,
      {
        new_user: newUserName.value.trim(),
        new_pubkey: newUserPubKey.value.trim(),
        signature,
      },
      { headers: getAuthHeaders() }
    );

    consensusMsg.value = `[+] ${res.data.message}`;
    newUserName.value = '';
    newUserPubKey.value = '';
  } catch (err) {
    consensusMsg.value = `[-] Rechazado: ${err.response?.data?.error || 'Error P2P'}`;
  } finally {
    addingNode.value = false;
  }
};

const shortCid = (cid) => {
  if (!cid) return '';
  return `${cid.substring(0, 8)}...${cid.substring(cid.length - 8)}`;
};

const logout = () => {
  localStorage.removeItem('omega_jwt');
  emit('logout');
};

onMounted(() => {
  loadNetworksForUser(props.currentUser);
  fetchFiles();
});

watch(() => props.currentUser, (newVal) => {
  loadNetworksForUser(newVal);
});
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap');

/* ============================================================
   TOKENS
   ============================================================ */
.silo-dashboard {
  --bg-main: #f2f1ec;
  --bg-panel: #ffffff;
  --border-color: #111110;
  --hairline: #ded9cd;
  --text-main: #111110;
  --text-muted: #5c5c56;
  --highlight: #c4241b;
  --highlight-hover: #8f1a14;
  --accent-blue: #1414c2;
  --accent-green: #1d6e1d;
  --font-display: 'Times New Roman', Times, serif;
  --font-mono: 'JetBrains Mono', ui-monospace, 'SFMono-Regular', Menlo, Consolas, monospace;

  font-family: var(--font-display);
  background: var(--bg-main);
  color: var(--text-main);
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  font-size: 14px;
}

/* ============================================================
   BARRA SUPERIOR — solo identidad de sesión
   ============================================================ */
.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 36px;
  padding: 0 1rem;
  background: var(--border-color);
  color: #fff;
  position: sticky;
  top: 0;
  z-index: 100;
}

.topbar-brand { display: flex; align-items: baseline; gap: 0.5rem; }

.brand-name {
  font-family: var(--font-display);
  font-weight: bold;
  font-size: 1rem;
  letter-spacing: -0.3px;
}

.brand-version {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  border: 1px solid var(--highlight);
  color: var(--highlight);
  background: #fff;
  padding: 0 0.3rem;
}

.topbar-session {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-family: var(--font-mono);
  font-size: 0.75rem;
}

.session-user { font-weight: 700; }

.link-btn {
  background: none;
  border: none;
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 0.75rem;
  color: inherit;
  cursor: pointer;
  padding: 0;
}
.link-btn:hover { color: var(--highlight); }

/* ============================================================
   LAYOUT: sidebar + contenido
   ============================================================ */
.layout {
  flex-grow: 1;
  display: flex;
  justify-content: center;
  padding: 1rem;
  gap: 1rem;
}

/* ============================================================
   SIDEBAR — navegación + estado del nodo
   ============================================================ */
.sidebar {
  width: 190px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  box-shadow: 4px 4px 0 0 rgba(0, 0, 0, 0.15);
  height: fit-content;
}

.sidebar-nav { display: flex; flex-direction: column; }

.sidebar-nav button {
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 0.78rem;
  text-align: left;
  background: transparent;
  border: none;
  border-bottom: 1px solid var(--hairline);
  padding: 0.6rem 0.8rem;
  color: var(--accent-blue);
  cursor: pointer;
}

.sidebar-nav button:hover { background: var(--bg-main); }
.sidebar-nav button.active { background: var(--border-color); color: #fff; }
.sidebar-nav button.nav-danger { color: var(--highlight); }
.sidebar-nav button.nav-danger.active { background: var(--highlight); color: #fff; }

/* Menú Expandible de Redes */
.expandable-menu {
  display: flex;
  flex-direction: column;
  border-bottom: 1px solid var(--hairline);
}

.expand-btn {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: none !important; /* Sobreescribe el default del sidebar */
}

.arrow {
  font-size: 0.6rem;
  transition: transform 0.2s;
  color: var(--text-muted);
}
.arrow-down {
  transform: rotate(90deg);
}

.expanded-content {
  background: #fdfdfc;
  border-top: 1px dashed var(--hairline);
  display: flex;
  flex-direction: column;
}

.sub-nav-btn {
  padding-left: 1.5rem !important; /* Indentación visual */
  font-size: 0.72rem !important;
  color: var(--text-muted) !important;
}
.sub-nav-btn:hover { color: var(--accent-blue) !important;}
.sub-nav-btn.active { background: #eae9e4 !important; color: var(--text-main) !important; border-left: 3px solid var(--border-color) !important;}
.disabled-btn { cursor: default !important; font-style: italic; color: #999 !important;}
.disabled-btn:hover { background: transparent !important; color: #999 !important;}


.sidebar-status {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  padding: 0.8rem;
  border-top: 1px solid var(--border-color);
  background: var(--bg-main);
  color: var(--text-muted);
}

.status-line {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--accent-green);
  font-weight: 700;
  margin-bottom: 0.6rem;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent-green);
  box-shadow: 0 0 0 2px rgba(29, 110, 29, 0.15);
}

.status-label { text-transform: uppercase; letter-spacing: 0.5px; margin-top: 0.4rem; }
.status-value { color: var(--text-main); font-weight: 700; word-break: break-all; }

/* ============================================================
   CONTENIDO PRINCIPAL
   ============================================================ */
.main-viewport { flex-grow: 1; max-width: 1200px; }

.view {
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  box-shadow: 4px 4px 0 0 rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  min-height: 500px;
}

.view-header {
  display: flex;
  justify-content: space-between;
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

/* Headers específicos para los Hubs de Red */
.network-header { background: var(--text-main); border-bottom: 2px solid var(--highlight);}
.network-id-badge { font-family: var(--font-mono); font-size: 0.7rem; color: #aaa;}

.network-hub-content {
    flex-grow: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    background: var(--bg-main);
    padding: 2rem;
}
.hub-placeholder {
    text-align: center;
    border: 1px dashed var(--text-muted);
    padding: 2rem;
    max-width: 500px;
    background: var(--bg-panel);
}

/* ============================================================
   BARRA DE SUBIDA
   ============================================================ */
.upload-bar {
  display: flex;
  border-bottom: 1px solid var(--border-color);
  background: #f9f9f6;
  font-family: var(--font-mono);
  font-size: 0.78rem;
}

.hidden-input { display: none; }

.upload-label {
  flex: 1;
  padding: 0.5rem 1rem;
  cursor: pointer;
  color: var(--accent-blue);
  border-right: 1px solid var(--border-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.upload-label:hover { background: #eeede7; }

.tag-input {
  flex: 2;
  border: none;
  border-right: 1px solid var(--border-color);
  padding: 0.5rem 1rem;
  font-family: inherit;
  font-size: inherit;
  outline: none;
  background: transparent;
}
.tag-input:focus { background: #fff; }

.network-selector {
  border: none;
  border-right: 1px solid var(--border-color);
  background: transparent;
  padding: 0 1rem;
  font-family: inherit;
  font-weight: 700;
  font-size: 0.72rem;
  outline: none;
  color: var(--highlight);
  cursor: pointer;
}

.upload-btn { border: none; background: transparent; color: var(--highlight); font-weight: 700; padding: 0 1rem; }
.upload-btn:hover:not(:disabled) { background: var(--highlight); color: #fff; }

/* ============================================================
   TABLA DE DATOS
   ============================================================ */
.table-wrapper { flex-grow: 1; overflow-y: auto; padding: 0.5rem; }

.data-table { width: 100%; border-collapse: collapse; font-family: var(--font-mono); font-size: 0.8rem; }

.data-table th {
  text-align: left;
  padding: 0.3rem 0.5rem;
  border-bottom: 1px solid var(--border-color);
  font-weight: 700;
  text-transform: uppercase;
  font-size: 0.72rem;
  letter-spacing: 0.5px;
  background: var(--bg-main);
}

.col-ext { width: 8%; }
.col-name { width: 42%; }
.col-origin { width: 20%; font-style: italic; }
.col-hash { width: 30%; color: var(--text-muted); }

.data-row { border-bottom: 1px solid var(--hairline); }
.data-row:hover { background: #faf9f5; }
.data-row td { padding: 0.45rem 0.5rem; vertical-align: middle; }

.ext-tag {
  display: inline-block;
  border: 1px solid var(--text-muted);
  color: var(--text-muted);
  font-weight: 700;
  font-size: 0.68rem;
  padding: 0.05rem 0.3rem;
}

.priv-tag {
  display: inline-block;
  border: 1px solid var(--highlight);
  color: var(--highlight);
  font-size: 0.62rem;
  font-weight: 700;
  padding: 0.05rem 0.3rem;
  margin-right: 0.4rem;
  cursor: help;
}

.filename-locked {
  color: var(--highlight);
  background: #fcebe9;
  padding: 0.1rem 0.3rem;
  border: 1px dotted var(--highlight);
}

.filename-link { color: var(--accent-blue); text-decoration: underline; cursor: pointer; }
.filename-link:hover { color: var(--highlight); }

.empty-row { text-align: center; padding: 2rem; color: var(--text-muted); font-style: italic; }

/* ============================================================
   PANEL ADMIN
   ============================================================ */
.admin-panel { display: flex; padding: 1rem; gap: 1rem; background: var(--bg-main); flex-grow: 1; }

.admin-card {
  flex: 1;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  padding: 1.5rem;
  box-shadow: 2px 2px 0 0 rgba(0, 0, 0, 0.15);
}

.admin-card h3 {
  margin-top: 0;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.2rem;
  font-size: 1rem;
  text-transform: uppercase;
}

.doc-text { color: var(--text-muted); font-size: 0.85rem; margin-bottom: 1rem; }

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

.stats-list { list-style: none; padding: 0; margin: 0; font-family: var(--font-mono); font-size: 0.8rem; }
.stats-list li { display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px dotted var(--hairline); }
.stat-label { font-weight: 700; text-transform: uppercase; }
.stat-value.ok { color: var(--accent-green); font-weight: 700; }

/* ============================================================
   BOTONES
   ============================================================ */
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
.action-btn:disabled { color: #999; border-color: #ccc; background: #f0f0ee; cursor: not-allowed; }

/* ============================================================
   MENSAJES Y ESTADOS
   ============================================================ */
.status-msg {
  margin: 0.5rem 0.7rem 0;
  padding: 0.4rem 0.6rem;
  font-family: var(--font-mono);
  font-size: 0.78rem;
  font-weight: 700;
  border: 1px solid var(--accent-green);
  color: var(--accent-green);
}
.error-msg { border-color: var(--highlight); color: var(--highlight); }
.loading-state { padding: 2rem; text-align: center; font-style: italic; color: var(--text-muted); }

.graph-wrapper { flex-grow: 1; position: relative; background: #fff; padding: 2px; }

/* ============================================================
   TRANSICIONES
   ============================================================ */
.slide-fade-enter-active { transition: all 0.1s ease-out; }
.slide-fade-leave-active { transition: all 0.1s ease-in; }
.slide-fade-enter-from, .slide-fade-leave-to { opacity: 0; }

/* ============================================================
   RESPONSIVE
   ============================================================ */
@media (max-width: 800px) {
  .layout { flex-direction: column; }
  .sidebar { width: 100%; }
  .sidebar-nav { flex-direction: row; flex-wrap: wrap; }
  .sidebar-nav button { border-bottom: none; border-right: 1px solid var(--hairline); }
}
</style>