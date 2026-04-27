<template>
    <ConfirmDialog></ConfirmDialog>
    <div class="header-promotion">
        <div class="container_buttons-social-media">
            <div class="button_mode">
                <img :src="LogoDark" alt="Logo" style="width: 100px; padding: 10%; border-radius: 20%;" />
            </div>
        </div>
        <div class="button_dark_mode">
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
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 1rem;
}

.header-promotion {
    display: flex;
    justify-content: space-between;
    width: 100%;
    border-bottom: solid 1px rgba(0, 0, 0, 0.374);

}

.button_mode {
    display: flexbox;
    justify-content: center;
    align-items: center;
    margin-left: 0.5rem;
}

.button_dark_mode {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-right: 0.5rem;
    gap: 0.5rem;
    padding: 1rem;
}

.text-promotion {
    color: white;
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
    margin: 0%;
    padding: 0%;
    gap: 0.5rem;
    margin-top: 0.2rem;
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