<template>
    <main class="supervisor-page">
        <section class="page-heading">
            <div>
                <p class="eyebrow">Panel de revision</p>
                <h1>Supervisor</h1>
                <p>Aprueba albumes y revisa imagenes retenidas por el analisis de seguridad.</p>
            </div>
            <button class="primary-action" type="button" :disabled="isBusy" @click="loadData">
                <i :class="isRefreshing ? 'pi pi-spin pi-spinner' : 'pi pi-refresh'"></i>
                {{ isRefreshing ? "Actualizando" : "Actualizar" }}
            </button>
        </section>

        <div v-if="actionMessage" class="action-status">
            <i class="pi pi-spin pi-spinner"></i>
            {{ actionMessage }}
        </div>

        <section class="review-panel">
            <div class="panel-title">
                <h2>Albumes pendientes</h2>
                <span>{{ pendingAlbums.length }} en revision</span>
            </div>

            <div v-if="pendingAlbums.length" class="review-grid">
                <article v-for="album in pendingAlbums" :key="album.id" class="review-card">
                    <h3>{{ album.title }}</h3>
                    <p>{{ album.description || "Sin descripcion" }}</p>
                    <div class="review-actions">
                        <button class="approve" :disabled="isBusy" @click="approveAlbum(album.id)">
                            <i :class="actionKey === `album-approve-${album.id}` ? 'pi pi-spin pi-spinner' : 'pi pi-check'"></i>
                            {{ actionKey === `album-approve-${album.id}` ? "Aprobando" : "Aprobar" }}
                        </button>
                        <button class="reject" :disabled="isBusy" @click="rejectAlbum(album.id)">
                            <i :class="actionKey === `album-reject-${album.id}` ? 'pi pi-spin pi-spinner' : 'pi pi-times'"></i>
                            {{ actionKey === `album-reject-${album.id}` ? "Rechazando" : "Rechazar" }}
                        </button>
                    </div>
                </article>
            </div>
            <p v-else class="empty-state">No hay albumes pendientes.</p>
        </section>

        <section class="review-panel">
            <div class="panel-title">
                <h2>Imagenes en cuarentena</h2>
                <span>{{ quarantineImages.length }} retenidas</span>
            </div>

            <div v-if="quarantineImages.length" class="review-grid image-review-grid">
                <article v-for="image in quarantineImages" :key="image.id" class="review-card">
                    <img :src="apiUrl + image.file_path" alt="Imagen en cuarentena">
                    <div class="quarantine-meta">
                        <span>Album</span>
                        <strong>{{ image.album_title || image.album?.title || "Album no encontrado" }}</strong>
                    </div>
                    <details class="analysis-details">
                        <summary>Ver analisis</summary>
                        <pre>{{ formatAnalysis(image.image_analysis) }}</pre>
                    </details>
                    <div class="review-actions">
                        <button class="approve" :disabled="isBusy" @click="approveImage(image.id)">
                            <i :class="actionKey === `image-approve-${image.id}` ? 'pi pi-spin pi-spinner' : 'pi pi-check'"></i>
                            {{ actionKey === `image-approve-${image.id}` ? "Aprobando" : "Aprobar" }}
                        </button>
                        <button class="reject" :disabled="isBusy" @click="rejectImage(image.id)">
                            <i :class="actionKey === `image-reject-${image.id}` ? 'pi pi-spin pi-spinner' : 'pi pi-trash'"></i>
                            {{ actionKey === `image-reject-${image.id}` ? "Rechazando" : "Rechazar" }}
                        </button>
                    </div>
                </article>
            </div>
            <p v-else class="empty-state">No hay imagenes en cuarentena.</p>
        </section>

    </main>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import albumService from "@/services/albumService.js";
import imageService from "@/services/imageService.js";

const apiUrl = import.meta.env.VITE_API_URL.replace("/api/v1","");
const pendingAlbums = ref([]);
const quarantineImages = ref([]);
const actionKey = ref("");
const actionMessage = ref("");
const isRefreshing = ref(false);

const isBusy = computed(() => !!actionKey.value || isRefreshing.value);

async function loadData() {
    isRefreshing.value = true;
    try {
        const albumsResp = await albumService.getPending();
        pendingAlbums.value = albumsResp.data;

        const quarantineResp = await imageService.listQuarantine();
        quarantineImages.value = quarantineResp.data;
    } finally {
        isRefreshing.value = false;
    }
}

async function approveAlbum(albumId) {
    await runReviewAction(`album-approve-${albumId}`, "Aprobando album", async () => {
        await albumService.approve(albumId);
    });
}

async function rejectAlbum(albumId) {
    await runReviewAction(`album-reject-${albumId}`, "Rechazando album", async () => {
        await albumService.reject(albumId);
    });
}

