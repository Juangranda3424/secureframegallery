<template>
    <main class="gallery-page">
        <GalleryHeader
            :loading="loading"
            :unread-count="unreadCount"
            :notifications-open="notificationsOpen"
            :notifications="notifications"
            @refresh="loadAlbums"
            @toggle-notifications="toggleNotifications"
        />

        <GallerySummary
            :total="albums.length"
            :approved="approvedCount"
            :pending="pendingCount"
        />

        <GalleryTabs
            v-if="activeTab !== 'images'"
            :active-tab="activeTab"
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
            :active-analysis-step="activeAnalysisStep"
            :analysis-steps="analysisSteps"
            @back="activeTab = 'albums'"
            @upload="uploadImage"
            @delete-image="deleteImage"
        />

        <ConfirmModal
            :visible="deleteConfirm.visible"
            title="Eliminar imagen"
            message="Esta imagen se eliminará del álbum y no podrá recuperarse desde la galería."
            confirm-label="Eliminar"
            loading-label="Eliminando imagen"
            icon="pi pi-trash"
            severity="danger"
            :loading="deletingImage"
            @cancel="closeDeleteConfirm"
            @confirm="confirmDeleteImage"
        />
    </main>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from "vue";
import { onBeforeRouteUpdate } from "vue-router";
import albumService from "@/services/albumService.js";
import imageService from "@/services/imageService.js";
import notificationService from "@/services/notificationService.js";
import GalleryHeader from "@/components/gallery/GalleryHeader.vue";
import GallerySummary from "@/components/gallery/GallerySummary.vue";
import GalleryTabs from "@/components/gallery/GalleryTabs.vue";
import AlbumRequestForm from "@/components/gallery/AlbumRequestForm.vue";
import AlbumList from "@/components/gallery/AlbumList.vue";
import ImageUploadPanel from "@/components/gallery/ImageUploadPanel.vue";
import ConfirmModal from "@/components/general/ConfirmModal.vue";
import { useToastGlobal } from "@/helpers/utils.js";

const apiUrl = import.meta.env.VITE_API_URL.replace("/api/v1","");
const albums = ref([]);
const images = ref([]);
const selectedAlbum = ref(null);
const loading = ref(false);
const activeTab = ref("albums");
const uploading = ref(false);
const deletingImage = ref(false);
const activeAnalysisStep = ref("");
const deleteConfirm = ref({
    visible: false,
    image: null,
});
const notifications = ref([]);
const notificationsOpen = ref(false);
const shownNotificationIds = new Set();
let notificationInterval = null;
const { msjShow } = useToastGlobal();
const analysisSteps = [
    { key: "upload", label: "Recibiendo archivo" },
    { key: "metadata", label: "Limpiando metadatos EXIF" },
    { key: "stego", label: "Analizando imagen por esteganografia" },
    { key: "decision", label: "Registrando resultado de revision" },
];

const approvedCount = computed(() => albums.value.filter((album) => album.status === "approved").length);
const pendingCount = computed(() => albums.value.filter((album) => (album.status || "pending") === "pending").length);
const unreadCount = computed(() => notifications.value.filter((notification) => !notification.read).length);

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
        notifyUploadResult(uploadedImage);
        event.target.value = "";
    } catch (error) {
        const message = error.response?.data?.detail || "No se pudo completar el analisis de la imagen.";
        msjShow("error", "Error al analizar", message, 4500);
    } finally {
        uploading.value = false;
        activeAnalysisStep.value = "";
    }
}

async function deleteImage(image) {
    deleteConfirm.value = {
        visible: true,
        image,
    };
}

function closeDeleteConfirm(force = false) {
    if (deletingImage.value && !force) return;

    deleteConfirm.value = {
        visible: false,
        image: null,
    };
}

async function confirmDeleteImage() {
    if (!selectedAlbum.value || !deleteConfirm.value.image) return;

    deletingImage.value = true;
    try {
        await imageService.remove(selectedAlbum.value.id, deleteConfirm.value.image.id);
        images.value = images.value.filter((item) => item.id !== deleteConfirm.value.image.id);
        msjShow("success", "Imagen eliminada", "La imagen fue eliminada del album.", 3000);
        closeDeleteConfirm(true);
    } finally {
        deletingImage.value = false;
    }
}

function notifyUploadResult(image) {
    if (image.status === "quarantined") {
        const result = {
            status: "quarantined",
            message: "La imagen fue marcada como sospechosa y quedo en cuarentena para revision del supervisor."
        };

        msjShow(
            "warn",
            "Imagen enviada a revision",
            result.message,
            5200
        );

        return result;
    }

    const result = {
        status: "approved",
        message: "La imagen paso el analisis de seguridad y ya esta disponible en el album."
    };

    msjShow(
        "success",
        "Imagen aprobada",
        result.message,
        4200
    );

    return result;
}

async function loadNotifications() {
    const { data } = await notificationService.list();
    notifications.value = data;
}

async function toggleNotifications() {
    notificationsOpen.value = !notificationsOpen.value;
    await loadNotifications();

    if (notificationsOpen.value) {
        const unread = notifications.value.filter((notification) => !notification.read);
        await Promise.all(unread.map((notification) => notificationService.markRead(notification.id)));
        notifications.value = notifications.value.map((notification) => ({
            ...notification,
            read: true,
        }));
    }
}

async function pollNotifications() {
    try {
        const { data } = await notificationService.unread();
        if (!data.length) return;

        await loadNotifications();

        for (const notification of data) {
            if (shownNotificationIds.has(notification.id)) continue;
            shownNotificationIds.add(notification.id);

            msjShow(
                notification.type === "approved" ? "success" : notification.type === "rejected" ? "error" : "info",
                notification.title,
                notification.message,
                6500
            );
        }

        if (data.some((notification) => notification.type === "approved")) {
            await loadAlbums();
            if (selectedAlbum.value?.status === "approved") {
                const { data: refreshedImages } = await imageService.list(selectedAlbum.value.id);
                images.value = refreshedImages;
            }
        }
    } catch (error) {
        console.warn("No se pudieron consultar notificaciones", error);
    }
}

function wait(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

onMounted(async () => {
    await loadAlbums();
    await loadNotifications();
    await pollNotifications();
    notificationInterval = window.setInterval(pollNotifications, 10000);
});

onUnmounted(() => {
    if (notificationInterval) {
        window.clearInterval(notificationInterval);
    }
});

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
