<template>
  <div class="view-container">
    <div class="view-header network-header">
      <h2 class="view-title glitch-text">{{ currentNetwork.name.toUpperCase() }}</h2>
      <div class="hub-stats">
        <button @click="toggleNewPost" class="action-btn small-btn mr-1">
          {{ isComposing ? 'CANCELAR TRANSMISIÓN' : 'NUEVO HILO' }}
        </button>
        <button @click="fetchFeed" class="link-btn">[ REFRESH ]</button>
      </div>
    </div>

    <div class="hub-layout">
      <div v-if="isComposing" class="global-composer-box">
        <h3 class="box-title">NUEVA TRANSMISIÓN AL ENJAMBRE</h3>
        <input v-model="newThreadTitle" type="text" placeholder="Asunto / Título del Manifiesto..." class="composer-input" />
        <textarea v-model="newThreadContent" placeholder="Redactar inteligencia (Soporta sintaxis Markdown)..." class="composer-textarea main-composer"></textarea>
        <div class="composer-actions">
          <button @click="publishPost(null)" class="action-btn" :disabled="isPublishing || !newThreadContent">
            {{ isPublishing ? 'ENCRIPTANDO BLOQUE...' : 'DIFUNDIR' }}
          </button>
        </div>
        <div v-if="sysMsg && !replyingTo" class="status-msg">{{ sysMsg }}</div>
      </div>

      <div class="feed-col">
        <div v-if="isLoadingFeed" class="loading-state">
          <span class="pulse">SINCRONIZANDO Y DESCIFRANDO BLOQUES...</span>
        </div>
        
        <div v-else-if="feedTree.length === 0" class="empty-state">
          NO HAY INTELIGENCIA COMPARTIDA EN ESTA FRECUENCIA.
        </div>

        <div v-else class="timeline">
          <div v-for="thread in feedTree" :key="thread.cid" class="thread-card">
            
            <div class="post-header">
              <span class="post-author">@{{ thread.uploader }}</span>
              <span class="post-date">{{ formatDate(thread.date) }}</span>
              <span class="post-cid" :title="thread.cid">CID: {{ shortCid(thread.cid) }}</span>
            </div>
            
            <h4 class="post-title" v-if="thread.title">{{ thread.title }}</h4>
            <div class="post-content markdown-body" v-html="thread.htmlContent"></div>
            
            <div class="post-footer">
              <button @click="toggleReply(thread.cid)" class="link-btn">
                [ {{ replyingTo === thread.cid ? 'CANCELAR RESPUESTA' : 'AÑADIR A ESTE HILO' }} ]
              </button>
            </div>

            <div v-if="replyingTo === thread.cid" class="inline-reply-box">
              <textarea v-model="replyContent" placeholder="Escriba su respuesta (Markdown)..." class="composer-textarea mini"></textarea>
              <div class="composer-actions right">
                <button @click="publishPost(thread.cid)" class="action-btn small-btn" :disabled="isPublishing || !replyContent">
                  {{ isPublishing ? 'TX...' : 'ENVIAR RESPUESTA' }}
                </button>
              </div>
              <div v-if="sysMsg && replyingTo === thread.cid" class="status-msg">{{ sysMsg }}</div>
            </div>

            <div v-if="thread.replies && thread.replies.length > 0" class="replies-container">
              <div v-for="reply in thread.replies" :key="reply.cid" class="reply-card">
                <div class="post-header">
                  <span class="post-author">@{{ reply.uploader }}</span>
                  <span class="post-date">{{ formatDate(reply.date) }}</span>
                </div>
                <div class="post-content markdown-body" v-html="reply.htmlContent"></div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import axios from 'axios';
import CryptoJS from 'crypto-js';
import { marked } from 'marked';
import { signChallenge } from '../utils/crypto';

const props = defineProps({
  currentNetwork: Object,
  currentUser: String,
  files: Array
});

const emit = defineEmits(['refresh-requested']);

const API_URL = 'http://127.0.0.1:5000/api/network/upload';
const IPFS_GATEWAY = 'http://127.0.0.1:8080/ipfs/';
const getAuthHeaders = () => ({ Authorization: `Bearer ${localStorage.getItem('omega_jwt')}` });

const isLoadingFeed = ref(false);
const postsData = ref({}); 

const isComposing = ref(false); // Controla la visibilidad del composer principal
const newThreadTitle = ref('');
const newThreadContent = ref('');

const replyingTo = ref(null);
const replyContent = ref('');

