// src/services/api.js
//
// Punto único de configuración de red para toda la app.
// Antes, cada vista (Dashboard, Editor, Settings, NetworkHub, NetworkMap)
// repetía su propia constante API_URL y su propia función getAuthHeaders().
// Eso significaba 5 lugares distintos que tocar si cambiaba el backend o
// el esquema de autenticación. Ahora todo vive aquí.

import axios from 'axios';

export const API_BASE_URL = 'http://127.0.0.1:5000/api';
export const IPFS_GATEWAY_URL = 'http://127.0.0.1:8080/ipfs/';

const api = axios.create({ baseURL: API_BASE_URL });

// Adjunta automáticamente el JWT (si existe) a cada petición saliente.
// Las vistas ya no necesitan pasar `{ headers: getAuthHeaders() }` a mano.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('omega_jwt');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;