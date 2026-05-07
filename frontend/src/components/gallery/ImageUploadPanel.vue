<template>
    <section class="workspace-panel images-panel">
        <div class="panel-title split">
            <div>
                <h2>{{ album.title }}</h2>
                <p>Estado del album: <span class="status-pill" :class="album.status">{{ album.status }}</span></p>
            </div>
            <button class="secondary-action" type="button" @click="$emit('back')">
                <i class="pi pi-arrow-left"></i>
                Ver albumes
            </button>
        </div>

        <div v-if="album.status === 'approved'" class="upload-panel">
            <label class="upload-dropzone">
                <i class="pi pi-cloud-upload"></i>
                <strong>Subir imagen para analisis</strong>
                <span>PNG, JPG, WEBP o GIF. Se limpiara EXIF y se revisara esteganografia.</span>
                <input
                    type="file"
                    accept="image/png,image/jpeg,image/webp,image/gif"
                    :disabled="uploading"
                    @change="$emit('upload', $event)"
                />
            </label>

            <div v-if="uploading || uploadResult" class="analysis-panel">
                <h3>Revision de seguridad</h3>
                <ol class="analysis-steps">
                    <li v-for="step in analysisSteps" :key="step.key" :class="stepState(step.key)">
                        <i :class="stepIcon(step.key)"></i>
                        <span>{{ step.label }}</span>
                    </li>
                </ol>
                <p v-if="uploadResult" class="analysis-result" :class="uploadResult.status">
                    {{ uploadResult.message }}
                </p>
            </div>
        </div>

        <p v-else class="empty-state">Este album todavia no esta aprobado. Un supervisor debe aprobarlo antes de subir imagenes.</p>

        <div v-if="images.length" class="image-grid">
            <img
                v-for="image in images"
                :key="image.id"
                :src="apiUrl + image.file_path"
                :alt="album.title"
            >
        </div>
        <p v-else-if="album.status === 'approved'" class="empty-state">Aun no hay imagenes aprobadas para este album.</p>
    </section>
</template>

<script setup>
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
    uploadResult: {
        type: Object,
        default: null,
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

defineEmits(["back", "upload"]);

function stepState(key) {
    const currentIndex = props.analysisSteps.findIndex((step) => step.key === props.activeAnalysisStep);
    const stepIndex = props.analysisSteps.findIndex((step) => step.key === key);
    if (props.uploadResult && stepIndex <= currentIndex) return "done";
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
  padding: 24px;
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
  grid-template-columns: minmax(0, 1.2fr) minmax(300px, 0.8fr);
  gap: 18px;
  align-items: stretch;
  margin-bottom: 22px;
}

.upload-dropzone {
  display: grid;
  place-items: center;
  gap: 10px;
  min-height: 220px;
  padding: 24px;
  border: 1px dashed #98a2b3;
  border-radius: 8px;
  background: #f9fafb;
  color: #475467;
  text-align: center;
  cursor: pointer;
}

.upload-dropzone > i {
  color: #091350;
  font-size: 2rem;
}

.upload-dropzone strong {
  color: #101828;
  font-size: 1.1rem;
}

.upload-dropzone span {
  max-width: 420px;
  line-height: 1.45;
}

.upload-dropzone input {
  max-width: 280px;
}

.analysis-panel {
  padding: 18px;
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

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

.image-grid img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #e4e7ec;
}

.empty-state {
  margin: 0;
  padding: 18px;
  border: 1px dashed #d0d5dd;
  border-radius: 8px;
  background: #f9fafb;
  color: #667085;
}

@media (max-width: 900px) {
  .upload-panel {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .panel-title.split {
    display: grid;
  }
}
</style>
