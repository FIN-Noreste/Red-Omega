<template>
  <div class="silo-dashboard">
    <!-- BARRA SUPERIOR: solo identidad de sesión -->
    <header class="topbar">
      <div class="topbar-brand">
        <span class="brand-name">RED OMEGA</span>
        <span class="brand-version">v1.2.0</span>
      </div>
      <div class="topbar-session">
        <!-- Control de Skins -->
        <select v-model="currentSkin" @change="applySkin" class="skin-selector" aria-label="Seleccionar tema visual">
          <option value="brutalist">Brutalist (Default)</option>
          <option value="material">Material Design</option>
          <option value="flat">Flat Design</option>
          <option value="light">F.I.N Light</option>
          <option value="dark">F.I.N Dark</option>
        </select>
        <span class="session-user">@{{ currentUser.toUpperCase() }}</span>
        <button @click="logout" class="link-btn">[ SALIR ]</button>
      </div>
    </header>

    <div class="layout">
      <!-- SIDEBAR: navegación + estado del nodo + FRECUENCIAS EXTENSIBLES -->
      <aside class="sidebar">
        <nav class="sidebar-nav">
          <button @click="viewMode = 'table'" :class="{ active: viewMode === 'table' }">BÓVEDA</button>

          <!-- MENÚ EXPANDIBLE DE FRECUENCIAS -->
          <div class="expandable-menu">
            <button @click="toggleNetworks" class="expand-btn" :aria-expanded="showNetworks">
              FRECUENCIAS <span class="arrow" :class="{ 'arrow-down': showNetworks }">▶</span>
            </button>
            <div v-show="showNetworks" class="expanded-content">
              <!-- Botón Red Pública -->
              <button
                @click="openPublicNetwork"
                :class="{ active: viewMode === 'table' && currentNetworkId === 'public' }"
                class="sub-nav-btn public-btn"
              >
                [ RED PÚBLICA ]
              </button>

              <!-- Botones Redes Privadas -->
              <button
                v-for="net in privateNetworks"
                :key="net.id"
                @click="openNetworkView(net)"
                :class="{ active: viewMode === 'network_hub' && currentNetwork?.id === net.id }"
                class="sub-nav-btn"
              >
                {{ net.name.toUpperCase() }}
              </button>
              <button v-if="!privateNetworks.length" class="sub-nav-btn disabled-btn" disabled>Sin sintonizar...</button>
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

          <!-- BÓVEDA GLOBAL / PÚBLICA -->
          <section v-if="viewMode === 'table'" key="table" class="view">
            <div class="view-header">
              <h2 class="view-title">REGISTRO DE BLOQUES GLOBAL</h2>
              <div class="header-actions">
                <input
                  v-model="searchQuery"
                  type="text"
                  placeholder="Filtrar por nombre, tag o nodo..."
                  class="filter-input"
                  aria-label="Filtrar bloques"
                />
                <button @click="fetchFiles" class="link-btn">[ RECARGAR ]</button>
              </div>
            </div>

            <div class="upload-bar">
              <input type="file" @change="handleFileSelect" accept=".pdf,.mp3" id="file-upload" class="hidden-input"/>
              <label for="file-upload" class="upload-label">
                {{ selectedFile ? selectedFile.name : 'SELECCIONAR ARCHIVO...' }}
              </label>

              <input v-model="uploadTags" type="text" placeholder="TAGS (ej: opsec, track)" class="tag-input" />

              <select v-model="selectedNetwork" class="network-selector" aria-label="Red de destino">
                <option value="public">[ RED PÚBLICA ]</option>
                <option v-for="net in privateNetworks" :key="net.id" :value="net.id">
                  [ PRIVADA: {{ net.name.toUpperCase() }} ]
                </option>
              </select>

              <button class="action-btn upload-btn" @click="uploadFile" :disabled="!selectedFile || uploading">
                <span v-if="uploading" class="spinner" aria-hidden="true"></span>
                {{ uploading ? 'TX...' : 'TRANSMITIR' }}
              </button>
            </div>
            <div v-if="uploadMsg" :class="['status-msg', { 'error-msg': uploadMsg.includes('[-]') }]">{{ uploadMsg }}</div>
            <div v-if="loadingFiles" class="loading-state"><span class="spinner" aria-hidden="true"></span>ESCANEO DE RED EN PROGRESO...</div>

            <div v-else class="table-wrapper">
              <table class="data-table">
                <thead>
                  <tr>
                    <th class="col-ext">EXT</th>
                    <th class="col-name">IDENTIFICADOR</th>
                    <th class="col-tags">TAGS</th>
                    <th class="col-origin">ORIGEN</th>
                    <th class="col-hash">HASH (CID)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="file in filteredFiles" :key="file.cid" class="data-row">
                    <td class="col-ext"><span class="ext-tag">{{ file.ext }}</span></td>
                    <td class="col-name">
                      <span v-if="file.isPrivate" class="priv-tag" :title="file.network_id">PRIV</span>
                      <a @click.prevent="downloadFile(file)" class="filename-link" href="#">{{ file.filename }}</a>
                    </td>
                    <td class="col-tags">{{ file.tagsDecrypted || '—' }}</td>
                    <td class="col-origin">@{{ file.uploader }}</td>
                    <td class="col-hash">{{ shortCid(file.cid) }}</td>
                  </tr>
                  <tr v-if="!filteredFiles.length">
                    <td colspan="5" class="empty-row">
                      {{ searchQuery ? 'SIN COINCIDENCIAS PARA EL FILTRO ACTUAL' : 'SIN BLOQUES DETECTADOS' }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          <!-- HUB DE FRECUENCIA PRIVADA -->
          <section v-else-if="viewMode === 'network_hub' && currentNetwork" key="network_hub" class="view">
             <NetworkHub
                :key="currentNetwork.id"
                :currentNetwork="currentNetwork"
                :currentUser="currentUser"
                :files="globalProcessedFiles"
                @refresh-requested="fetchFiles"
             />
          </section>

          <!-- CARTOGRAFÍA -->
          <section v-else-if="viewMode === 'graph'" key="graph" class="view">
            <div class="view-header">
              <h2 class="view-title">ANÁLISIS DE ENLACES ESPACIALES</h2>
            </div>
            <div class="graph-wrapper">
              <NetworkMap />
            </div>
          </section>

          <!-- CONSENSO -->
          <section v-else-if="viewMode === 'admin' && currentUser === 'admin'" key="admin" class="view">
            <div class="view-header">
              <h2 class="view-title">PROPAGACIÓN DE IDENTIDADES</h2>
            </div>

            <div class="admin-panel">
              <div class="admin-card">
                <h3>INYECTAR NODO</h3>
                <p class="doc-text">Autoriza una nueva identidad matemática en la red P2P.</p>

                <div class="input-group">
                  <label for="new-user-alias">ALIAS_</label>
                  <input id="new-user-alias" v-model="newUserName" type="text" placeholder="Ej: investigador_03" />
                </div>

                <div class="input-group">
                  <label for="new-user-pubkey">LLAVE PÚBLICA (HEX)_</label>
                  <input id="new-user-pubkey" v-model="newUserPubKey" type="text" placeholder="String de 64 caracteres" />
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
import api, { IPFS_GATEWAY_URL } from '../services/api';
import { shortCid, getFileExtension } from '../utils/format';
import { signChallenge } from '../utils/crypto';
import NetworkMap from './NetworkMap.vue';
import Editor from './Editor.vue';
import Settings from './Settings.vue';
import GhostChat from './GhostChat.vue';
import NetworkHub from './NetworkHub.vue';
import { useNetworks } from '../composables/useNetworks';

const props = defineProps(['currentUser']);
const emit = defineEmits(['logout']);

const files = ref([]);
const loadingFiles = ref(true);
const selectedFile = ref(null);
const uploading = ref(false);
const uploadTags = ref('');
const uploadMsg = ref('');
const searchQuery = ref('');

const newUserName = ref('');
const newUserPubKey = ref('');
const addingNode = ref(false);
const consensusMsg = ref('');

const { privateNetworks, loadNetworksForUser } = useNetworks();
const selectedNetwork = ref('public');

const viewMode = ref('table');
const showNetworks = ref(false);
const currentNetwork = ref(null);
const currentNetworkId = ref('public');

const currentSkin = ref('brutalist');

const toggleNetworks = () => {
    showNetworks.value = !showNetworks.value;
};

const openPublicNetwork = () => {
    currentNetwork.value = null;
    currentNetworkId.value = 'public';
    viewMode.value = 'table';
};

const openNetworkView = (net) => {
    currentNetwork.value = net;
    currentNetworkId.value = net.id;
    viewMode.value = 'network_hub';
};

const applySkin = () => {
  document.documentElement.setAttribute('data-theme', currentSkin.value);
  localStorage.setItem('omega_skin', currentSkin.value);
};

const currentDate = new Date()
  .toLocaleDateString('es-ES', { year: 'numeric', month: '2-digit', day: '2-digit' })
  .replace(/\//g, '.');

const globalProcessedFiles = computed(() => {
  const visibleFiles = [];
  files.value.forEach((f) => {
    const isPrivate = f.network_id !== 'public';

    if (!isPrivate) {
      visibleFiles.push({
        ...f,
        isPrivate: false,
        tagsDecrypted: f.tags,
        ext: getFileExtension(f.filename),
      });
      return;
    }

    const net = privateNetworks.value.find((n) => n.id === f.network_id);
    if (!net) return; // No sintonizamos esta frecuencia: no podemos descifrarla, así que se omite.

    try {
      const decFilename = CryptoJS.AES.decrypt(f.filename, net.key).toString(CryptoJS.enc.Utf8);
      const decTags = CryptoJS.AES.decrypt(f.tags, net.key).toString(CryptoJS.enc.Utf8);

      if (!decFilename) throw new Error('Descifrado vacío');

      visibleFiles.push({
        ...f,
        isPrivate: true,
        filename: decFilename,
        tagsDecrypted: decTags,
        ext: getFileExtension(decFilename),
      });
    } catch (e) {
      // Bloque corrupto o llave incorrecta: se descarta silenciosamente.
    }
  });
  return visibleFiles;
});

// Filtro de búsqueda en cliente sobre la Bóveda pública/visible.
const filteredFiles = computed(() => {
  const q = searchQuery.value.trim().toLowerCase();
  if (!q) return globalProcessedFiles.value;
  return globalProcessedFiles.value.filter((f) =>
    f.filename.toLowerCase().includes(q) ||
    (f.tagsDecrypted || '').toLowerCase().includes(q) ||
    f.uploader.toLowerCase().includes(q)
  );
});

watch(privateNetworks, (nets) => {
  if (selectedNetwork.value !== 'public' && !nets.some((n) => n.id === selectedNetwork.value)) {
    selectedNetwork.value = 'public';
  }
});

const readFileAsDataUrl = (file) => new Promise((resolve, reject) => {
  const reader = new FileReader();
  reader.onload = (e) => resolve(e.target.result);
  reader.onerror = () => reject(new Error('No se pudo leer el archivo.'));
  reader.readAsDataURL(file);
});

const uploadFile = async () => {
  if (!selectedFile.value) return;

  const targetNetworkId = selectedNetwork.value;
  let net = null;
  if (targetNetworkId !== 'public') {
    net = privateNetworks.value.find((n) => n.id === targetNetworkId);
    if (!net) {
      uploadMsg.value = '[-] La frecuencia seleccionada ya no está sintonizada.';
      return;
    }
  }

  uploading.value = true;
  uploadMsg.value = '';

  try {
    let uploadFilename = selectedFile.value.name;
    let finalTags = (uploadTags.value || '').trim().toLowerCase();
    let fileBlob = selectedFile.value;

    if (net) {
      const fileDataUrl = await readFileAsDataUrl(selectedFile.value);
      uploadFilename = CryptoJS.AES.encrypt(uploadFilename, net.key).toString();
      finalTags = CryptoJS.AES.encrypt(finalTags, net.key).toString();
      const encryptedFileData = CryptoJS.AES.encrypt(fileDataUrl, net.key).toString();
      fileBlob = new Blob([encryptedFileData]);
    }

    const formData = new FormData();
    formData.append('file', fileBlob, uploadFilename);
    formData.append('tags', finalTags);
    formData.append('network_id', targetNetworkId);

    let digitalSignature;
    try {
      digitalSignature = signChallenge(`${uploadFilename}|${finalTags}`);
    } catch (e) {
      uploadMsg.value = '[-] Error OpSec: Llave privada no encontrada.';
      return;
    }
    formData.append('signature', digitalSignature);

    const res = await api.post('/network/upload', formData);
    uploadMsg.value = `[+] TX OK. CID: ${shortCid(res.data.cid)}`;
    selectedFile.value = null;
    uploadTags.value = '';
    fetchFiles();
  } catch (err) {
    uploadMsg.value = `[-] Rechazado: ${err.response?.data?.error || 'Nodo desconectado'}`;
  } finally {
    uploading.value = false;
  }
};

const downloadFile = async (file) => {
  try {
    if (!file.isPrivate) {
      // ARCHIVO PÚBLICO: Fue subido como binario puro.
      // Forzamos a Axios a descargarlo como Blob (archivo físico).
      const res = await api.get(`${IPFS_GATEWAY_URL}${file.cid}`, { responseType: 'blob' });
      const blobUrl = URL.createObjectURL(res.data);
      
      const a = document.createElement('a');
      a.href = blobUrl;
      a.download = file.filename;
      document.body.appendChild(a);
      a.click();
      
      document.body.removeChild(a);
      URL.revokeObjectURL(blobUrl);
      return;
    }

    // ARCHIVO PRIVADO: Fue subido como texto encriptado.
    const res = await api.get(`${IPFS_GATEWAY_URL}${file.cid}`, { responseType: 'text' });
    let encryptedData = res.data;

    const net = privateNetworks.value.find((n) => n.id === file.network_id);
    if (!net) {
      alert('[-] No se encontró la llave para esta frecuencia.');
      return;
    }

    // 1. Desencriptar el bloque
    const decryptedStr = CryptoJS.AES.decrypt(encryptedData, net.key).toString(CryptoJS.enc.Utf8);
    if (!decryptedStr) throw new Error('Descifrado vacío');

    // 2. Extraer la cadena Base64 pura (ignorando el "data:application/pdf;base64,")
    const parts = decryptedStr.split(',');
    const base64Content = parts.length > 1 ? parts[1] : parts[0]; 

    // 3. Traducir de Base64 a binario (Array de Bytes)
    const byteCharacters = atob(base64Content);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);

    // 4. Reconstruir y disparar la descarga
    const mimeType = parts.length > 1 ? parts[0].match(/:(.*?);/)[1] : "application/octet-stream";
    const blob = new Blob([byteArray], { type: mimeType });
    const blobUrl = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = blobUrl;
    a.download = file.filename;
    document.body.appendChild(a);
    a.click();
    
    document.body.removeChild(a);
    URL.revokeObjectURL(blobUrl);

  } catch (e) {
    console.error("Error en la extracción:", e);
    alert('Interferencia: El bloque está corrupto o la decodificación falló.');
  }
};

const fetchFiles = async () => {
  loadingFiles.value = true;
  try {
    const res = await api.get('/network/files');
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
  if (!newUserName.value.trim() || !newUserPubKey.value.trim()) {
    consensusMsg.value = '[-] Faltan datos.';
    return;
  }
  addingNode.value = true;
  consensusMsg.value = '';

  try {
    const payloadToSign = `SYSTEM_TRUST_ADD|${newUserName.value.trim()}|${newUserPubKey.value.trim()}`;
    const signature = signChallenge(payloadToSign);

    const res = await api.post('/auth/system/trust/add', {
      new_user: newUserName.value.trim(),
      new_pubkey: newUserPubKey.value.trim(),
      signature,
    });

    consensusMsg.value = `[+] ${res.data.message}`;
    newUserName.value = '';
    newUserPubKey.value = '';
  } catch (err) {
    consensusMsg.value = `[-] Rechazado: ${err.response?.data?.error || 'Error P2P'}`;
  } finally {
    addingNode.value = false;
  }
};

const logout = () => {
  // Limpieza completa: antes solo se borraba el JWT, dejando la llave
  // privada y el alias del usuario en localStorage tras cerrar sesión.
  localStorage.removeItem('omega_jwt');
  localStorage.removeItem('omega_priv_key');
  localStorage.removeItem('omega_user');
  emit('logout');
};

onMounted(() => {
  loadNetworksForUser(props.currentUser);
  fetchFiles();
  const savedSkin = localStorage.getItem('omega_skin');
  if (savedSkin) {
    currentSkin.value = savedSkin;
    applySkin();
  }
});

watch(() => props.currentUser, (newVal) => {
  loadNetworksForUser(newVal);
});
</script>

<style scoped>
/* Las variables se controlan ahora desde App.vue mediante data-theme */
.silo-dashboard {
  font-family: var(--font-display);
  background: var(--bg-main);
  color: var(--text-main);
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  font-size: var(--base-font-size, 14px);
  transition: background 0.3s, color 0.3s;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: var(--topbar-height, 36px);
  padding: 0 1rem;
  background: var(--topbar-bg, var(--border-color));
  color: var(--topbar-text, #fff);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: var(--topbar-shadow, none);
  border-bottom: var(--topbar-border, none);
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
  background: var(--version-bg, #fff);
  padding: 0 0.3rem;
  border-radius: var(--radius-sm, 0);
}

.topbar-session {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-family: var(--font-mono);
  font-size: 0.75rem;
}

.skin-selector {
  background: transparent;
  color: inherit;
  border: 1px dashed var(--hairline);
  font-family: inherit;
  font-size: 0.7rem;
  padding: 2px 4px;
  border-radius: var(--radius-sm, 0);
  outline: none;
}
.skin-selector option {
  color: #000;
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
  transition: color 0.2s;
}
.link-btn:hover { color: var(--highlight); }

/* LAYOUT EXPANDIDO */
.layout {
  flex-grow: 1;
  display: flex;
  padding: 1rem;
  gap: 1rem;
  width: 100%;
  box-sizing: border-box;
}

.sidebar {
  width: 220px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background: var(--bg-panel);
  border: var(--panel-border, 1px solid var(--border-color));
  box-shadow: var(--panel-shadow, 4px 4px 0 0 rgba(0, 0, 0, 0.15));
  border-radius: var(--radius-md, 0);
  height: fit-content;
  overflow: hidden;
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
  padding: 0.8rem 1rem;
  color: var(--accent-blue);
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}

.sidebar-nav button:hover { background: var(--hover-bg, var(--bg-main)); }
.sidebar-nav button.active {
  background: var(--active-bg, var(--border-color));
  color: var(--active-text, #fff);
}
.sidebar-nav button.nav-danger { color: var(--highlight); }
.sidebar-nav button.nav-danger.active { background: var(--highlight); color: #fff; }

.expandable-menu {
  display: flex;
  flex-direction: column;
  border-bottom: 1px solid var(--hairline);
}

.expand-btn {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: none !important;
}

.arrow {
  font-size: 0.6rem;
  transition: transform 0.2s;
  color: var(--text-muted);
}
.arrow-down { transform: rotate(90deg); }

.expanded-content {
  background: var(--expanded-bg, #fdfdfc);
  border-top: 1px dashed var(--hairline);
  display: flex;
  flex-direction: column;
}

.sub-nav-btn {
  padding-left: 1.5rem !important;
  font-size: 0.72rem !important;
  color: var(--text-muted) !important;
  border-bottom: none !important;
}
.sub-nav-btn:hover { color: var(--accent-blue) !important;}
.sub-nav-btn.active {
  background: var(--active-sub-bg, #eae9e4) !important;
  color: var(--text-main) !important;
  border-left: 3px solid var(--border-color) !important;
}
.sub-nav-btn.disabled-btn { cursor: default; opacity: 0.6; }
.public-btn {
  font-weight: bold !important;
}

.sidebar-status {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  padding: 0.8rem;
  border-top: 1px solid var(--border-color);
  background: var(--status-bg, var(--bg-main));
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

.main-viewport {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.view {
  background: var(--bg-panel);
  border: var(--panel-border, 1px solid var(--border-color));
  box-shadow: var(--panel-shadow, 4px 4px 0 0 rgba(0, 0, 0, 0.15));
  border-radius: var(--radius-lg, 0);
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  min-height: 500px;
  overflow: hidden;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--header-padding, 0.3rem 0.7rem);
  background: var(--header-bg, var(--border-color));
  color: var(--header-text, #fff);
  border-bottom: var(--header-border, none);
  flex-wrap: wrap;
  gap: 0.5rem;
}

.view-title {
  margin: 0;
  font-family: var(--font-display);
  font-size: 0.9rem;
  font-weight: bold;
  text-transform: uppercase;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.filter-input {
  background: rgba(255,255,255,0.15);
  border: 1px solid rgba(255,255,255,0.3);
  color: inherit;
  font-family: var(--font-mono);
  font-size: 0.72rem;
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-sm, 0);
  outline: none;
  width: 220px;
  max-width: 40vw;
}
.filter-input::placeholder { color: rgba(255,255,255,0.6); }
.filter-input:focus { border-color: rgba(255,255,255,0.7); }

.upload-bar {
  display: flex;
  border-bottom: 1px solid var(--border-color);
  background: var(--upload-bg, #f9f9f6);
  font-family: var(--font-mono);
  font-size: 0.78rem;
  flex-wrap: wrap;
}

.hidden-input { display: none; }

.upload-label {
  flex: 1;
  min-width: 150px;
  padding: 0.6rem 1rem;
  cursor: pointer;
  color: var(--accent-blue);
  border-right: 1px solid var(--border-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: flex;
  align-items: center;
  transition: background 0.2s;
}
.upload-label:hover { background: var(--hover-bg, #eeede7); }

.tag-input {
  flex: 2;
  min-width: 200px;
  border: none;
  border-right: 1px solid var(--border-color);
  padding: 0.6rem 1rem;
  font-family: inherit;
  font-size: inherit;
  outline: none;
  background: transparent;
  color: var(--text-main);
}
.tag-input:focus { background: var(--input-focus, #fff); }

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

.upload-btn {
  border: none;
  background: transparent;
  color: var(--highlight);
  font-weight: 700;
  padding: 0 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.upload-btn:hover:not(:disabled) {
  background: var(--btn-hover-bg, var(--highlight));
  color: var(--btn-hover-text, #fff);
}

.spinner {
  display: inline-block;
  width: 0.8em;
  height: 0.8em;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin-right: 0.4em;
  vertical-align: -0.1em;
}
@keyframes spin { to { transform: rotate(360deg); } }

.table-wrapper { flex-grow: 1; overflow-y: auto; padding: var(--table-padding, 0.5rem); }

.data-table { width: 100%; border-collapse: collapse; font-family: var(--font-mono); font-size: 0.8rem; }

.data-table th {
  text-align: left;
  padding: 0.5rem;
  border-bottom: 2px solid var(--border-color);
  font-weight: 700;
  text-transform: uppercase;
  font-size: 0.72rem;
  letter-spacing: 0.5px;
  background: var(--table-header-bg, var(--bg-main));
  color: var(--text-main);
}

.col-ext { width: 8%; }
.col-name { width: 32%; }
.col-tags { width: 18%; color: var(--text-muted); font-size: 0.72rem; }
.col-origin { width: 18%; font-style: italic; }
.col-hash { width: 24%; color: var(--text-muted); }

.data-row { border-bottom: 1px solid var(--hairline); transition: background 0.1s; }
.data-row:hover { background: var(--row-hover, #faf9f5); }
.data-row td { padding: 0.6rem 0.5rem; vertical-align: middle; }

.ext-tag {
  display: inline-block;
  border: 1px solid var(--text-muted);
  color: var(--text-muted);
  font-weight: 700;
  font-size: 0.68rem;
  padding: 0.05rem 0.3rem;
  border-radius: var(--radius-sm, 0);
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
  border-radius: var(--radius-sm, 0);
}

.filename-link { color: var(--accent-blue); text-decoration: var(--link-decor, underline); cursor: pointer; }
.filename-link:hover { color: var(--highlight); }

.empty-row { text-align: center; padding: 2rem; color: var(--text-muted); font-style: italic; }

.admin-panel { display: flex; padding: 1.5rem; gap: 1.5rem; background: var(--bg-main); flex-grow: 1; flex-wrap: wrap;}

.admin-card {
  flex: 1;
  min-width: 300px;
  background: var(--bg-panel);
  border: var(--panel-border, 1px solid var(--border-color));
  padding: 1.5rem;
  box-shadow: var(--card-shadow, 2px 2px 0 0 rgba(0, 0, 0, 0.15));
  border-radius: var(--radius-md, 0);
}

.admin-card h3 {
  margin-top: 0;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.5rem;
  font-size: 1rem;
  text-transform: uppercase;
}

.doc-text { color: var(--text-muted); font-size: 0.85rem; margin-bottom: 1.5rem; }

.input-group { margin-bottom: 1.2rem; font-family: var(--font-mono); }
.input-group label { display: block; font-weight: 700; margin-bottom: 0.4rem; font-size: 0.75rem; text-transform: uppercase; }
.input-group input {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid var(--border-color);
  background: var(--input-bg, #fff);
  color: var(--text-main);
  font-family: inherit;
  font-size: 0.85rem;
  box-sizing: border-box;
  outline: none;
  border-radius: var(--radius-sm, 0);
  transition: border-color 0.2s, box-shadow 0.2s;
}
.input-group input:focus { border-color: var(--accent-blue); box-shadow: var(--input-focus-shadow, none); }

.stats-list { list-style: none; padding: 0; margin: 0; font-family: var(--font-mono); font-size: 0.8rem; }
.stats-list li { display: flex; justify-content: space-between; padding: 0.7rem 0; border-bottom: 1px dotted var(--hairline); }
.stat-label { font-weight: 700; text-transform: uppercase; }
.stat-value.ok { color: var(--accent-green); font-weight: 700; }

.action-btn {
  background: var(--btn-bg, #e7e6e0);
  color: var(--text-main);
  border: var(--btn-border, 1px solid var(--border-color));
  border-right: var(--btn-border-right, 2px solid var(--border-color));
  border-bottom: var(--btn-border-bottom, 2px solid var(--border-color));
  padding: 0.6rem 1rem;
  font-family: var(--font-mono);
  font-weight: 700;
  font-size: 0.78rem;
  cursor: pointer;
  text-transform: uppercase;
  border-radius: var(--radius-sm, 0);
  transition: all 0.1s;
}
.action-btn:active {
  border: var(--btn-active-border, 1px solid var(--border-color));
  border-top: var(--btn-active-border-top, 2px solid var(--border-color));
  border-left: var(--btn-active-border-left, 2px solid var(--border-color));
  background: var(--btn-active-bg, #ccc);
  transform: var(--btn-active-transform, none);
}
.action-btn:hover:not(:disabled) { background: var(--btn-hover, #d7d6d0); box-shadow: var(--btn-hover-shadow, none);}
.action-btn:disabled { color: var(--text-muted); border-color: var(--hairline); background: var(--bg-main); cursor: not-allowed; }

.status-msg {
  margin: 1rem;
  padding: 0.6rem;
  font-family: var(--font-mono);
  font-size: 0.78rem;
  font-weight: 700;
  border: 1px solid var(--accent-green);
  color: var(--accent-green);
  background: var(--msg-bg, transparent);
  border-radius: var(--radius-sm, 0);
}
.error-msg { border-color: var(--highlight); color: var(--highlight); }
.loading-state { padding: 3rem; text-align: center; font-style: italic; color: var(--text-muted); }

.graph-wrapper { flex-grow: 1; position: relative; background: var(--graph-bg, #fff); padding: 2px; }

.slide-fade-enter-active { transition: all 0.15s ease-out; }
.slide-fade-leave-active { transition: all 0.15s ease-in; }
.slide-fade-enter-from, .slide-fade-leave-to { opacity: 0; transform: translateY(5px); }

@media (max-width: 800px) {
  .layout { flex-direction: column; padding: 0.5rem; }
  .sidebar { width: 100%; }
  .sidebar-nav { flex-direction: row; flex-wrap: wrap; }
  .sidebar-nav button { flex: 1; text-align: center; border-bottom: 1px solid var(--border-color); border-right: 1px solid var(--hairline); }
  .expandable-menu { width: 100%; }
  .upload-bar { flex-direction: column; }
  .upload-label, .tag-input, .network-selector, .upload-btn { border-right: none; border-bottom: 1px solid var(--border-color); width: 100%; box-sizing: border-box; }
  .view-header { flex-direction: column; align-items: stretch; }
  .filter-input { width: 100%; max-width: none; }
}
</style>