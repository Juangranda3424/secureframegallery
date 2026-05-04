<template>
    <main class="supervisor-page">
        <section>
            <h2>Albumes pendientes</h2>

            <article v-for="album in pendingAlbums" :key="album.id">
                <h3>{{ album.title }}</h3>
                <p>{{ album.description }}</p>
                <button @click="approveAlbum(album.id)">Aprobar</button>
                <button @click="rejectAlbum(album.id)">Rechazar</button>
            </article>
        </section>

        <section>
            <h2>Imagenes en cuarentena</h2>

            <article v-for="image in quarantineImages" :key="image.id">
                <img :src="apiUrl + image.file_path" alt="Imagen en cuarentena">
                <pre>{{ image.image_analysis }}</pre>
                <button @click="approveImage(image.id)">Aprobar</button>
                <button @click="rejectImage(image.id)">Rechazar</button>
            </article>
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
