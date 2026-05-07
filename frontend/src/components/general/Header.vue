<template>
    <ConfirmDialog></ConfirmDialog>
    <div class="app-header">
        <div class="brand">
            <img :src="LogoDark" alt="Logo SecureFrame Gallery" />
            <div>
                <strong>SecureFrame Gallery</strong>
                <span>Revision segura de imagenes</span>
            </div>
        </div>
        <div class="header-actions">
            <Button icon="pi pi-sign-out" severity="danger" label="Cerrar Sesión" size="large" @click="handleLogout"
                :title="'Cerrar sesión'" />
        </div>
    </div>
    <NavBar />
    <div v-if="isLoading" class="loading-overlay">
        <ProgressSpinner 
            style="width: 40%; height: 40%;" 
            strokeWidth="8" 
            fill="transparent"
            animationDuration=".5s" 
            aria-label="Custom ProgressSpinner" 
        />
    </div>
</template>

<script setup>

import LogoDark from '@/assets/hero.png';
import NavBar from '@/components/general/NavBar.vue';
import Button from 'primevue/button';
import ProgressSpinner from 'primevue/progressspinner';
import ConfirmDialog from 'primevue/confirmdialog';
import { useAuth } from '@/helpers/useAuth.js';
import { useConfirm } from "primevue/useconfirm";
import { ref } from 'vue';


const { logout } = useAuth();
const confirm = useConfirm();
const isLoading = ref(false);

const handleLogout = () => {
    confirm.require({
        message: "¿Seguro que desea cerrar sesión?",
        header: 'Cerrar Sesión',
        icon: 'pi pi-exclamation-circle',
        acceptProps: { label: 'Cerrar sesión', severity: 'danger' },
        rejectProps: { label: 'Cancelar', severity: 'secondary', outlined: true },
        accept: async () => {
            isLoading.value = true;
            await new Promise(resolve => setTimeout(resolve, 2000));
            logout();
            isLoading.value = false;
        }
    });
};

</script>

<style scoped>
.app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    padding: 18px 24px;
    border-bottom: 1px solid #e4e7ec;
    background: #fff;
}

.brand {
    display: flex;
    align-items: center;
    gap: 14px;
}

.brand img {
    width: 76px;
    height: 76px;
    object-fit: cover;
    border-radius: 8px;
}

.brand strong,
.brand span {
    display: block;
}

.brand strong {
    color: #091350;
    font-size: 1.1rem;
}

.brand span {
    margin-top: 2px;
    color: #667085;
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
}
</style>