const isPublishing = ref(false);
const sysMsg = ref('');

const fetchFeed = () => {
    emit('refresh-requested');
};

const toggleNewPost = () => {
    isComposing.value = !isComposing.value;
    if(!isComposing.value) {
        newThreadTitle.value = '';
        newThreadContent.value = '';
    }
};

const syncFeedContents = async () => {
  if (!props.currentNetwork || !props.files) return;
  isLoadingFeed.value = true;
  
  const networkPosts = props.files.filter(f => 
      f.network_id === props.currentNetwork.id && 
      f.ext === 'MD'
  );

  for (let post of networkPosts) {
      if (!postsData.value[post.cid]) {
          try {
              const res = await axios.get(`${IPFS_GATEWAY}${post.cid}`, { responseType: 'text' });
              const encryptedData = res.data;
              
              // 1. Descifrar con CryptoJS
              const bytes = CryptoJS.AES.decrypt(encryptedData, props.currentNetwork.key);
              const decryptedBase64 = bytes.toString(CryptoJS.enc.Utf8);
              
              // 2. Decodificar el Base64 a texto plano real
              // (Usamos atob combinado con decodeURIComponent para caracteres especiales)
              let plainMarkdown = '';
              try {
                  plainMarkdown = decodeURIComponent(escape(window.atob(decryptedBase64)));
              } catch (decodeErr) {
                 // Si falla el atob, es posible que el texto no se haya empaquetado en base64 (post viejo). 
                 // Intentamos usar el string directo.
                 plainMarkdown = decryptedBase64;
              }

              // Validamos que realmente hayamos obtenido texto legible
              if (plainMarkdown && !plainMarkdown.startsWith("U2FsdGVkX1")) {
                  postsData.value[post.cid] = plainMarkdown;
              } else {
                  throw new Error("Texto aún cifrado");
              }
              
          } catch (e) {
              console.warn(`Descarte táctico: El bloque ${post.cid} no pudo ser descifrado correctamente.`);
              postsData.value[post.cid] = null; // Lo marcamos como nulo para que el computed lo ignore
          }
      }
  }
  isLoadingFeed.value = false;
};

// Se ejecuta cada vez que cambian los archivos (ej. al refrescar)
watch(() => props.files, () => { syncFeedContents(); }, { deep: true });
onMounted(() => { syncFeedContents(); });

const feedTree = computed(() => {
  const allPosts = [];
  
  props.files.forEach(f => {
      // Filtrar solo MDs de esta red
      if (f.network_id !== props.currentNetwork.id || f.ext !== 'MD') return;
      
      let isReply = false;
      let parentCid = null;
      let isPost = false;
      
      const tagsArray = f.tagsDecrypted ? f.tagsDecrypted.split(',') : [];
      tagsArray.forEach(tag => {
          if (tag === 'post') isPost = true;
          if (tag.startsWith('reply_to:')) {
              isReply = true;
              parentCid = tag.split(':')[1];
          }
      });
      
      // Si no tiene la etiqueta 'post', no se dibuja en el Hub
      if(!isPost) return;

      // Si la función de sincronización lo marcó como nulo (falla de descifrado), lo ignoramos totalmente
      const markdownText = postsData.value[f.cid];
      if (!markdownText) return; 

      let displayTitle = f.filename.replace('.md', '').replace(/_/g, ' ').toUpperCase();
      if (displayTitle.startsWith('REPLY')) displayTitle = ''; 

      allPosts.push({
          ...f,
          title: displayTitle,
          isReply,
          parentCid,
          htmlContent: marked(markdownText),
          replies: [] 
      });
  });

  const threads = allPosts.filter(p => !p.isReply);
  const replies = allPosts.filter(p => p.isReply);

  replies.forEach(reply => {
      const parent = threads.find(t => t.cid === reply.parentCid);
      if (parent) {
          parent.replies.push(reply);
      } else {
          threads.push(reply);
      }
  });

  // Ordenar de más reciente a más antiguo
  return threads.sort((a, b) => new Date(b.date) - new Date(a.date));
});

const toggleReply = (cid) => {
    if (replyingTo.value === cid) {
        replyingTo.value = null; 
        replyContent.value = '';
    } else {
        replyingTo.value = cid;  
        replyContent.value = '';
        sysMsg.value = '';
    }
};

