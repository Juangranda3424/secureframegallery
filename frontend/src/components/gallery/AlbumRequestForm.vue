<template>
    <section class="workspace-panel">
        <div class="panel-title">
            <h2>Solicitar nuevo album</h2>
            <p>Quedara en revision hasta que un supervisor lo apruebe.</p>
        </div>

        <form class="album-form" @submit.prevent="submitAlbum">
            <label>
                Titulo
                <input v-model="draft.title" maxlength="100" placeholder="Ej. Evidencia de campo" required>
            </label>
            <label>
                Descripcion
                <textarea v-model="draft.description" maxlength="500" placeholder="Describe el contenido esperado"></textarea>
            </label>
            <fieldset class="visibility-field">
                <legend>Visibilidad</legend>
                <label class="visibility-option" :class="{ active: !draft.initial_priv }">
                    <input v-model="draft.initial_priv" type="radio" :value="false">
                    <span>
                        <strong>Publico</strong>
                        <small>Visible para visitantes cuando sea aprobado.</small>
                    </span>
                </label>
                <label class="visibility-option" :class="{ active: draft.initial_priv }">
                    <input v-model="draft.initial_priv" type="radio" :value="true">
                    <span>
                        <strong>Privado</strong>
                        <small>Visible solo dentro de tu cuenta.</small>
                    </span>
                </label>
            </fieldset>
            <button class="submit-action" type="submit" :disabled="loading">
                <i class="pi pi-send"></i>
                Solicitar album
            </button>
        </form>
    </section>
</template>

<script setup>
import { reactive } from "vue";

defineProps({
    loading: {
        type: Boolean,
        default: false,
    },
});

const emit = defineEmits(["submit"]);

const draft = reactive({
    title: "",
    description: "",
    initial_priv: false,
});

function submitAlbum() {
    if (!draft.title.trim()) return;

    emit("submit", {
        title: draft.title,
        description: draft.description,
        initial_priv: draft.initial_priv,
    });

    draft.title = "";
    draft.description = "";
    draft.initial_priv = false;
}
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

.album-form {
  display: grid;
  gap: 16px;
  max-width: 760px;
}

.album-form label {
  display: grid;
  gap: 8px;
  color: #344054;
  font-weight: 700;
}

.album-form input,
.album-form textarea {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #d0d5dd;
  border-radius: 6px;
  color: #101828;
  font: inherit;
}

.album-form textarea {
  min-height: 112px;
  resize: vertical;
}

.visibility-field {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin: 0;
  padding: 0;
  border: 0;
}

.visibility-field legend {
  grid-column: 1 / -1;
  margin-bottom: 8px;
  color: #344054;
  font-weight: 700;
}

.visibility-option {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 10px;
  padding: 12px;
  border: 1px solid #d0d5dd;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
}

.visibility-option.active {
  border-color: #091350;
  background: #f8faff;
}

.visibility-option input {
  width: auto;
  margin-top: 3px;
}

.visibility-option span {
  display: grid;
  gap: 2px;
  min-width: 0;
}

.visibility-option small {
  color: #667085;
  font-weight: 500;
  line-height: 1.35;
}

.submit-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: fit-content;
  min-height: 40px;
  padding: 10px 16px;
  border: 0;
  border-radius: 6px;
  background: #d32626;
  color: #fff;
  font-weight: 700;
  cursor: pointer;
}

.submit-action:disabled {
  opacity: 0.65;
  cursor: wait;
}

@media (max-width: 640px) {
  .visibility-field {
    grid-template-columns: 1fr;
  }
}
</style>
