import { ref } from 'vue';

// Eliminamos la constante STORAGE_KEY global estática

// Creamos un ref reactivo que estará vacío por defecto,
// pero lo poblaremos dinámicamente cuando sepamos quién es el usuario.
const privateNetworks = ref([]);

export function useNetworks() {
  
  // Función para inicializar/cargar las redes basadas en el usuario actual
  const loadNetworksForUser = (username) => {
    if (!username) return;
    const storageKey = `omega_networks_${username}`;
    try {
      const saved = localStorage.getItem(storageKey);
      privateNetworks.value = saved ? JSON.parse(saved) : [];
    } catch (e) {
      console.error('Error cargando redes para', username, e);
      privateNetworks.value = [];
    }
  };

  const addNetwork = (username, net) => {
    if (!username) return;
    const storageKey = `omega_networks_${username}`;
    privateNetworks.value.push(net);
    localStorage.setItem(storageKey, JSON.stringify(privateNetworks.value));
  };

  const removeNetwork = (username, id) => {
    if (!username) return;
    const storageKey = `omega_networks_${username}`;
    privateNetworks.value = privateNetworks.value.filter(n => n.id !== id);
    localStorage.setItem(storageKey, JSON.stringify(privateNetworks.value));
  };

  return { privateNetworks, loadNetworksForUser, addNetwork, removeNetwork };
}