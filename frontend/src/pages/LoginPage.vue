<template>
  <div class="login-page">
    <router-link class="public-link" to="/public">
      <i class="pi pi-images"></i>
      Galeria publica
    </router-link>

    <div class="cloud-path"></div>

    <div class="login-wrapper">
      <FormLogin />
    </div>
  </div>
</template>

<script setup>
import FormLogin from '@/components/form/FormLogin.vue';
</script>

<style scoped>
.login-page {
  position: relative;
  overflow: hidden;
  display: flex;
  width: 100%;
  min-height: 100vh;
  margin: 0;
  padding: 0;
  background: #091350; /* Tu azul oscuro */
}

.public-link {
  position: absolute;
  top: 22px;
  right: 24px;
  z-index: 20;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 40px;
  padding: 10px 16px;
  border-radius: 6px;
  background: #fff;
  color: #091350;
  font-weight: 800;
  text-decoration: none;
  box-shadow: 0 12px 26px rgba(16, 24, 40, 0.18);
}

/* La forma de nube nítida y orgánica usando clip-path */
.cloud-path {
  position: absolute;
  bottom: -20px; /* Ajuste para esconder el borde inferior */
  left: 0;
  width: 100%;
  height: 250px; /* Altura de la masa blanca */
  background: white; /* Color sólido y nítido */
  
  /* --- ESTO ES LA MAGIA: Define el contorno orgánico --- */
  /* Recrea la forma de tu imagen de referencia */
  clip-path: ellipse(65% 120% at 50% 120%); 
}

.login-wrapper {
  z-index: 10; /* Asegura que el formulario esté por encima */
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

</style>
