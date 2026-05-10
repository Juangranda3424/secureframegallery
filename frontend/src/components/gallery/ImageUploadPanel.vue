<template>
    <section class="workspace-panel images-panel">
        <div class="panel-title split">
            <div>
                <h2>{{ album.title }}</h2>
                <p>Estado del album: <span class="status-pill" :class="album.status">{{ album.status }}</span></p>
            </div>
            <button class="secondary-action" type="button" @click="$emit('back')">
                <i class="pi pi-arrow-left"></i>
                Regresar a albumes
            </button>
        </div>

        <div v-if="album.status === 'approved'" class="upload-panel" :class="{ analyzing: uploading }">
            <label class="upload-dropzone" :class="{ disabled: uploading }">
                <span class="upload-icon">
                    <i class="pi pi-cloud-upload"></i>
                </span>
                <span class="upload-copy">
                    <strong>Subir imagen para analisis</strong>
                    <small>El archivo se valida, se limpia EXIF y se analiza por esteganografia antes de publicarse.</small>
                </span>
                <span class="upload-cta">
                    <i class="pi pi-plus"></i>
                    Seleccionar imagen
                </span>
                <span class="upload-formats">PNG, JPG, WEBP o GIF</span>
                <input
                    type="file"
                    accept="image/png,image/jpeg,image/webp,image/gif"
                    :disabled="uploading"
                    @change="$emit('upload', $event)"
                />
            </label>

            <div v-if="uploading" class="analysis-panel">
                <h3>Revision de seguridad</h3>
                <ol class="analysis-steps">
                    <li v-for="step in analysisSteps" :key="step.key" :class="stepState(step.key)">
                        <i :class="stepIcon(step.key)"></i>
                        <span>{{ step.label }}</span>
                    </li>
                </ol>
            </div>
        </div>

        <p v-else class="empty-state">Este album todavia no esta aprobado. Un supervisor debe aprobarlo antes de subir imagenes.</p>

        <div v-if="images.length" class="images-section">
            <div class="images-section-head">
                <h3>Imagenes aprobadas</h3>
                <span>{{ images.length }} archivo{{ images.length === 1 ? "" : "s" }}</span>
            </div>
            <div class="image-grid">
                <figure v-for="image in images" :key="image.id" class="image-card">
                    <img :src="image.file_path" :alt="album.title" @click="openImage(image)">
                    <button class="delete-image-action" type="button" @click="$emit('delete-image', image)">
                        <i class="pi pi-trash"></i>
                        Eliminar
                    </button>
                    <figcaption :class="image.status">
                        <i class="pi pi-check-circle"></i>
                        {{ image.status === "approved" ? "Aprobada" : "En revision" }}
                    </figcaption>
                </figure>
            </div>
        </div>
        <p v-else-if="album.status === 'approved'" class="empty-state">Aun no hay imagenes aprobadas para este album.</p>

        <div v-if="previewImage" class="image-preview-backdrop" @click.self="closeImage">
            <section class="image-preview" role="dialog" aria-modal="true" aria-label="Imagen completa">
                <button class="close-preview" type="button" aria-label="Cerrar imagen" @click="closeImage">
                    <i class="pi pi-times"></i>
                </button>
                <img :src="previewImage.file_path" :alt="album.title">
            </section>
        </div>
    </section>
</template>

<script setup>
import { ref } from "vue";

const props = defineProps({
    album: {
        type: Object,
        required: true,
    },
    images: {
        type: Array,
        required: true,
    },
    apiUrl: {
        type: String,
        required: true,
    },
    uploading: {
        type: Boolean,
        default: false,
    },
    activeAnalysisStep: {
        type: String,
        default: "",
    },
    analysisSteps: {
        type: Array,
        required: true,
    },
});

defineEmits(["back", "upload", "delete-image"]);
const previewImage = ref(null);

function openImage(image) {
    previewImage.value = image;
}

function closeImage() {
    previewImage.value = null;
}

function stepState(key) {
    const currentIndex = props.analysisSteps.findIndex((step) => step.key === props.activeAnalysisStep);
    const stepIndex = props.analysisSteps.findIndex((step) => step.key === key);
    if (stepIndex < currentIndex) return "done";
    if (stepIndex === currentIndex && props.uploading) return "active";
    return "";
}

function stepIcon(key) {
    const state = stepState(key);
    if (state === "done") return "pi pi-check-circle";
    if (state === "active") return "pi pi-spin pi-spinner";
    return "pi pi-circle";
}
</script>

<style scoped>
.workspace-panel {
  width: 100%;
  padding: 28px;
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

.secondary-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 40px;
  padding: 10px 16px;
  border: 0;
  border-radius: 6px;
  background: #eef2ff;
  color: #091350;
  font-weight: 700;
  cursor: pointer;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 3px 9px;
  border-radius: 999px;
  background: #fff4e5;
  color: #b54708;
  font-size: 0.8rem;
  font-weight: 800;
}

