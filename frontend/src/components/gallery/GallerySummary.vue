<template>
    <section class="summary-grid">
        <article class="summary-item">
            <span>{{ total }}</span>
            <p>Total</p>
        </article>
        <article class="summary-item success">
            <span>{{ approved }}</span>
            <p>Aprobados</p>
        </article>
        <article class="summary-item warning">
            <span>{{ pending }}</span>
            <p>Pendientes</p>
        </article>
    </section>
</template>

<script setup>
defineProps({
    total: {
        type: Number,
        required: true,
    },
    approved: {
        type: Number,
        required: true,
    },
    pending: {
        type: Number,
        required: true,
    },
});
</script>

<style scoped>
.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  width: 100%;
  margin-bottom: 22px;
}

.summary-item {
  padding: 16px;
  border: 1px solid #e4e7ec;
  border-radius: 8px;
  background: #fff;
}

.summary-item span {
  display: block;
  color: #091350;
  font-size: 1.7rem;
  font-weight: 800;
}

.summary-item p {
  margin: 4px 0 0;
  color: #667085;
}

.summary-item.success span {
  color: #157347;
}

.summary-item.warning span {
  color: #b54708;
}

@media (max-width: 760px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
