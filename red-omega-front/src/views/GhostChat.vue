<template>
  <div class="view-container">
    <div class="view-header">
      <h2 class="view-title glitch">CANAL FANTASMA // E2EE ACTIVO</h2>
      <div class="frequency-input">
        <label>FRECUENCIA AES:</label>
        <input v-model="secretKey" type="password" placeholder="Llave compartida..." />
      </div>
    </div>

    <div class="chat-layout">
      <!-- SIDEBAR: USUARIOS DETECTADOS -->
      <aside class="users-sidebar">
        <h3 class="sidebar-title">IDENTIDADES EN RED</h3>
        <ul class="users-list">
          <!-- El usuario actual -->
          <li class="my-user">
             <span class="status-dot"></span> @{{ currentUser }} (Tú)
          </li>
          <!-- Usuarios detectados -->
          <li 
            v-for="user in activeUsers" 
            :key="user"
            @click="targetUser = user"
            :class="{ selected: targetUser === user }"
          >
            <span class="status-dot"></span> @{{ user }}
          </li>
          <li v-if="activeUsers.length === 0" class="empty-users">Buscando señales...</li>
        </ul>
        <button v-if="targetUser" @click="targetUser = ''" class="action-btn clear-btn">GLOBAL (LIMPIAR TARGET)</button>
      </aside>

      <!-- ÁREA DE CHAT -->
      <div class="chat-area">
        <div class="terminal-body" ref="chatBox">
          <div v-if="!secretKey" class="static-noise">
            [!] INSERTE FRECUENCIA PARA DESCIFRAR EL TRÁFICO
          </div>

          <div v-else>
            <div v-for="msg in decryptedMessages" :key="msg.id" class="chat-line">
              <span class="timestamp">[{{ msg.time }}]</span>
              
              <!-- Mensaje de Pánico (Sobrescribe todo) -->
              <span v-if="msg.is_panic" class="panic-msg">
                *** {{ msg.plain_text }} ***
              </span>
              
              <span v-else-if="msg.error" class="noise-msg">*** INTERFERENCIA ***</span>
              
              <span v-else>
                <!-- Indicador de Target -->
                <span v-if="msg.target" class="target-indicator">
                  [A: @{{ msg.target }}]
                </span>
                
                <strong class="alias" :class="{ 'my-msg': msg.alias === currentUser }">
                  &lt;{{ msg.alias }}&gt;
                </strong> 
                
                <span v-if="!msg.isDrop" class="text" :class="{ 'direct-msg': msg.target }">
                  {{ msg.text }}
                </span>
                
                <span v-else class="dead-drop-ui">
                  [DEAD DROP DETECTADO] -> 
                  <button @click="downloadDrop(msg.cid, msg.filename)" class="action-btn drop-btn">
                    EXTRAER: {{ msg.filename }}
                  </button>
                </span>
              </span>
            </div>
          </div>
        </div>

        <div class="terminal-input">
          <div class="input-tools">
            <span v-if="targetUser" class="target-badge">DMs to: @{{ targetUser }}</span>
            <span v-else class="target-badge public-badge">GLOBAL MSG</span>
            
            <input type="file" @change="handleDropSelect" id="drop-upload" class="hidden-input" />
            <label for="drop-upload" class="drop-label action-btn" title="Adjuntar Dead Drop">
              [ 📎 DEAD DROP ]
            </label>
          </div>
          
          <input 
            v-model="newMessage" 
            @keyup.enter="sendMessage" 
            type="text" 
            :placeholder="dropFile ? `Drop cargado: ${dropFile.name} [Enter para enviar]` : 'Escriba aquí... [Enter para transmitir]'" 
            class="msg-input"
            :disabled="!secretKey || uploadingDrop"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import axios from 'axios';
import CryptoJS from 'crypto-js';

const props = defineProps(['currentUser']);

const API_URL_CHAT = 'http://127.0.0.1:5000/api/network/chat';
const API_URL_DROP = 'http://127.0.0.1:5000/api/network/ghost_drop';
const IPFS_GATEWAY = 'http://127.0.0.1:8080/ipfs/';

const secretKey = ref('');
const newMessage = ref('');
const rawMessages = ref([]);
const chatBox = ref(null);
let pollingInterval = null;

const targetUser = ref('');
const dropFile = ref(null);
const uploadingDrop = ref(false);

const getAuthHeaders = () => ({ Authorization: `Bearer ${localStorage.getItem('omega_jwt')}` });