async function approveImage(imageId) {
    await runReviewAction(`image-approve-${imageId}`, "Aprobando imagen en cuarentena", async () => {
        await imageService.approve(imageId);
    });
}

async function rejectImage(imageId) {
    await runReviewAction(`image-reject-${imageId}`, "Rechazando y eliminando imagen", async () => {
        await imageService.rejectQuarantine(imageId);
    });
}

async function runReviewAction(key, message, action) {
    actionKey.value = key;
    actionMessage.value = message;
    try {
        await action();
        await loadData();
    } finally {
        actionKey.value = "";
        actionMessage.value = "";
    }
}

function formatAnalysis(analysis) {
    if (!analysis?.length) {
        return "No hay registro de analisis para esta imagen.";
    }

    return analysis
        .map((item) => item.result || JSON.stringify(item, null, 2))
        .join("\n\n");
}

onMounted(loadData);
</script>

<style scoped>
.supervisor-page {
  min-height: calc(100vh - 210px);
  padding: 32px;
  background: #f7f8fb;
  color: #101828;
}

.page-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  width: 100%;
  margin-bottom: 22px;
}

.eyebrow {
  margin: 0 0 6px;
  color: #d32626;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}

.page-heading h1 {
  margin: 0;
  font-size: 2rem;
}

.page-heading p {
  margin: 8px 0 0;
  color: #667085;
}

.primary-action {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 40px;
  padding: 10px 16px;
  border: 0;
  border-radius: 6px;
  background: #091350;
  color: #fff;
  font-weight: 800;
  cursor: pointer;
  transition: background-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.primary-action:disabled {
  opacity: 0.72;
  cursor: wait;
}

.primary-action:hover {
  background: #111d6b;
  box-shadow: 0 10px 20px rgba(9, 19, 80, 0.18);
  transform: translateY(-1px);
}

.primary-action:disabled:hover {
  box-shadow: none;
  transform: none;
}

.action-status {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 18px;
  padding: 12px 14px;
  border: 1px solid #b8c0ea;
  border-radius: 8px;
  background: #f8faff;
  color: #091350;
  font-weight: 800;
  animation: status-in 0.18s ease;
}

@keyframes status-in {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}


.review-panel {
  width: 100%;
  margin-bottom: 20px;
  padding: 24px;
  border: 1px solid #e4e7ec;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 10px 30px rgba(16, 24, 40, 0.05);
}

.panel-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.panel-title h2 {
  margin: 0;
  font-size: 1.25rem;
}

.panel-title span {
  color: #667085;
  font-weight: 700;
}

.review-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.review-card {
  padding: 16px;
  border: 1px solid #e4e7ec;
  border-radius: 8px;
  background: #fff;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.review-card:hover {
  border-color: #b8c0ea;
  box-shadow: 0 12px 26px rgba(16, 24, 40, 0.08);
  transform: translateY(-1px);
}

.review-card h3 {
  margin: 0 0 8px;
}

.review-card p {
  margin: 0 0 16px;
  color: #667085;
}

.review-card img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #e4e7ec;
}

.review-card pre {
  max-height: 140px;
  overflow: auto;
  padding: 10px;
  border-radius: 6px;
  background: #f9fafb;
  color: #344054;
  white-space: pre-wrap;
}

.quarantine-meta {
  display: grid;
  gap: 4px;
  margin: 12px 0;
  padding: 10px 12px;
  border-radius: 6px;
  background: #f8faff;
}

.quarantine-meta span {
  color: #667085;
  font-size: 0.78rem;
  font-weight: 800;
  text-transform: uppercase;
}

.quarantine-meta strong {
  color: #091350;
}

.analysis-details {
  margin-bottom: 12px;
}

.analysis-details summary {
  color: #091350;
  font-weight: 800;
  cursor: pointer;
}

.review-actions {
  display: flex;
  gap: 8px;
}

.review-actions button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  min-height: 36px;
  padding: 8px 12px;
  border: 0;
  border-radius: 6px;
  color: #fff;
  font-weight: 800;
  cursor: pointer;
  transition: filter 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.review-actions button:hover {
  filter: brightness(1.06);
  box-shadow: 0 8px 18px rgba(16, 24, 40, 0.14);
  transform: translateY(-1px);
}

.review-actions button:disabled {
  opacity: 0.72;
  cursor: wait;
}

.review-actions button:disabled:hover {
  box-shadow: none;
  filter: none;
  transform: none;
}

.review-actions button:active,
.primary-action:active {
  transform: translateY(0);
}

.approve {
  background: #157347;
}

.reject {
  background: #d32626;
}

.empty-state {
  margin: 0;
  padding: 18px;
  border: 1px dashed #d0d5dd;
  border-radius: 8px;
  background: #f9fafb;
  color: #667085;
}
</style>
