<template>
    <section class="page-heading">
        <div>
            <p class="eyebrow">Galeria segura</p>
            <h1>Mis albumes</h1>
            <p class="heading-copy">Solicita albumes, espera aprobacion y sube imagenes para revision automatica.</p>
        </div>
        <button class="primary-action" type="button" :disabled="loading" @click="$emit('refresh')">
            <i class="pi pi-refresh"></i>
            Actualizar
        </button>
    </section>
</template>

<script setup>
defineProps({
    loading: {
        type: Boolean,
        default: false,
    },
});

defineEmits(["refresh"]);
</script>

<style scoped>
.page-heading {
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

.page-heading h1 {
  margin: 0;
  font-size: 2rem;
  line-height: 1.2;
}

.heading-copy {
  margin: 8px 0 0;
  color: #667085;
}

.primary-action {
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
  font-weight: 700;
  cursor: pointer;
}

.primary-action:disabled {
  opacity: 0.65;
  cursor: wait;
}

@media (max-width: 760px) {
  .page-heading {
    display: grid;
  }
}
</style>
