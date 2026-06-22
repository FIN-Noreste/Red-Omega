<template>
  <div class="app-root">
    <transition name="auth-fade" mode="out-in">
      <AuthGate v-if="!isAuthenticated" key="auth" @authenticated="onLogin" />
      <Dashboard v-else key="dashboard" :current-user="currentUser" @logout="onLogout" />
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import AuthGate from './views/AuthGate.vue';
import Dashboard from './views/Dashboard.vue';

const isAuthenticated = ref(false);
const currentUser = ref('');

const onLogin = (username) => {
  currentUser.value = username;
  // BUG FIX: antes solo se guardaba el JWT, nunca el alias. Al recargar
  // la página, onMounted() de abajo no tenía forma de saber quién era el
  // usuario real y mostraba "Investigador" para todo el mundo (y eso a su
  // vez rompía la carga de redes privadas, que está indexada por usuario).
  localStorage.setItem('omega_user', username);
  isAuthenticated.value = true;
};

const onLogout = () => {
  isAuthenticated.value = false;
  currentUser.value = '';
};

onMounted(() => {
  const token = localStorage.getItem('omega_jwt');
  const savedUser = localStorage.getItem('omega_user');
  const savedSkin = localStorage.getItem('omega_skin') || 'brutalist';

  document.documentElement.setAttribute('data-theme', savedSkin);

  if (token && savedUser) {
    isAuthenticated.value = true;
    currentUser.value = savedUser;
  }
});
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600;700&family=Roboto:wght@400;500;700&display=swap');

/* ============================================================
   SISTEMA DE SKINS (CSS Variables)
   Todas las vistas (incluyendo AuthGate, Editor y NetworkMap, que antes
   ignoraban este sistema y quedaban "atascadas" en un look retro fijo)
   ahora leen exclusivamente estas variables, así que cambiar de skin
   re-pinta la app entera de forma consistente.
   ============================================================ */

/* 1. BRUTALIST (Default original) */
:root[data-theme="brutalist"] {
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
  --font-mono: 'JetBrains Mono', monospace;

  --radius-sm: 0;
  --radius-md: 0;
  --radius-lg: 0;

  --btn-border: 1px solid #000;
  --btn-border-right: 2px solid #000;
  --btn-border-bottom: 2px solid #000;
  --btn-active-border-top: 2px solid #000;
  --btn-active-border-left: 2px solid #000;

  --panel-shadow: 4px 4px 0 0 rgba(0, 0, 0, 1);
  --card-shadow: 2px 2px 0 0 rgba(0, 0, 0, 1);
}

/* 2. MATERIAL DESIGN (Google-like, amigable, tarjetas elevadas) */
:root[data-theme="material"] {
  --bg-main: #f5f5f5;
  --bg-panel: #ffffff;
  --border-color: #e0e0e0;
  --hairline: #eeeeee;
  --text-main: #212121;
  --text-muted: #757575;
  --highlight: #d32f2f;
  --highlight-hover: #b71c1c;
  --accent-blue: #1976d2;
  --accent-green: #388e3c;

  --font-display: 'Roboto', sans-serif;
  --font-mono: 'Roboto', sans-serif;
  --base-font-size: 15px;

  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;

  --panel-border: none;
  --panel-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --card-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);

  --topbar-bg: #1976d2;
  --topbar-border: none;
  --topbar-shadow: 0 2px 4px rgba(0,0,0,0.2);
  --version-bg: rgba(255,255,255,0.1);

  --btn-bg: #1976d2;
  --btn-hover: #1565c0;
  --text-on-btn: #fff;
  --btn-border: none;
  --btn-border-right: none;
  --btn-border-bottom: none;
  --btn-active-border-top: none;
  --btn-active-border-left: none;
  --btn-hover-shadow: 0 2px 4px rgba(0,0,0,0.2);

  --active-bg: #e3f2fd;
  --active-text: #1976d2;
  --hover-bg: #f5f5f5;

  --table-header-bg: #fafafa;
  --upload-bg: #fff;
  --input-bg: #f5f5f5;
  --input-focus-shadow: inset 0 -2px 0 #1976d2;
  --link-decor: none;
}

/* 3. FLAT DESIGN (Minimalista moderno, colores pastel) */
:root[data-theme="flat"] {
  --bg-main: #ecf0f1;
  --bg-panel: #ffffff;
  --border-color: #bdc3c7;
  --hairline: #ecf0f1;
  --text-main: #2c3e50;
  --text-muted: #7f8c8d;
  --highlight: #e74c3c;
  --highlight-hover: #c0392b;
  --accent-blue: #3498db;
  --accent-green: #2ecc71;

  --font-display: 'Inter', sans-serif;
  --font-mono: 'Inter', sans-serif;

  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;

  --panel-border: 1px solid #ecf0f1;
  --panel-shadow: none;
  --card-shadow: none;

  --topbar-bg: #2c3e50;
  --topbar-border: none;

  --btn-bg: #3498db;
  --btn-hover: #2980b9;
  --btn-border: none;
  --btn-border-right: none;
  --btn-border-bottom: none;
  --btn-active-border-top: none;
  --btn-active-border-left: none;
  --btn-active-transform: scale(0.98);

  --active-bg: #3498db;
  --active-text: #fff;

  --table-header-bg: #f8f9fa;
  --upload-bg: #fff;
  --input-bg: #fff;
  --link-decor: none;
}

