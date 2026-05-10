<template>
    <main class="supervisor-page">
        <section class="page-heading">
            <div>
                <p class="eyebrow">Panel de revision</p>
                <h1>Supervisor</h1>
                <p>Aprueba albumes y revisa imagenes retenidas por el analisis de seguridad.</p>
            </div>
        </section>

        <section class="review-panel">
            <div class="panel-title">
                <h2>Albumes pendientes</h2>
                <span>{{ pendingAlbums.length }} en revision</span>
            </div>

            <div v-if="pendingAlbums.length" class="review-grid">
                <article v-for="album in pendingAlbums" :key="album.id" class="review-card">
                    <h3>{{ album.title }}</h3>
                    <p>{{ album.description || "Sin descripcion" }}</p>
                    <div class="review-actions">
                        <button class="approve" :disabled="isBusy" @click="approveAlbum(album.id)">
                            <i :class="actionKey === `album-approve-${album.id}` ? 'pi pi-spin pi-spinner' : 'pi pi-check'"></i>
                            {{ actionKey === `album-approve-${album.id}` ? "Aprobando" : "Aprobar" }}
                        </button>
                        <button class="reject" :disabled="isBusy" @click="rejectAlbum(album.id)">
                            <i :class="actionKey === `album-reject-${album.id}` ? 'pi pi-spin pi-spinner' : 'pi pi-times'"></i>
                            {{ actionKey === `album-reject-${album.id}` ? "Rechazando" : "Rechazar" }}
                        </button>
                    </div>
                </article>
            </div>
            <p v-else class="empty-state">No hay albumes pendientes.</p>
        </section>

        <section class="review-panel">
            <div class="panel-title">
                <h2>Imagenes en cuarentena</h2>
                <span>{{ quarantineImages.length }} retenidas</span>
            </div>

            <div v-if="quarantineImages.length" class="review-grid image-review-grid">
                <article v-for="image in quarantineImages" :key="image.id" class="review-card">
                    <img
                        :src="image.file_path"
                        alt="Imagen en cuarentena"
                        class="quarantine-image"
                        @click="openImage(image)"
                    >
                    <div class="quarantine-meta">
                        <span>Album</span>
                        <strong>{{ image.album_title || image.album?.title || "Album no encontrado" }}</strong>
                    </div>
                    <details class="analysis-details">
                        <summary>Ver analisis</summary>
                        <pre>{{ formatAnalysis(image.image_analysis) }}</pre>
                    </details>
                    <div class="review-actions">
                        <button class="approve" :disabled="isBusy" @click="approveImage(image.id)">
                            <i :class="actionKey === `image-approve-${image.id}` ? 'pi pi-spin pi-spinner' : 'pi pi-check'"></i>
                            {{ actionKey === `image-approve-${image.id}` ? "Aprobando" : "Aprobar" }}
                        </button>
                        <button class="reject" :disabled="isBusy" @click="rejectImage(image.id)">
                            <i :class="actionKey === `image-reject-${image.id}` ? 'pi pi-spin pi-spinner' : 'pi pi-trash'"></i>
                            {{ actionKey === `image-reject-${image.id}` ? "Rechazando" : "Rechazar" }}
                        </button>
                    </div>
                </article>
            </div>
            <p v-else class="empty-state">No hay imagenes en cuarentena.</p>
        </section>

        <div v-if="previewImage" class="image-preview-backdrop" @click.self="closeImage">
            <section class="image-preview" role="dialog" aria-modal="true" aria-label="Imagen en cuarentena completa">
                <button class="close-preview" type="button" aria-label="Cerrar imagen" @click="closeImage">
                    <i class="pi pi-times"></i>
                </button>
                <img :src="previewImage.file_path" alt="Imagen en cuarentena completa">
            </section>
        </div>
    </main>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import albumService from "@/services/albumService.js";
import imageService from "@/services/imageService.js";
import { useToastGlobal } from "@/helpers/utils.js";

const { msjShow } = useToastGlobal();

const apiUrl = import.meta.env.VITE_API_URL.replace("/api/v1","");
const pendingAlbums = ref([]);
const quarantineImages = ref([]);
const actionKey = ref("");
const previewImage = ref(null);

const isBusy = computed(() => !!actionKey.value);

async function loadData() {
    const albumsResp = await albumService.getPending();
    pendingAlbums.value = albumsResp.data;

    const quarantineResp = await imageService.listQuarantine();
    quarantineImages.value = quarantineResp.data;
}

async function approveAlbum(albumId) {
    await runReviewAction(`album-approve-${albumId}`, async () => {
        await albumService.approve(albumId);
        msjShow("success", "Album aprobado", "El album ha sido aprobado correctamente.", 3500);
    });
}

async function rejectAlbum(albumId) {
    await runReviewAction(`album-reject-${albumId}`, async () => {
        await albumService.reject(albumId);
        msjShow("warn", "Album rechazado", "El album ha sido rechazado.", 3500);
    });
}

async function approveImage(imageId) {
    await runReviewAction(`image-approve-${imageId}`, async () => {
        await imageService.approve(imageId);
        msjShow("success", "Imagen aprobada", "La imagen ha sido aprobada y ya es visible en la galeria.", 3500);
    });
}

