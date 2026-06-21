<template>
  <div class="app-root">
    <AuthGate v-if="!isAuthenticated" @authenticated="onLogin" />
    <Dashboard v-else :current-user="currentUser" @logout="onLogout" />
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
  isAuthenticated.value = true;
};

const onLogout = () => {
  isAuthenticated.value = false;
  currentUser.value = '';
};

onMounted(() => {
  const savedCss = localStorage.getItem('omega_custom_css');

  const token = localStorage.getItem('omega_jwt');

  if (savedCss) {
    const styleEl = document.createElement('style');
    styleEl.id = 'omega-custom-css';
    styleEl.innerHTML = savedCss;
    document.head.appendChild(styleEl);
  }
  
  if (token) {
    isAuthenticated.value = true;
    currentUser.value = "Investigador"; 
  }
});
</script>

<style>
/* RESET BRUTALISTA */
:root {
  --bg: #ffffff;
  --fg: #000000;
  --link: #0000EE;
  --border: 1px solid #000;
}

body { 
  margin: 0; 
  background-color: var(--bg); 
  color: var(--fg);
  font-family: 'TIMES NEW ROMAN', serif;
  font-size: 14px;
  line-height: 1.3;
  -webkit-font-smoothing: none; /* Aspecto pixelado crudo */
}

.app-root { 
  min-height: 100vh; 
  padding: 1rem; 
}

/* Scrollbar crudo */
::-webkit-scrollbar { width: 10px; height: 10px; border-left: var(--border); }
::-webkit-scrollbar-track { background: #fff; }
::-webkit-scrollbar-thumb { background: #000; }
</style>