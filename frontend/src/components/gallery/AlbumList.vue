<template>
    <section class="workspace-panel">
        <div class="panel-title">
            <h2>Albumes registrados</h2>
            <p>Selecciona un album aprobado para subir imagenes.</p>
        </div>

        <div v-if="albums.length" class="album-grid">
            <article
                v-for="album in albums"
                :key="album.id"
                class="album-card"
                :class="{ selected: selectedAlbumId === album.id }"
                @click="$emit('select', album)"
            >
                <div class="album-card-head">
                    <i class="pi pi-folder"></i>
                    <div class="album-badges">
                        <span class="privacy-pill" :class="{ private: album.initial_priv }">
                            {{ album.initial_priv ? "privado" : "publico" }}
                        </span>
                        <span class="status-pill" :class="album.status || 'pending'">{{ album.status || "pending" }}</span>
                    </div>
                </div>
                <h3>{{ album.title }}</h3>
                <p>{{ album.description || "Sin descripcion" }}</p>
            </article>
        </div>
        <p v-else class="empty-state">Todavia no tienes albumes registrados.</p>
    </section>
</template>

<script setup>
defineProps({
    albums: {
        type: Array,
        required: true,
    },
    selectedAlbumId: {
        type: String,
        default: null,
    },
});

defineEmits(["select"]);
</script>

<style scoped>
.workspace-panel {
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

.panel-title h2 {
  margin: 0;
  font-size: 1.25rem;
}

.panel-title p {
  margin: 6px 0 0;
  color: #667085;
}

.album-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.album-card {
  min-height: 160px;
  border: 1px solid #e4e7ec;
  border-radius: 8px;
  padding: 16px;
  background: #fff;
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
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

.album-badges {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 6px;
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

.album-card:hover,
.album-card.selected {
  border-color: #091350;
  box-shadow: 0 12px 26px rgba(9, 19, 80, 0.12);
  transform: translateY(-1px);
}

.privacy-pill,
.status-pill {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 3px 9px;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 800;
}

.privacy-pill {
  background: #eef2ff;
  color: #091350;
}

.privacy-pill.private {
  background: #f2f4f7;
  color: #475467;
}

.status-pill {
  background: #fff4e5;
  color: #b54708;
}

.status-pill.approved {
  background: #e7f6ec;
  color: #157347;
}

.status-pill.rejected {
  background: #fdecec;
  color: #c1272d;
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
