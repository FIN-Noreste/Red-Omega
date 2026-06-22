// src/utils/format.js
//
// Funciones de formato reutilizadas en varias vistas. Antes existían
// 3 copias ligeramente distintas de `shortCid` (Dashboard, NetworkHub,
// NetworkMap) y 2 de `formatDate`/`getExtension`. Centralizarlas evita que
// se desincronicen y reduce el tamaño de cada componente.

/**
 * Abrevia un CID/hash para mostrarlo en UI: "QmAbc1234...9f8e7d6c".
 * prefixLen/suffixLen son configurables porque distintas vistas usan
 * distintos anchos de columna (la tabla de la Bóveda necesita más
 * espacio que las tarjetas del feed).
 */
export const shortCid = (cid, prefixLen = 8, suffixLen = 8) => {
  if (!cid) return '';
  if (cid.length <= prefixLen + suffixLen) return cid;
  return `${cid.slice(0, prefixLen)}...${cid.slice(-suffixLen)}`;
};

/** Formatea una fecha ISO a "dd/mm/aaaa hh:mm" usando el locale del navegador. */
export const formatDate = (dateString) => {
  if (!dateString) return '';
  const d = new Date(dateString);
  if (Number.isNaN(d.getTime())) return '';
  return `${d.toLocaleDateString()} ${d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
};

/** Extrae la extensión de un nombre de archivo en mayúsculas, o '???' si no hay. */
export const getFileExtension = (filename) => {
  const dotIndex = filename ? filename.lastIndexOf('.') : -1;
  if (dotIndex <= 0) return '???';
  return filename.slice(dotIndex + 1).toUpperCase();
};

/**
 * Convierte un título arbitrario (con acentos, signos, espacios) en un
 * nombre de archivo seguro tipo "mi_titulo_aqui". Antes el código solo
 * hacía `.replace(/\s+/g, '_')`, así que títulos con símbolos como
 * "¿Qué hacer?" o "100% seguro" generaban nombres de archivo con
 * caracteres no válidos.
 */
export const slugify = (text, fallback = 'documento') => {
  if (!text) return fallback;
  const slug = text
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // quita acentos
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '');
  return slug || fallback;
};

/** Genera un identificador corto aleatorio (para nombres de respuestas, etc). */
export const generateRandomId = () => {
  if (window.crypto?.randomUUID) {
    return window.crypto.randomUUID().slice(0, 8);
  }
  return Math.floor(Math.random() * 1e9).toString(36);
};