const decryptedMessages = computed(() => {
  if (!secretKey.value) return [];
  
  const validMessages = [];

  rawMessages.value.forEach(msg => {
    if (msg.is_panic) {
       const date = new Date(parseFloat(msg.id) * 1000);
       validMessages.push({
           id: msg.id,
           time: date.toLocaleTimeString('es-ES', { hour12: false }),
           is_panic: true,
           plain_text: msg.plain_text
       });
       return;
    }

    try {
      const bytes = CryptoJS.AES.decrypt(msg.payload, secretKey.value);
      const decryptedString = bytes.toString(CryptoJS.enc.Utf8);
      if (!decryptedString) throw new Error("Bad key");
      
      const parsed = JSON.parse(decryptedString);
      
      // DARK ROUTING (DMs)
      if (parsed.target && parsed.target !== props.currentUser && parsed.alias !== props.currentUser) {
          return; 
      }

      const date = new Date(parseFloat(msg.id) * 1000);
      
      validMessages.push({
        id: msg.id,
        time: date.toLocaleTimeString('es-ES', { hour12: false }),
        alias: parsed.alias,
        text: parsed.text,
        target: parsed.target || null,
        isDrop: parsed.isDrop || false,
        cid: parsed.cid || null,
        filename: parsed.filename || null,
        error: false
      });
    } catch (e) {
      validMessages.push({ id: msg.id, time: "??:??:??", error: true });
    }
  });

  return validMessages;
});

const activeUsers = computed(() => {
    const users = new Set();
    decryptedMessages.value.forEach(msg => {
        if(msg.alias && msg.alias !== props.currentUser && !msg.error) {
            users.add(msg.alias);
        }
    });
    return Array.from(users);
});

const fetchMessages = async () => {
  try {
    const res = await axios.get(API_URL_CHAT, { headers: getAuthHeaders() });
    const isNew = rawMessages.value.length !== res.data.length;
    rawMessages.value = res.data;
    
    if(isNew) {
        setTimeout(() => { if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight; }, 100);
    }
  } catch (err) {}
};

const handleDropSelect = (event) => {
  const file = event.target.files[0];
  if (!file) return;
  if (file.size > 10 * 1024 * 1024) {
      alert("Para Dead Drops, el límite es 10MB por RAM del navegador.");
      return;
  }
  dropFile.value = file;
};

const sendMessage = async () => {
  if (!secretKey.value) return;
  if (!newMessage.value.trim() && !dropFile.value) return;

  uploadingDrop.value = true;
  let finalPayload = {};

  if (dropFile.value) {
    const reader = new FileReader();
    reader.readAsDataURL(dropFile.value);
    
    reader.onload = async () => {
      const base64Data = reader.result;
      const encryptedFileData = CryptoJS.AES.encrypt(base64Data, secretKey.value).toString();
      
      const blob = new Blob([encryptedFileData], { type: 'text/plain' });
      const formData = new FormData();
      formData.append('file', blob, 'ghost_drop.bin');

      try {
        const resDrop = await axios.post(API_URL_DROP, formData, { headers: getAuthHeaders() });
        const cid = resDrop.data.cid;

        finalPayload = {
          alias: props.currentUser, 
          target: targetUser.value || null, 
          text: newMessage.value.trim() || "Dead Drop Depositado.",
          isDrop: true,
          cid: cid,
          filename: dropFile.value.name
        };

        transmitToNetwork(finalPayload);
      } catch (err) {
        console.error("Fallo al inyectar el Drop en IPFS");
        uploadingDrop.value = false;
      }
    };
  } else {
    finalPayload = { 
        alias: props.currentUser, 
        target: targetUser.value || null,
        text: newMessage.value.trim() 
    };
    transmitToNetwork(finalPayload);
  }
};

const transmitToNetwork = async (plainObject) => {
  const encryptedPayload = CryptoJS.AES.encrypt(JSON.stringify(plainObject), secretKey.value).toString();
  try {
    await axios.post(API_URL_CHAT, { payload: encryptedPayload }, { headers: getAuthHeaders() });
    newMessage.value = '';
    dropFile.value = null; 
    fetchMessages();
  } catch (err) {
    console.error("Fallo al transmitir");
  } finally {
    uploadingDrop.value = false;
  }
};

const downloadDrop = async (cid, originalName) => {
  try {
    const response = await axios.get(`${IPFS_GATEWAY}${cid}`, { responseType: 'text' });
    const encryptedData = response.data;

    const bytes = CryptoJS.AES.decrypt(encryptedData, secretKey.value);
    const decryptedBase64 = bytes.toString(CryptoJS.enc.Utf8);

    if (!decryptedBase64) throw new Error("Fallo de integridad");

    const a = document.createElement("a");
    a.href = decryptedBase64;
    a.download = originalName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

  } catch (e) {
    alert("Interferencia: Imposible extraer el Dead Drop. Archivo corrupto o llave incorrecta.");
  }
};

onMounted(() => {
  fetchMessages();
  pollingInterval = setInterval(fetchMessages, 2000);
});

onUnmounted(() => { clearInterval(pollingInterval); });
</script>

