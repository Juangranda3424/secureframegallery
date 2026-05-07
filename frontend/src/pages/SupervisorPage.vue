<template>
    <main class="supervisor-page">
        <section class="page-heading">
            <div>
                <p class="eyebrow">Panel de revision</p>
                <h1>Supervisor</h1>
                <p>Aprueba albumes y revisa imagenes retenidas por el analisis de seguridad.</p>
            </div>
            <button class="primary-action" type="button" @click="loadData">
                <i class="pi pi-refresh"></i>
                Actualizar
            </button>
        </section>

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
                        <button class="approve" @click="approveAlbum(album.id)">
                            <i class="pi pi-check"></i>
                            Aprobar
                        </button>
                        <button class="reject" @click="rejectAlbum(album.id)">
                            <i class="pi pi-times"></i>
                            Rechazar
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
                    <pre>{{ image.image_analysis }}</pre>
                    <div class="review-actions">
                        <button class="approve" @click="approveImage(image.id)">
                            <i class="pi pi-check"></i>
                            Aprobar
                        </button>
                        <button class="reject" @click="rejectImage(image.id)">
                            <i class="pi pi-trash"></i>
                            Rechazar
                        </button>
                    </div>
                </article>
            </div>
            <p v-else class="empty-state">No hay imagenes en cuarentena.</p>
        </section>

    </main>
</template>

<script setup>
import { onMounted, ref } from "vue";
import albumService from "@/services/albumService.js";
import imageService from "@/services/imageService.js";

const apiUrl = import.meta.env.VITE_API_URL.replace("/api/v1","");
const pendingAlbums = ref([]);
const quarantineImages = ref([]);

async function loadData() {
    const albumsResp = await albumService.getPending();
    pendingAlbums.value = albumsResp.data;

    const quarantineResp = await imageService.listQuarantine();
    quarantineImages.value = quarantineResp.data;
}

async function approveAlbum(albumId) {
    await albumService.approve(albumId);
    await loadData();
}

async function rejectAlbum(albumId) {
    await albumService.reject(albumId);
    await loadData();
}

async function approveImage(imageId) {
    await imageService.approve(imageId);
    await loadData();
}

async function rejectImage(imageId) {
    await imageService.rejectQuarantine(imageId);
    await loadData();
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
