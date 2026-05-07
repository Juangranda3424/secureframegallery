<template>
    <main class="gallery-page">
        <GalleryHeader :loading="loading" @refresh="loadAlbums" />

        <GallerySummary
            :total="albums.length"
            :approved="approvedCount"
            :pending="pendingCount"
        />

        <GalleryTabs
            :active-tab="activeTab"
            :has-selected-album="!!selectedAlbum"
            @change="activeTab = $event"
        />

        <AlbumRequestForm
            v-if="activeTab === 'request'"
            :loading="loading"
            @submit="createAlbum"
        />

        <AlbumList
            v-if="activeTab === 'albums'"
            :albums="albums"
            :selected-album-id="selectedAlbum?.id"
            @select="selectAlbum"
        />

        <ImageUploadPanel
            v-if="activeTab === 'images' && selectedAlbum"
            :album="selectedAlbum"
            :images="images"
            :api-url="apiUrl"
            :uploading="uploading"
            :upload-result="uploadResult"
            :active-analysis-step="activeAnalysisStep"
            :analysis-steps="analysisSteps"
            @back="activeTab = 'albums'"
            @upload="uploadImage"
        />
    </main>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { onBeforeRouteUpdate } from "vue-router";
import albumService from "@/services/albumService.js";
import imageService from "@/services/imageService.js";
import GalleryHeader from "@/components/gallery/GalleryHeader.vue";
import GallerySummary from "@/components/gallery/GallerySummary.vue";
import GalleryTabs from "@/components/gallery/GalleryTabs.vue";
import AlbumRequestForm from "@/components/gallery/AlbumRequestForm.vue";
import AlbumList from "@/components/gallery/AlbumList.vue";
import ImageUploadPanel from "@/components/gallery/ImageUploadPanel.vue";

const apiUrl = import.meta.env.VITE_API_URL.replace("/api/v1","");
const albums = ref([]);
const images = ref([]);
const selectedAlbum = ref(null);
const loading = ref(false);
const activeTab = ref("albums");
const uploading = ref(false);
const activeAnalysisStep = ref("");
const uploadResult = ref(null);
const analysisSteps = [
    { key: "upload", label: "Recibiendo archivo" },
    { key: "metadata", label: "Limpiando metadatos EXIF" },
    { key: "stego", label: "Analizando imagen por esteganografia" },
    { key: "decision", label: "Registrando resultado de revision" },
];

const approvedCount = computed(() => albums.value.filter((album) => album.status === "approved").length);
const pendingCount = computed(() => albums.value.filter((album) => (album.status || "pending") === "pending").length);

async function loadAlbums() {
    const { data } = await albumService.getAll();
    albums.value = data;

    if (selectedAlbum.value) {
        const freshAlbum = data.find((album) => album.id === selectedAlbum.value.id);
        selectedAlbum.value = freshAlbum || null;
    }
}

async function createAlbum(album) {
    loading.value = true;
    try {
        await albumService.create({
            title: album.title,
            description: album.description,
            initial_priv: true
        });

        await loadAlbums();
        activeTab.value = "albums";
    } finally {
        loading.value = false;
    }
}

async function selectAlbum(album) {
    selectedAlbum.value = album;
    activeTab.value = "images";
    images.value = [];
    uploadResult.value = null;
    activeAnalysisStep.value = "";

    if (album.status === "approved") {
        const { data } = await imageService.list(album.id);
        images.value = data;
    }
}

async function uploadImage(event) {
    const file = event.target.files?.[0];
    if (!file || !selectedAlbum.value) return;

    uploading.value = true;
    uploadResult.value = null;
    activeAnalysisStep.value = "upload";

    try {
        await wait(450);
        activeAnalysisStep.value = "metadata";
        await wait(450);
        activeAnalysisStep.value = "stego";

        const { data: uploadedImage } = await imageService.upload(selectedAlbum.value.id, file);
        activeAnalysisStep.value = "decision";
        await wait(350);

        const { data } = await imageService.list(selectedAlbum.value.id);
        images.value = data;
        uploadResult.value = buildUploadResult(uploadedImage);
        event.target.value = "";
    } catch (error) {
        uploadResult.value = {
            status: "rejected",
            message: error.response?.data?.detail || "No se pudo completar el analisis de la imagen."
        };
    } finally {
        uploading.value = false;
    }
}

function buildUploadResult(image) {
    if (image.status === "quarantined") {
        return {
            status: "quarantined",
            message: "La imagen fue marcada como sospechosa y quedo en cuarentena para revision del supervisor."
        };
    }

    return {
        status: "approved",
        message: "La imagen paso la revision de esteganografia y fue aprobada."
    };
}

function wait(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

onMounted(loadAlbums);
onBeforeRouteUpdate(async () => {
    await loadAlbums();
});
</script>

<style scoped>
.gallery-page {
  display: grid;
  align-content: start;
  width: 100%;
  min-height: calc(100vh - 210px);
  padding: 32px;
  background: #f7f8fb;
  color: #101828;
}

@media (max-width: 760px) {
  .gallery-page {
    padding: 18px;
  }
}
</style>