.status-pill.approved {
  background: #e7f6ec;
  color: #157347;
}

.status-pill.rejected {
  background: #fdecec;
  color: #c1272d;
}

.upload-panel {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(340px, 0.75fr);
  gap: 20px;
  align-items: stretch;
  width: 100%;
  margin-bottom: 26px;
}

.upload-dropzone {
  position: relative;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 18px;
  min-height: 220px;
  padding: 28px;
  border: 1px dashed #6b78b8;
  border-radius: 8px;
  background: linear-gradient(135deg, #f8faff 0%, #ffffff 55%, #fff7f7 100%);
  color: #475467;
  cursor: pointer;
  overflow: hidden;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.upload-dropzone:only-child {
  grid-column: 1 / -1;
}

.upload-dropzone:hover {
  border-color: #091350;
  box-shadow: 0 16px 36px rgba(9, 19, 80, 0.12);
  transform: translateY(-1px);
}

.upload-dropzone.disabled {
  cursor: wait;
  opacity: 0.76;
}

.upload-icon {
  display: grid;
  place-items: center;
  width: 76px;
  height: 76px;
  border-radius: 8px;
  background: #eef2ff;
}

.upload-icon i {
  color: #091350;
  font-size: 2.2rem;
}

.upload-copy {
  display: grid;
  gap: 8px;
}

.upload-copy strong {
  color: #101828;
  font-size: 1.28rem;
}

.upload-copy small {
  max-width: 620px;
  color: #667085;
  font-size: 0.98rem;
  line-height: 1.45;
}

.upload-cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 42px;
  padding: 10px 16px;
  border-radius: 6px;
  background: #091350;
  color: #fff;
  font-weight: 800;
  white-space: nowrap;
}

.upload-formats {
  position: absolute;
  right: 28px;
  bottom: 20px;
  color: #667085;
  font-size: 0.86rem;
  font-weight: 700;
}

.upload-dropzone input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.analysis-panel {
  padding: 20px;
  border: 1px solid #e4e7ec;
  border-radius: 8px;
  background: #fcfcfd;
}

.analysis-panel h3 {
  margin: 0 0 14px;
  font-size: 1rem;
}

.analysis-steps {
  display: grid;
  gap: 12px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.analysis-steps li {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #667085;
}

.analysis-steps li.done {
  color: #157347;
}

.analysis-steps li.active {
  color: #091350;
  font-weight: 800;
}

.analysis-result {
  margin: 16px 0 0;
  padding: 12px;
  border-radius: 6px;
  background: #eef2ff;
  color: #091350;
  line-height: 1.45;
}

.analysis-result.approved {
  background: #e7f6ec;
  color: #157347;
}

.analysis-result.quarantined,
.analysis-result.rejected {
  background: #fff4e5;
  color: #b54708;
}

.images-section {
  padding-top: 18px;
  border-top: 1px solid #e4e7ec;
}

.images-section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
}

.images-section-head h3 {
  margin: 0;
  font-size: 1.05rem;
}

.images-section-head span {
  color: #667085;
  font-weight: 700;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.image-card {
  position: relative;
  margin: 0;
  overflow: hidden;
  border: 1px solid #e4e7ec;
  border-radius: 8px;
  background: #fff;
}

.image-card:hover .delete-image-action,
.delete-image-action:focus-visible {
  opacity: 1;
  transform: translateY(0);
}

.image-card img {
  display: block;
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  cursor: zoom-in;
}

.image-card figcaption {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  color: #157347;
  font-weight: 800;
  background: #f6fef9;
}

.delete-image-action {
  position: absolute;
  top: 10px;
  right: 10px;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  min-height: 34px;
  padding: 8px 10px;
  border: 0;
  border-radius: 6px;
  background: #d32626;
  color: #fff;
  font-weight: 800;
  cursor: pointer;
  opacity: 0;
  transform: translateY(-4px);
  transition: opacity 0.2s ease, transform 0.2s ease, filter 0.2s ease;
}

.delete-image-action:hover {
  filter: brightness(1.08);
}

.image-card figcaption.quarantined {
  color: #b54708;
  background: #fff4e5;
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

@media (max-width: 900px) {
  .upload-panel {
    grid-template-columns: 1fr;
  }

  .upload-dropzone {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .upload-icon {
    margin: 0 auto;
  }

  .upload-cta {
    width: fit-content;
    margin: 0 auto;
  }

  .upload-formats {
    position: static;
  }
}

@media (max-width: 760px) {
  .panel-title.split {
    display: grid;
  }
}
</style>
