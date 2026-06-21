<template>
  <div class="editor-container view-container">
    <div class="toolbar">
      <h2 class="view-title">TERMINAL DE REDACCIÓN</h2>
      <div class="actions">
        <input v-model="articleTitle" type="text" placeholder="TITULO_DEL_DOCUMENTO" class="title-input" />
        <input v-model="articleTags" type="text" placeholder="TAGS (ej: teoria, praxis)" class="tag-input" />
        <button class="action-btn" @click="publishArticle" :disabled="isPublishing || !articleTitle || !rawMarkdown">
          {{ isPublishing ? 'ENCRIPTANDO...' : 'INYECTAR EN BÓVEDA' }}
        </button>
      </div>
    </div>
    
    <div class="split-pane">
      <div class="pane editor-pane">
        <textarea 
          v-model="rawMarkdown" 
          placeholder="Escriba aquí la teoría o análisis táctico en formato Markdown..."
          class="md-input"
        ></textarea>
      </div>
      <div class="pane preview-pane">
        <div class="markdown-body" v-html="compiledMarkdown"></div>
      </div>
    </div>
    <div v-if="sysMsg" :class="['sys-msg', { 'error-msg': sysMsg.includes('[-]') }]">{{ sysMsg }}</div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { marked } from 'marked';
import axios from 'axios';
import { signChallenge } from '../utils/crypto';

const API_URL = 'http://127.0.0.1:5000/api/network/upload';
const getAuthHeaders = () => ({ Authorization: `Bearer ${localStorage.getItem('omega_jwt')}` });

const rawMarkdown = ref('');
const articleTitle = ref('');
const articleTags = ref('');
const isPublishing = ref(false);
const sysMsg = ref('');

const compiledMarkdown = computed(() => {
  return marked(rawMarkdown.value);
});

const publishArticle = async () => {
  isPublishing.value = true;
  sysMsg.value = '';

  const fileName = `${articleTitle.value.replace(/\s+/g, '_').toLowerCase()}.md`;
  const tagsRaw = articleTags.value.trim().toLowerCase() || 'documento';
  
  const blob = new Blob([rawMarkdown.value], { type: 'text/markdown' });

  let digitalSignature = '';
  try {
    digitalSignature = signChallenge(`${fileName}|${tagsRaw}`);
  } catch (e) {
    sysMsg.value = "[-] Error OpSec: Llave privada no encontrada.";
    isPublishing.value = false;
    return;
  }

  const formData = new FormData();
  formData.append('file', blob, fileName);
  formData.append('tags', tagsRaw);
  formData.append('signature', digitalSignature);

  try {
    const res = await axios.post(API_URL, formData, {
      headers: { ...getAuthHeaders(), 'Content-Type': 'multipart/form-data' }
    });
    sysMsg.value = `[+] Documento forjado y transmitido. CID: ${res.data.cid}`;
    rawMarkdown.value = '';
    articleTitle.value = '';
    articleTags.value = '';
  } catch (err) {
    sysMsg.value = `[-] Error de transmisión: ${err.response?.data?.error || 'Nodo desconectado'}`;
  } finally {
    isPublishing.value = false;
  }
};
</script>

<style scoped>
.editor-container { 
  display: flex; flex-direction: column; height: 100%; 
  font-family: 'Times New Roman', Times, serif; font-size: 14px;
}
.toolbar { 
  display: flex; justify-content: space-between; align-items: center; 
  padding: 0.2rem 0.5rem; border-bottom: 1px solid #000; background: #000; color: #fff;
}
.view-title { margin: 0; font-size: 0.9rem; font-weight: bold; text-transform: uppercase;}
.actions { display: flex; gap: 0.5rem;}
.title-input, .tag-input { 
  border: 1px solid #000; padding: 0.2rem 0.5rem; font-family: inherit; font-size: 0.85rem; outline: none;
}
.title-input:focus, .tag-input:focus { border-color: #cc0000;}

/* Boton Retro */
.action-btn {
  background: #e0e0e0; color: #000; border: 1px solid #000; border-right: 2px solid #000; border-bottom: 2px solid #000;
  padding: 0.2rem 0.8rem; font-family: inherit; font-weight: bold; font-size: 0.8rem; cursor: pointer; text-transform: uppercase;
}
.action-btn:active { border: 1px solid #000; border-top: 2px solid #000; border-left: 2px solid #000; background: #ccc;}
.action-btn:disabled { color: #888; border-color: #aaa; background: #eee; cursor: not-allowed; }

.split-pane { display: flex; flex-grow: 1; min-height: 500px; background: #f0f0f0; padding: 0.5rem; gap: 0.5rem;}
.pane { flex: 1; padding: 1rem; overflow-y: auto; background: #fff; border: 1px solid #000;}
.editor-pane { }
.md-input { width: 100%; height: 100%; background: transparent; border: none; color: #000; font-family: monospace; font-size: 0.9rem; resize: none; outline: none;}
.preview-pane { }

/* Estilos de Markdown inyectado */
:deep(.markdown-body) { font-family: 'Times New Roman', Times, serif; line-height: 1.4; font-size: 0.95rem;}
:deep(.markdown-body h1), :deep(.markdown-body h2) { border-bottom: 1px solid #000; padding-bottom: 0.2rem; margin-top: 0.5rem;}
:deep(.markdown-body blockquote) { border-left: 3px solid #cc0000; margin: 0.5rem 0; padding-left: 0.5rem; color: #444; font-style: italic;}
:deep(.markdown-body code) { background: #eaeaea; padding: 0.1rem 0.3rem; font-family: monospace;}

.sys-msg { padding: 0.5rem; font-weight: bold; border-top: 1px solid #000; font-size: 0.85rem; background: #fff;}
.error-msg { color: #cc0000; }
</style>