const publishPost = async (parentCid = null) => {
  isPublishing.value = true;
  sysMsg.value = '';

  const isReply = parentCid !== null;
  const contentToPublish = isReply ? replyContent.value : newThreadContent.value;
  
  let baseFilename = isReply 
      ? `reply_${Math.floor(Math.random()*10000)}` 
      : newThreadTitle.value || `informe_${Math.floor(Math.random()*10000)}`;
      
  let uploadFilename = `${baseFilename.replace(/\s+/g, '_').toLowerCase()}.md`;
  let uploadTagsString = isReply ? `post,reply_to:${parentCid}` : `post,thread`;

  const netKey = props.currentNetwork.key;
  
  // CIFRADO DE CONTENIDO (Mismo método que Editor.vue para compatibilidad)
  const base64Data = window.btoa(unescape(encodeURIComponent(contentToPublish)));
  const encryptedFileData = CryptoJS.AES.encrypt(base64Data, netKey).toString();
  
  const encryptedFilename = CryptoJS.AES.encrypt(uploadFilename, netKey).toString();
  const encryptedTags = CryptoJS.AES.encrypt(uploadTagsString, netKey).toString();

  const formData = new FormData();
  formData.append('file', new Blob([encryptedFileData], { type: 'text/markdown' }), encryptedFilename);
  formData.append('tags', encryptedTags);
  formData.append('network_id', props.currentNetwork.id);
  
  try {
      const digitalSignature = signChallenge(`${encryptedFilename}|${encryptedTags}`);
      formData.append('signature', digitalSignature);
  } catch (e) {
      sysMsg.value = "[-] Error OpSec: Llave privada no encontrada.";
      isPublishing.value = false;
      return;
  }

  try {
    await axios.post(API_URL, formData, { headers: getAuthHeaders() });
    
    if (isReply) {
        replyingTo.value = null;
        replyContent.value = '';
    } else {
        isComposing.value = false;
        newThreadTitle.value = '';
        newThreadContent.value = '';
    }
    sysMsg.value = '[+] Transmisión exitosa.';
    
    // Disparar refresco automático
    fetchFeed();
  } catch (err) {
    sysMsg.value = '[-] Interferencia. No se pudo transmitir.';
  } finally {
    isPublishing.value = false;
  }
};

const shortCid = (cid) => cid ? `${cid.substring(0, 6)}...${cid.substring(cid.length - 4)}` : '';
const formatDate = (dateString) => {
    if(!dateString) return '';
    const d = new Date(dateString);
    return `${d.toLocaleDateString()} ${d.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`;
};
</script>

<style scoped>
.view-container {
  display: flex;
  flex-direction: column;
  background: var(--bg-main);
  border: 1px solid var(--border-color);
  box-shadow: 4px 4px 0 0 rgba(0, 0, 0, 0.15);
  min-height: 500px;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.3rem 0.7rem;
  color: #fff;
}

.view-title {
  margin: 0;
  font-family: var(--font-display);
  font-size: 0.9rem;
  font-weight: bold;
  text-transform: uppercase;
}

.network-header { background: var(--border-color); color: #fff; border-bottom: 2px solid var(--highlight);}
.glitch-text { font-family: var(--font-display); letter-spacing: 1px; }

.hub-stats { display: flex; align-items: center; gap: 1rem;}
.mr-1 { margin-right: 1rem;}

.hub-layout {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    overflow: hidden;
}

/* MODULO DE REDACCION GLOBAL */
.global-composer-box {
    background: #eae9e4;
    border-bottom: 2px solid var(--border-color);
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
}

.global-composer-box h3.box-title { 
    margin-top: 0; 
    border-bottom: 1px dotted var(--border-color); 
    padding-bottom: 0.3rem; 
    font-size: 0.9rem;
    font-family: var(--font-display);
}

.composer-input, .composer-textarea {
    width: 100%;
    background: #fff;
    border: 1px solid var(--border-color);
    padding: 0.6rem;
    font-family: inherit;
    font-size: 0.9rem;
    box-sizing: border-box;
    outline: none;
    margin-bottom: 0.5rem;
}
.composer-textarea.main-composer { height: 250px; resize: vertical; font-family: var(--font-mono); font-size: 0.85rem;}
.composer-textarea:focus, .composer-input:focus { border-color: var(--accent-blue); box-shadow: 2px 2px 0 var(--accent-blue);}

.composer-actions { display: flex; justify-content: flex-end; }
.composer-actions.right { margin-top: 0.5rem; }

/* FEED (TIMELINE EXPANDIDO) */
.feed-col {
    flex-grow: 1;
    background: var(--bg-main);
    padding: 1.5rem;
    overflow-y: auto;
}

.loading-state, .empty-state {
    text-align: center;
    padding: 3rem;
    font-family: var(--font-mono);
    color: var(--text-muted);
    font-size: 0.85rem;
}
.pulse { animation: pulse 1.5s infinite; }
@keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }


