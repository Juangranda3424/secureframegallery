<template>
    <Teleport to="body">
        <div v-if="visible" class="modal-backdrop">
            <section class="confirm-modal" role="dialog" aria-modal="true">
                <div class="modal-icon" :class="severity">
                    <i :class="icon"></i>
                </div>
                <div>
                    <h2>{{ title }}</h2>
                    <p>{{ message }}</p>
                </div>
                <div class="modal-actions">
                    <button class="cancel-action" type="button" :disabled="loading" @click="$emit('cancel')">
                        Cancelar
                    </button>
                    <button class="confirm-action" type="button" :class="severity" :disabled="loading" @click="$emit('confirm')">
                        <i v-if="loading" class="pi pi-spin pi-spinner"></i>
                        {{ loading ? loadingLabel : confirmLabel }}
                    </button>
                </div>
            </section>
        </div>
    </Teleport>
</template>

<script setup>
defineProps({
    visible: {
        type: Boolean,
        default: false,
    },
    title: {
        type: String,
        required: true,
    },
    message: {
        type: String,
        required: true,
    },
    confirmLabel: {
        type: String,
        default: "Confirmar",
    },
    loadingLabel: {
        type: String,
        default: "Procesando",
    },
    icon: {
        type: String,
        default: "pi pi-exclamation-triangle",
    },
    severity: {
        type: String,
        default: "danger",
    },
    loading: {
        type: Boolean,
        default: false,
    },
});

defineEmits(["cancel", "confirm"]);
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 10000;
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgba(16, 24, 40, 0.52);
  animation: fade-in 0.18s ease;
}

.confirm-modal {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 16px;
  width: min(480px, 100%);
  padding: 22px;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 24px 70px rgba(16, 24, 40, 0.28);
  animation: modal-in 0.2s ease;
}

.modal-icon {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  border-radius: 8px;
  background: #fdecec;
  color: #d32626;
}

.modal-icon.info {
  background: #eef2ff;
  color: #091350;
}

.confirm-modal h2 {
  margin: 0;
  color: #101828;
  font-size: 1.16rem;
}

.confirm-modal p {
  margin: 8px 0 0;
  color: #667085;
  line-height: 1.45;
}

.modal-actions {
  grid-column: 1 / -1;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 4px;
}

.modal-actions button {
  min-height: 40px;
  padding: 10px 14px;
  border: 0;
  border-radius: 6px;
  font-weight: 800;
  cursor: pointer;
}

.cancel-action {
  background: #f2f4f7;
  color: #344054;
}

.confirm-action {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #d32626;
  color: #fff;
}

.confirm-action.info {
  background: #091350;
}

.modal-actions button:disabled {
  opacity: 0.7;
  cursor: wait;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes modal-in {
  from {
    opacity: 0;
    transform: translateY(8px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
</style>