/* 4. F.I.N LIGHT (Limpio, científico, alto contraste) */
:root[data-theme="light"] {
  --bg-main: #ffffff;
  --bg-panel: #fafafa;
  --border-color: #000000;
  --hairline: #e5e5e5;
  --text-main: #000000;
  --text-muted: #666666;
  --highlight: #ff3333;
  --highlight-hover: #cc0000;
  --accent-blue: #0000ff;
  --accent-green: #00cc00;

  --font-display: 'JetBrains Mono', monospace;
  --font-mono: 'JetBrains Mono', monospace;

  --radius-sm: 0;
  --radius-md: 0;
  --radius-lg: 0;

  --panel-border: 1px solid #000;
  --panel-shadow: none;
  --card-shadow: none;

  --topbar-bg: #fff;
  --topbar-text: #000;
  --topbar-border: 1px solid #000;

  --btn-bg: #fff;
  --btn-border: 1px solid #000;
  --btn-border-right: 1px solid #000;
  --btn-border-bottom: 1px solid #000;

  --active-bg: #000;
  --active-text: #fff;
}

/* 5. F.I.N DARK (Hacker, terminal, bajo impacto visual) */
:root[data-theme="dark"] {
  --bg-main: #0a0a0a;
  --bg-panel: #141414;
  --border-color: #333333;
  --hairline: #222222;
  --text-main: #e0e0e0;
  --text-muted: #888888;
  --highlight: #ff4444;
  --highlight-hover: #ff6666;
  --accent-blue: #4488ff;
  --accent-green: #00ff00;

  --font-display: 'JetBrains Mono', monospace;
  --font-mono: 'JetBrains Mono', monospace;

  --radius-sm: 2px;
  --radius-md: 4px;
  --radius-lg: 4px;

  --panel-border: 1px solid #333;
  --panel-shadow: 0 10px 30px rgba(0,0,0,0.5);
  --card-shadow: none;

  --topbar-bg: #000;
  --topbar-border: 1px solid #333;

  --btn-bg: #1a1a1a;
  --btn-border: 1px solid #444;
  --btn-border-right: 1px solid #444;
  --btn-border-bottom: 1px solid #444;

  --active-bg: #2a2a2a;
  --active-text: #fff;
  --hover-bg: #1f1f1f;

  --table-header-bg: #111;
  --upload-bg: #111;
  --input-bg: #0a0a0a;
  --expanded-bg: #0f0f0f;
  --active-sub-bg: #1f1f1f;
  --status-bg: #0a0a0a;
  --msg-bg: rgba(0, 255, 0, 0.05);
  --graph-bg: #0a0a0a;
}

/* Aplicación global básica */
body {
  margin: 0;
  background-color: var(--bg-main);
  color: var(--text-main);
  font-family: var(--font-display);
  font-size: var(--base-font-size, 14px);
  line-height: 1.4;
  transition: background-color 0.3s, color 0.3s;
}

/* Respeta la preferencia del sistema de reducir movimiento */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.001ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.001ms !important;
  }
}

.app-root {
  min-height: 100vh;
}

.auth-fade-enter-active,
.auth-fade-leave-active {
  transition: opacity 0.25s ease;
}
.auth-fade-enter-from,
.auth-fade-leave-to {
  opacity: 0;
}

/* Scrollbar adaptativo */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--bg-main); border-left: 1px solid var(--border-color); }
::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: var(--radius-sm); }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* Arreglos específicos para Material/Flat en Dashboard */
:root[data-theme="material"] .action-btn,
:root[data-theme="flat"] .action-btn {
  color: var(--text-on-btn, #fff);
}
:root[data-theme="material"] .link-btn,
:root[data-theme="flat"] .link-btn,
:root[data-theme="material"] .skin-selector,
:root[data-theme="flat"] .skin-selector {
  color: var(--topbar-text, #fff);
  border-color: rgba(255,255,255,0.3);
}
:root[data-theme="dark"] .action-btn { color: var(--text-main); }

/* Foco de teclado visible en toda la app (accesibilidad) */
button:focus-visible,
input:focus-visible,
textarea:focus-visible,
select:focus-visible,
a:focus-visible {
  outline: 2px solid var(--accent-blue);
  outline-offset: 2px;
}
</style>