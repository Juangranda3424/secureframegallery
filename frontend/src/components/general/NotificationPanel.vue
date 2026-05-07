<template>
    <section v-if="visible" class="notification-panel">
        <div class="notification-head">
            <h2>Notificaciones</h2>
            <span>{{ notifications.length }}</span>
        </div>

        <div v-if="notifications.length" class="notification-list">
            <article
                v-for="notification in notifications"
                :key="notification.id"
                class="notification-item"
                :class="[notification.type, { unread: !notification.read }]"
            >
                <i :class="iconFor(notification.type)"></i>
                <div>
                    <strong>{{ notification.title }}</strong>
                    <p>{{ notification.message }}</p>
                </div>
            </article>
        </div>

        <p v-else class="empty-state">No tienes notificaciones todavia.</p>
    </section>
</template>

<script setup>
defineProps({
    visible: {
        type: Boolean,
        default: false,
    },
    notifications: {
        type: Array,
        default: () => [],
    },
});

function iconFor(type) {
    if (type === "approved") return "pi pi-check-circle";
    if (type === "rejected") return "pi pi-times-circle";
    return "pi pi-info-circle";
}
</script>

<style scoped>
.notification-panel {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  z-index: 50;
  width: min(420px, calc(100vw - 36px));
  max-height: 460px;
  overflow: auto;
  padding: 18px;
  border: 1px solid #e4e7ec;
  border-radius: 8px;
  background: #fff;
  box-shadow: 0 18px 46px rgba(16, 24, 40, 0.18);
  animation: panel-in 0.18s ease;
}

.notification-panel::before {
  content: "";
  position: absolute;
  top: -7px;
  right: 28px;
  width: 14px;
  height: 14px;
  border-left: 1px solid #e4e7ec;
  border-top: 1px solid #e4e7ec;
  background: #fff;
  transform: rotate(45deg);
}

.notification-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.notification-head h2 {
  margin: 0;
  font-size: 1.08rem;
}

.notification-head span {
  color: #667085;
  font-weight: 800;
}

.notification-list {
  display: grid;
  gap: 10px;
}

.notification-item {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 12px;
  padding: 12px;
  border: 1px solid #e4e7ec;
  border-radius: 8px;
  background: #fcfcfd;
}

.notification-item.unread {
  border-color: #b8c0ea;
  background: #f8faff;
}

.notification-item i {
  margin-top: 2px;
  color: #091350;
}

.notification-item.approved i {
  color: #157347;
}

.notification-item.rejected i {
  color: #d32626;
}

.notification-item strong {
  color: #101828;
}

.notification-item p {
  margin: 4px 0 0;
  color: #667085;
  line-height: 1.45;
}

.empty-state {
  margin: 0;
  padding: 14px;
  border: 1px dashed #d0d5dd;
  border-radius: 8px;
  background: #f9fafb;
  color: #667085;
}

@keyframes panel-in {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
