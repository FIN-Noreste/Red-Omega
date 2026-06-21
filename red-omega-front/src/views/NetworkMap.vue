<template>
  <div class="map-container view-container">
    <div class="toolbar">
      <h2 class="view-title">ANÁLISIS DE ENLACES ESPACIALES</h2>
    </div>
    
    <div class="map-overlay">
      <div v-if="selectedNode" class="node-info-window">
        <div class="window-header">
          <span>{{ selectedNode.name }}</span>
          <button @click="selectedNode = null" class="close-btn">X</button>
        </div>
        <div class="window-body">
          <p><strong>CID:</strong> <span class="mono-text">{{ shortCid(selectedNode.id) }}</span></p>
          <p><strong>ORIGEN:</strong> @{{ selectedNode.author }}</p>
          <p><strong>TAGS:</strong> {{ selectedNode.tags.join(', ') }}</p>
          <a :href="`http://127.0.0.1:8080/ipfs/${selectedNode.id}`" target="_blank" class="action-btn link-btn">ABRIR ARCHIVO</a>
        </div>
      </div>
      <div v-else class="instruction-text">
        <p>> Arrastrar: Rotar | Scroll: Zoom | Clic: Inspeccionar</p>
      </div>
    </div>
    
    <div ref="graphContainer" class="canvas-3d"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import axios from 'axios';
import ForceGraph3D from '3d-force-graph';
import * as THREE from 'three';

const graphContainer = ref(null);
let graph = null;
const selectedNode = ref(null);

const API_URL = 'http://127.0.0.1:5000/api';
const getAuthHeaders = () => ({ Authorization: `Bearer ${localStorage.getItem('omega_jwt')}` });

const shortCid = (cid) => `${cid.substring(0, 8)}...${cid.substring(cid.length - 8)}`;

const initGraph = async () => {
  try {
    const res = await axios.get(`${API_URL}/network/graph`, { headers: getAuthHeaders() });
    const gData = res.data;

    graph = ForceGraph3D()(graphContainer.value)
      .graphData(gData)
      .backgroundColor('#ffffff') 
      .linkWidth(1)
      .linkColor(() => '#cccccc') // Lineas más claras
      .linkOpacity(0.8) 
      .nodeThreeObject(node => {
        const canvas = document.createElement('canvas');
        canvas.width = 128; // Más pequeño
        canvas.height = 32;
        const ctx = canvas.getContext('2d');

        ctx.fillStyle = '#ffffff'; 
        ctx.fillRect(0, 0, 128, 32);
        
        ctx.strokeStyle = '#000000'; 
        ctx.lineWidth = 2;
        ctx.strokeRect(0, 0, 128, 32);

        ctx.fillStyle = '#000000'; 
        // Fuente Times
        ctx.font = 'bold 12px "Times New Roman", serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        let displayName = node.name;
        if (displayName.length > 15) {
          displayName = displayName.substring(0, 12) + '...';
        }
        ctx.fillText(displayName, 64, 16);

        const texture = new THREE.CanvasTexture(canvas);
        texture.minFilter = THREE.LinearFilter; 
        
        const material = new THREE.SpriteMaterial({ map: texture });
        const sprite = new THREE.Sprite(material);
        
        sprite.scale.set(15, 3.75, 1); // Escala ajustada
        return sprite;
      })
      .onNodeClick(node => {
        selectedNode.value = node;
        const distance = 40;
        const distRatio = 1 + distance/Math.hypot(node.x, node.y, node.z);
        graph.cameraPosition(
          { x: node.x * distRatio, y: node.y * distRatio, z: node.z * distRatio }, 
          node, 
          1000
        );
      });

  } catch (err) {
    console.error("Fallo de renderizado espacial:", err);
  }
};

onMounted(() => { initGraph(); });
onBeforeUnmount(() => { if (graph) graph._destructor(); });
</script>

<style scoped>
.map-container { display: flex; flex-direction: column; position: relative; height: 100%; font-family: 'Times New Roman', Times, serif;}
.toolbar { background: #000; color: #fff; padding: 0.2rem 0.5rem; }
.view-title { margin: 0; font-size: 0.9rem; font-weight: bold;}

.canvas-3d { flex-grow: 1; cursor: crosshair; }

.map-overlay { position: absolute; top: 30px; left: 10px; z-index: 10; pointer-events: none; }
.instruction-text { background: rgba(255,255,255,0.8); border: 1px solid #000; padding: 0.2rem 0.5rem; font-size: 0.8rem; font-style: italic;}

.node-info-window { 
  background: #fff; border: 1px solid #000; box-shadow: 2px 2px 0px rgba(0,0,0,0.2); 
  pointer-events: auto; width: 280px; font-size: 0.85rem;
}
.window-header { 
  background: #000; color: #fff; padding: 0.2rem 0.5rem; display: flex; justify-content: space-between; align-items: center;
  font-weight: bold; font-size: 0.8rem;
}
.close-btn { background: #ccc; border: 1px solid #fff; color: #000; cursor: pointer; font-size: 0.7rem; padding: 0 0.3rem;}
.window-body { padding: 0.8rem; }
.window-body p { margin: 0.3rem 0;}
.mono-text { font-family: monospace; font-size: 0.8rem; color: #444;}

.action-btn {
  background: #e0e0e0; color: #000; border: 1px solid #000; border-right: 2px solid #000; border-bottom: 2px solid #000;
  padding: 0.2rem 0.5rem; font-family: inherit; font-weight: bold; font-size: 0.8rem; cursor: pointer; text-transform: uppercase;
  display: inline-block; margin-top: 0.5rem; text-decoration: none; text-align: center;
}
.action-btn:active { border: 1px solid #000; border-top: 2px solid #000; border-left: 2px solid #000; background: #ccc;}
</style>
