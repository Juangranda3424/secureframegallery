<template>
    <main class="gallery-page">
        <section class="toolbar">
            <h2>Mis albumes</h2>

            <form @submit.prevent="createAlbum" class="album-form">
                <input v-model="form.title" maxlength="100"
                    placeholder="Título del álbum" required>
                    <textarea v-model="form.description" maxlength="500" placeholder="Descripcion"></textarea>
                    <button type="submit" :disabled="loading">Solicitar album</button>

            </form>
        </section>

        <section class="album-grid">
            <article
            v-for="album in albums"
            :key="album.id"
            class="album-card"
            @click="selectAlbum(album)"
            >
            <h3>{{ album.title }}</h3>
            <p>{{ album.description }}</p>
            <span>{{ album.status || "pending" }}</span>
        </article>
        </section>

        <section v-if="selectedAlbum" class="images-panel">
            <h2>{{ selectedAlbum.title }}</h2>

            <input
            v-if="selectedAlbum.status === 'approved'"
            type="file"
            accept="image/png,image/jpeg,image/webp,image/gif"
            @change="uploadImage"
            />

            <p v-else>Este album todavia no esta aprobado</p>

            <div class="image-grid">
                <img
                v-for="image in images"
                :key="image.id"
                :src="apiUrl + image.file_path"
                :alt="selectedAlbum.title">
            </div>

        </section>

    </main>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import albumService from "@/services/albumService.js";
import imageService from "@/services/imageService.js";

const apiUrl = import.meta.env.VITE_API_URL.replace("/api/v1","");
const albums = ref([]);
const images = ref([]);
const selectedAlbum = ref(null);
const loading = ref(false);

const form = reactive({
    title: "",
    description: "",
});

async function loadAlbums() {
    const { data } = await albumService.getAll();
    albums.value = data;
}

async function createAlbum() {
    if (!form.title.trim()) return;

    loading.value = true;
    try {
        await albumService.create({
            title: form.title,
            description: form.description,
            initial_priv: true
        });

        form.title = "";
        form.description = "";
        await loadAlbums();
    } finally {
        loading.value = false;
    }
}

async function selectAlbum(album) {
    selectedAlbum.value = album;
    images.value = [];

    if (album.status === "approved") {
        const { data } = await imageService.list(album.id);
        images.value = data;
    }
}

async function uploadImage(event) {
    const file = event.target.files?.[0];
    if (!file || !selectedAlbum.value) return;

    await imageService.upload(selectedAlbum.value.id, file);
    const { data} = await imageService.list(selectedAlbum.value.id);
    images.value = data;
    event.target.value = "";
}

onMounted(loadAlbums);

</script>

<style scoped>
.gallery-page {
  padding: 24px;
}

.toolbar {
  display: grid;
  gap: 16px;
  margin-bottom: 24px;
}

.album-form {
  display: grid;
  gap: 12px;
  max-width: 520px;
}

.album-form input,
.album-form textarea {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 6px;
}

.album-grid,
.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.album-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
}

.album-card:hover {
  border-color: #091350;
}

.images-panel {
  margin-top: 32px;
}

.image-grid img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: 8px;
}

</style>
