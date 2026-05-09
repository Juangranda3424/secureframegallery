<template>
    <main class="public-gallery-page">
        <section class="public-heading">
            <div>
                <p class="eyebrow">Galeria publica</p>
                <h1>Albumes disponibles</h1>
                <p>Explora albumes e imagenes aprobadas para visualizacion publica.</p>
            </div>
            <router-link class="login-link" to="/login">
                <i class="pi pi-sign-in"></i>
                Iniciar sesion
            </router-link>
        </section>

        <section v-if="selectedAlbum" class="public-panel">
            <div class="panel-title split">
                <div>
                    <h2>{{ selectedAlbum.title }}</h2>
                    <p>{{ selectedAlbum.description || "Sin descripcion" }}</p>
                </div>
                <button class="secondary-action" type="button" @click="backToAlbums">
                    <i class="pi pi-arrow-left"></i>
                    Albumes
                </button>
            </div>

            <div v-if="loadingImages" class="empty-state">
                Cargando imagenes publicas...
            </div>

            <div v-else-if="images.length" class="image-grid">
                <figure v-for="image in images" :key="image.id" class="image-card" @click="openImage(image)">
                    <img :src="apiUrl + image.file_path" :alt="selectedAlbum.title">
                    <figcaption>
                        <i class="pi pi-check-circle"></i>
                        Publica
                    </figcaption>
                </figure>
            </div>

            <p v-else class="empty-state">Este album aun no tiene imagenes publicas.</p>
        </section>

        <section v-else class="public-panel">
            <div class="panel-title">
                <h2>Albumes aprobados</h2>
                <p>Selecciona un album para ver sus imagenes publicas.</p>
            </div>

            <div v-if="loadingAlbums" class="empty-state">
                Cargando albumes publicos...
            </div>

            <div v-else-if="albums.length" class="album-grid">
                <article
                    v-for="album in albums"
                    :key="album.id"
                    class="album-card"
                    @click="selectAlbum(album)"
                >
                    <div class="album-card-head">
                        <i class="pi pi-folder-open"></i>
                        <span>publico</span>
                    </div>
                    <h3>{{ album.title }}</h3>
                    <p>{{ album.description || "Sin descripcion" }}</p>
                </article>
            </div>

            <p v-else class="empty-state">Todavia no hay albumes publicos disponibles.</p>
        </section>

        <div v-if="previewImage" class="image-preview-backdrop" @click.self="closeImage">
            <section class="image-preview" role="dialog" aria-modal="true" aria-label="Imagen completa">
                <button class="close-preview" type="button" aria-label="Cerrar imagen" @click="closeImage">
                    <i class="pi pi-times"></i>
                </button>
                <img :src="apiUrl + previewImage.file_path" :alt="selectedAlbum?.title || 'Imagen publica'">
            </section>
        </div>
    </main>
</template>

<script setup>
import { onMounted, ref } from "vue";
import albumService from "@/services/albumService.js";
import imageService from "@/services/imageService.js";

const apiUrl = import.meta.env.VITE_API_URL.replace("/api/v1", "");
const albums = ref([]);
const images = ref([]);
const selectedAlbum = ref(null);
const loadingAlbums = ref(false);
const loadingImages = ref(false);
const previewImage = ref(null);

async function loadPublicAlbums() {
    loadingAlbums.value = true;
    try {
        const { data } = await albumService.getPublic();
        albums.value = data;
    } finally {
        loadingAlbums.value = false;
    }
}

async function selectAlbum(album) {
    selectedAlbum.value = album;
    images.value = [];
    loadingImages.value = true;

    try {
        const { data } = await imageService.listPublic(album.id);
        images.value = data;
    } finally {
        loadingImages.value = false;
    }
}

function backToAlbums() {
    selectedAlbum.value = null;
    images.value = [];
    previewImage.value = null;
}

function openImage(image) {
    previewImage.value = image;
}

function closeImage() {
    previewImage.value = null;
}

onMounted(loadPublicAlbums);
</script>

<style scoped>
.public-gallery-page {
  display: grid;
  align-content: start;
  min-height: 100vh;
  padding: 32px;
  background: #f7f8fb;
  color: #101828;
}

.public-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  width: 100%;
  margin-bottom: 20px;
}

.eyebrow {
  margin: 0 0 6px;
  color: #d32626;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}

.public-heading h1 {
  margin: 0;
  font-size: 2rem;
  line-height: 1.2;
}

.public-heading p {
  margin: 8px 0 0;
  color: #667085;
}

.login-link,
.secondary-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 40px;
  padding: 10px 16px;
  border: 0;
  border-radius: 6px;
  background: #091350;
  color: #fff;
  font-weight: 800;
  text-decoration: none;
  cursor: pointer;
}

.secondary-action {
  background: #eef2ff;
  color: #091350;
}

.public-panel {
  width: 100%;
  padding: 24px;
  border: 1px solid #e4e7ec;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 10px 30px rgba(16, 24, 40, 0.05);
}

.panel-title {
  margin-bottom: 20px;
}

.panel-title.split {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.panel-title h2 {
  margin: 0;
  font-size: 1.25rem;
}

.panel-title p {
  margin: 6px 0 0;
  color: #667085;
}

.album-grid,
.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(100%, 240px), 1fr));
  gap: 16px;
}

.album-card {
  min-width: 0;
  min-height: 160px;
  padding: 16px;
  border: 1px solid #e4e7ec;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.album-card:hover {
  border-color: #091350;
  box-shadow: 0 12px 26px rgba(9, 19, 80, 0.12);
  transform: translateY(-1px);
}

.album-card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.album-card-head i {
  color: #091350;
  font-size: 1.2rem;
}

.album-card-head span {
  min-height: 24px;
  padding: 3px 9px;
  border-radius: 999px;
  background: #e7f6ec;
  color: #157347;
  font-size: 0.8rem;
  font-weight: 800;
}

.album-card h3,
.album-card p {
  overflow-wrap: anywhere;
  word-break: break-word;
}

.album-card h3 {
  margin: 0 0 10px;
  font-size: 1.05rem;
}

.album-card p {
  margin: 0;
  color: #667085;
  line-height: 1.5;
}

.image-card {
  position: relative;
  overflow: hidden;
  min-width: 0;
  margin: 0;
  border: 1px solid #e4e7ec;
  border-radius: 8px;
  background: #f9fafb;
  cursor: zoom-in;
}

.image-card img {
  display: block;
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
}

.image-card figcaption {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 10px 12px;
  color: #157347;
  font-weight: 800;
}

.empty-state {
  margin: 0;
  padding: 18px;
  border: 1px dashed #d0d5dd;
  border-radius: 8px;
  background: #f9fafb;
  color: #667085;
}

.image-preview-backdrop {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: grid;
  place-items: center;
  padding: 28px;
  background: rgba(9, 19, 80, 0.78);
}

.image-preview {
  position: relative;
  display: grid;
  max-width: min(1120px, 100%);
  max-height: 92vh;
}

.image-preview img {
  display: block;
  max-width: 100%;
  max-height: 92vh;
  border-radius: 8px;
  background: #fff;
  object-fit: contain;
}

.close-preview {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 1;
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border: 0;
  border-radius: 999px;
  background: #fff;
  color: #091350;
  cursor: pointer;
}

@media (max-width: 760px) {
  .public-gallery-page {
    padding: 18px;
  }

  .public-heading,
  .panel-title.split {
    display: grid;
  }
}
</style>