<style scoped>
/* HEREDAR VARIABLES DEL DASHBOARD */
.view-container {
  display: flex;
  flex-direction: column;
  background: var(--bg-panel);
  border: 1px solid var(--border-color);
  box-shadow: 4px 4px 0 0 rgba(0, 0, 0, 0.15);
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


.frequency-input { display: flex; align-items: center; gap: 0.5rem; font-family: var(--font-mono); }
.frequency-input label { font-size: 0.75rem; font-weight: bold;}
.frequency-input input { 
    background: var(--bg-main); border: 1px solid var(--border-color); 
    color: var(--text-main); padding: 0.2rem 0.5rem; outline: none; font-family: inherit;
}

.chat-layout { display: flex; flex-grow: 1; min-height: 500px; }

/* SIDEBAR USUARIOS */
.users-sidebar { 
    width: 220px; background: var(--bg-main); border-right: 1px solid var(--border-color); padding: 1rem;
    display: flex; flex-direction: column;
}
.sidebar-title { margin: 0 0 1rem 0; font-size: 0.85rem; color: var(--text-main); border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; font-family: var(--font-display); font-weight: bold;}
.users-list { list-style: none; padding: 0; margin: 0; flex-grow: 1; overflow-y: auto; font-family: var(--font-mono);}
.users-list li { 
    padding: 0.5rem; cursor: pointer; font-size: 0.8rem; display: flex; align-items: center; gap: 0.5rem;
    color: var(--text-muted); border-bottom: 1px dotted var(--hairline);
}
.users-list li.my-user { color: var(--text-main); font-weight: bold; cursor: default; border-bottom: 1px solid var(--border-color);}

.users-list li:hover:not(.my-user) { background: #eaeaea; color: var(--text-main);}
.users-list li.selected { background: var(--border-color); color: #fff; font-weight: bold;}

.status-dot { width: 8px; height: 8px; background: var(--accent-green); border-radius: 50%; border: 1px solid #000;}
.users-list li.selected .status-dot { background: #fff;}

.empty-users { color: var(--text-muted); font-style: italic; font-size: 0.75rem; border: none !important;}

.clear-btn { margin-top: 1rem; font-size: 0.7rem; text-align: center; width: 100%;}

/* ÁREA DE CHAT */
.chat-area { flex-grow: 1; display: flex; flex-direction: column; position: relative; background: #000; color: #00ff00;}

.terminal-body {
  flex-grow: 1;
  padding: 1rem;
  overflow-y: auto;
  font-family: var(--font-mono);
  font-size: 0.85rem;
}

.static-noise { color: #555; font-style: italic; text-align: center; margin-top: 4rem; }
.chat-line { margin-bottom: 0.4rem; line-height: 1.4; word-break: break-word;}
.timestamp { color: #555; margin-right: 0.5rem; }

.alias { color: #aaa; margin-right: 0.5rem; }
.alias.my-msg { color: #00ff00; }

.text { color: #ddd; }
.text.direct-msg { color: #00ffff; font-weight: bold;} /* DMs resaltan en cyan */

.target-indicator { color: #ff00ff; margin-right: 0.5rem; font-weight: bold;}

.noise-msg { color: var(--highlight); background: #330000; padding: 0 0.2rem; }
.panic-msg { color: #fff; background: var(--highlight); font-weight: bold; padding: 0.2rem 0.5rem; animation: blinker 1s linear infinite;}

/* INPUT */
.terminal-input {
  display: flex;
  flex-direction: column;
  border-top: 2px solid var(--border-color);
  background: var(--bg-main);
  padding: 0.5rem;
  font-family: var(--font-mono);
}

.input-tools { display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;}
.target-badge { background: #00ffff; color: #000; font-weight: bold; padding: 0.1rem 0.5rem; font-size: 0.75rem; border: 1px solid #000;}
.public-badge { background: var(--text-main); color: #fff;}

.hidden-input { display: none; }
.drop-label { margin: 0; padding: 0.2rem 0.5rem; font-size: 0.75rem;}

.msg-input {
  width: 100%;
  background: #fff;
  color: var(--text-main);
  border: 1px solid var(--border-color);
  padding: 0.6rem;
  font-family: inherit;
  font-size: 0.85rem;
  outline: none;
}
.msg-input:focus { border-color: var(--accent-blue); box-shadow: 2px 2px 0 var(--accent-blue);}
.msg-input:disabled { background: #eee; cursor: not-allowed; opacity: 0.7;}

.dead-drop-ui { color: #ffaa00; font-weight: bold; }
.drop-btn { color: #ffaa00; border-color: #ffaa00; margin-left: 0.5rem; background: #222;}
.drop-btn:hover { background: #ffaa00; color: #000;}

/* Botón base heredado de layout general */
.action-btn {
  background: #e7e6e0; color: var(--text-main); border: 1px solid var(--border-color); border-right: 2px solid var(--border-color); border-bottom: 2px solid var(--border-color);
  font-family: var(--font-mono); font-weight: 700; font-size: 0.78rem; cursor: pointer; text-transform: uppercase;
}
.action-btn:active { border-top: 2px solid var(--border-color); border-left: 2px solid var(--border-color); background: #ccc;}
.action-btn:hover { background: #d7d6d0;}

@keyframes blinker { 50% { opacity: 0.5; } }
</style>