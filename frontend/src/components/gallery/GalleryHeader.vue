<template>
    <section class="page-heading">
        <div>
            <p class="eyebrow">Galeria segura</p>
            <h1>Mis albumes</h1>
            <p class="heading-copy">Solicita albumes, espera aprobacion y sube imagenes para revision automatica.</p>
        </div>
        <div class="heading-actions">
            <div class="notification-wrap">
                <button class="notification-action" type="button" @click="$emit('toggle-notifications')">
                    <i class="pi pi-bell"></i>
                    Notificaciones
                    <span v-if="unreadCount">{{ unreadCount }}</span>
                </button>
                <NotificationPanel
                    :visible="notificationsOpen"
                    :notifications="notifications"
                />
            </div>
            <button class="primary-action" type="button" :disabled="loading" @click="$emit('refresh')">
                <i class="pi pi-refresh"></i>
                Actualizar
            </button>
        </div>
    </section>
</template>

<script setup>
import NotificationPanel from "@/components/general/NotificationPanel.vue";

defineProps({
    loading: {
        type: Boolean,
        default: false,
    },
    unreadCount: {
        type: Number,
        default: 0,
    },
    notificationsOpen: {
        type: Boolean,
        default: false,
    },
    notifications: {
        type: Array,
        default: () => [],
    },
});

defineEmits(["refresh", "toggle-notifications"]);
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

.heading-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.notification-wrap {
  position: relative;
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

.notification-action {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 40px;
  padding: 10px 16px;
  border: 1px solid #d0d5dd;
  border-radius: 6px;
  background: #fff;
  color: #091350;
  font-weight: 800;
  cursor: pointer;
}

.notification-action span {
  display: grid;
  place-items: center;
  min-width: 22px;
  height: 22px;
  padding: 0 6px;
  border-radius: 999px;
  background: #d32626;
  color: #fff;
  font-size: 0.78rem;
}

.primary-action:disabled {
  opacity: 0.65;
  cursor: wait;
}

@media (max-width: 760px) {
  .page-heading {
    display: grid;
  }

  .heading-actions {
    flex-wrap: wrap;
  }
}
</style>