async function rejectImage(imageId) {
    await runReviewAction(`image-reject-${imageId}`, async () => {
        await imageService.rejectQuarantine(imageId);
        msjShow("warn", "Imagen rechazada", "La imagen ha sido eliminada del sistema.", 3500);
    });
    closeImage();
}

async function runReviewAction(key, action) {
    actionKey.value = key;
    try {
        await action();
        await loadData();
    } catch {
        msjShow("error", "Error", "No se pudo completar la accion. Intenta de nuevo.", 4000);
    } finally {
        actionKey.value = "";
    }
}

function formatAnalysis(analysis) {
    if (!analysis?.length) {
        return "No hay registro de analisis para esta imagen.";
    }

    return analysis.map((item) => {
        let parsed;
        try {
            parsed = typeof item.result === "string" ? JSON.parse(item.result) : item.result;
        } catch {
            return item.result || JSON.stringify(item, null, 2);
        }

        const tipo = item.analysis_type?.toUpperCase() ?? "DESCONOCIDO";
        const confianza = parsed.confidence != null
            ? `${(parsed.confidence * 100).toFixed(1)}%`
            : "N/A";
        const motivos = parsed.reasons?.length
            ? parsed.reasons.map((r) => `  • ${r}`).join("\n")
            : "  • Sin motivos registrados";
        const detalles = parsed.details
            ? [
                `  LSB balance score : ${parsed.details.lsb_balance_score?.toFixed(4) ?? "N/A"}`,
                `  Entropia          : ${parsed.details.entropy?.toFixed(4) ?? "N/A"} bits`,
                `  EOF sospechoso    : ${parsed.details.eof_suspicious ? "SI" : "NO"}`,
              ].join("\n")
            : "  Sin detalles";

        return [
            `Tipo de deteccion : ${tipo}`,
            `Nivel de confianza: ${confianza}`,
            `Motivos de alerta :`,
            motivos,
            `Detalles tecnicos :`,
            detalles,
        ].join("\n");
    }).join("\n\n---\n\n");
}

function openImage(image) {
    previewImage.value = image;
}

function closeImage() {
    previewImage.value = null;
}

onMounted(loadData);
</script>

<style scoped>
.supervisor-page {
  min-height: calc(100vh - 210px);
  padding: 32px;
  background: #f7f8fb;
  color: #101828;
}

.page-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  width: 100%;
  margin-bottom: 22px;
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
}

.page-heading p {
  margin: 8px 0 0;
  color: #667085;
}

.review-panel {
  width: 100%;
  margin-bottom: 20px;
  padding: 24px;
  border: 1px solid #e4e7ec;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 10px 30px rgba(16, 24, 40, 0.05);
}

.panel-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.panel-title h2 {
  margin: 0;
  font-size: 1.25rem;
}

.panel-title span {
  color: #667085;
  font-weight: 700;
}

.review-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(100%, 280px), 1fr));
  gap: 16px;
}

.review-card {
  min-width: 0;
  padding: 16px;
  border: 1px solid #e4e7ec;
  border-radius: 8px;
  background: #fff;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.review-card:hover {
  border-color: #b8c0ea;
  box-shadow: 0 12px 26px rgba(16, 24, 40, 0.08);
  transform: translateY(-1px);
}

.review-card h3 {
  margin: 0 0 8px;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.review-card p {
  margin: 0 0 16px;
  color: #667085;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.review-card img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #e4e7ec;
}

.quarantine-image {
  cursor: zoom-in;
}

.review-card pre {
  max-height: 140px;
  overflow: auto;
  padding: 10px;
  border-radius: 6px;
  background: #f9fafb;
  color: #344054;
  white-space: pre-wrap;
}

.quarantine-meta {
  display: grid;
  gap: 4px;
  margin: 12px 0;
  padding: 10px 12px;
  border-radius: 6px;
  background: #f8faff;
}

.quarantine-meta span {
  color: #667085;
  font-size: 0.78rem;
  font-weight: 800;
  text-transform: uppercase;
}

.quarantine-meta strong {
  color: #091350;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.analysis-details {
  margin-bottom: 12px;
}

.analysis-details summary {
  color: #091350;
  font-weight: 800;
  cursor: pointer;
}

.review-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(112px, 1fr));
  gap: 8px;
}

.review-actions button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  min-width: 0;
  min-height: 36px;
  padding: 8px 12px;
  border: 0;
  border-radius: 6px;
  color: #fff;
  font-weight: 800;
  line-height: 1.2;
  white-space: nowrap;
  cursor: pointer;
  transition: filter 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.review-actions button i {
  flex: 0 0 auto;
}

.review-actions button:hover {
  filter: brightness(1.06);
  box-shadow: 0 8px 18px rgba(16, 24, 40, 0.14);
  transform: translateY(-1px);
}

.review-actions button:disabled {
  opacity: 0.72;
  cursor: wait;
}

.review-actions button:disabled:hover {
  box-shadow: none;
  filter: none;
  transform: none;
}

.review-actions button:active {
  transform: translateY(0);
}

.approve {
  background: #157347;
}

.reject {
  background: #d32626;
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
</style>