.timeline {
    display: flex;
    flex-direction: column;
    gap: 2rem;
    max-width: 900px;
    margin: 0 auto;
}

/* TARJETAS DE POSTS (TIPO BLOG ACADÉMICO) */
.thread-card {
    background: var(--bg-panel);
    border: 1px solid var(--border-color);
    box-shadow: 3px 3px 0 0 rgba(0,0,0,0.1);
    padding: 2rem;
    display: flex;
    flex-direction: column;
}

.post-header {
    display: flex;
    align-items: baseline;
    gap: 1rem;
    margin-bottom: 1rem;
    border-bottom: 1px solid var(--hairline);
    padding-bottom: 0.5rem;
    font-family: var(--font-mono);
    font-size: 0.8rem;
}
.post-author { font-weight: bold; color: var(--accent-blue); }
.post-date { color: var(--text-muted); }
.post-cid { margin-left: auto; color: #ccc; font-size: 0.65rem; cursor: help;}

.post-title { margin: 0 0 1rem 0; font-size: 1.3rem; text-transform: uppercase; font-family: var(--font-display); font-weight: bold;}

/* Markdown Styles (Legibilidad) */
.post-content { font-size: 1rem; line-height: 1.6; color: var(--text-main); font-family: var(--font-display);}
:deep(.post-content p) { margin-top: 0; margin-bottom: 1rem;}
:deep(.post-content h1), :deep(.post-content h2), :deep(.post-content h3) { margin-top: 1.5rem; margin-bottom: 0.5rem; font-weight: bold;}
:deep(.post-content blockquote) { border-left: 3px solid var(--highlight); margin: 1rem 0; padding-left: 1rem; color: var(--text-muted); font-style: italic; background: #faf9f5; padding: 0.8rem;}
:deep(.post-content code) { font-family: var(--font-mono); background: #eee; padding: 0.1rem 0.3rem;}
:deep(.post-content pre) { background: #111; color: #00ff00; padding: 1rem; font-family: var(--font-mono); font-size: 0.85rem; overflow-x: auto; margin-bottom: 1rem;}
:deep(.post-content img) { max-width: 100%; border: 1px solid var(--border-color); margin: 1rem 0;}

.post-footer { margin-top: 1rem; padding-top: 0.5rem; text-align: right;}

.link-btn {
  background: none; border: none; font-family: var(--font-mono); font-weight: 700; font-size: 0.75rem; color: var(--text-muted); cursor: pointer; padding: 0; text-transform: uppercase;
}
.link-btn:hover { color: var(--highlight); }

/* RESPUESTAS ANIDADAS */
.replies-container {
    margin-top: 1.5rem;
    margin-left: 2rem; 
    border-left: 2px solid var(--border-color);
    padding-left: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.reply-card {
    background: #fdfdfc;
    border: 1px dotted var(--hairline);
    padding: 1.2rem;
}
.reply-card .post-title { font-size: 1.1rem; }

.inline-reply-box {
    margin-top: 1rem;
    background: #f4f4f4;
    padding: 1rem;
    border: 1px dashed var(--border-color);
}
.composer-textarea.mini { height: 100px; }

/* Botón base */
.action-btn {
  background: #e7e6e0; color: var(--text-main); border: 1px solid var(--border-color); border-right: 2px solid var(--border-color); border-bottom: 2px solid var(--border-color);
  padding: 0.4rem 0.8rem; font-family: var(--font-mono); font-weight: 700; font-size: 0.75rem; cursor: pointer; text-transform: uppercase;
}
.action-btn:active { border: 1px solid var(--border-color); border-top: 2px solid var(--border-color); border-left: 2px solid var(--border-color); background: #ccc;}
.action-btn:hover:not(:disabled) { background: #d7d6d0; }
.action-btn:disabled { color: #999; border-color: #ccc; cursor: not-allowed;}
.small-btn { padding: 0.2rem 0.5rem; font-size: 0.7rem;}
.status-msg { margin-top: 0.5rem; font-family: var(--font-mono); font-size: 0.75rem; color: var(--accent-green); font-weight: bold;}
</style>