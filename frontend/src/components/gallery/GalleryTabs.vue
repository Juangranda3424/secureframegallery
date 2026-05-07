<template>
    <nav class="gallery-tabs" aria-label="Navegacion de albumes">
        <button type="button" :class="{ active: activeTab === 'request' }" @click="$emit('change', 'request')">
            <i class="pi pi-plus-circle"></i>
            Solicitar
        </button>
        <button type="button" :class="{ active: activeTab === 'albums' }" @click="$emit('change', 'albums')">
            <i class="pi pi-images"></i>
            Albumes
        </button>
        <button
            type="button"
            :class="{ active: activeTab === 'images' }"
            :disabled="!hasSelectedAlbum"
            @click="$emit('change', 'images')"
        >
            <i class="pi pi-upload"></i>
            Imagenes
        </button>
    </nav>
</template>

<script setup>
defineProps({
    activeTab: {
        type: String,
        required: true,
    },
    hasSelectedAlbum: {
        type: Boolean,
        default: false,
    },
});

defineEmits(["change"]);
</script>

<style scoped>
.gallery-tabs {
  display: flex;
  gap: 8px;
  width: 100%;
  margin-bottom: 18px;
  padding: 6px;
  border: 1px solid #e4e7ec;
  border-radius: 8px;
  background: #fff;
}

.gallery-tabs button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-width: 128px;
  padding: 10px 16px;
  border: 0;
  border-radius: 6px;
  background: transparent;
  color: #475467;
  font-weight: 700;
  cursor: pointer;
}

.gallery-tabs button.active {
  background: #091350;
  color: #fff;
}

.gallery-tabs button:disabled {
  color: #98a2b3;
  cursor: not-allowed;
}

@media (max-width: 760px) {
  .gallery-tabs {
    overflow-x: auto;
  }
}
</style>
