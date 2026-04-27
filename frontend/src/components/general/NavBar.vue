<template>
    <div>
        <Menubar    
            :model="items"
            style="font-size: 1.1rem; background-color: #f6f6f6;" 
            >
            <template #start>
                <div style="padding: 20% 0% 20% 0%; display: flex; align-items: center; gap: 0.5rem;">
                    <Button icon="pi pi-user" severity="contrast" variant="text" rounded aria-label="User" />
                    <span style="color: #000; font-weight: 500; margin-right: 10%;">{{ userName }}</span>
                </div>
            </template>
            <template #separator> 
                |
            </template>
        </Menubar>
    </div>
</template>

<script setup>
import Menubar from 'primevue/menubar';
import router from '@/router/router';
import Button from 'primevue/button';
import { ref, onMounted, computed } from "vue";
import { useRoute } from 'vue-router';
const route = useRoute();
const userName = ref('');
const isDark = ref(false);

// Detectar cuando PrimeVue cambia a modo oscuro
const checkDarkMode = () => {
    isDark.value = document.documentElement.classList.contains("my-app-dark");
};

onMounted(() => {
    checkDarkMode();

    const storedUser = localStorage.getItem('user');
    if (storedUser) {
        // Quitar comillas dobles si existen
        userName.value = storedUser.replace(/^"|"$/g, '').toUpperCase();
    }

    // Observar cambios en la clase del <html>
    const observer = new MutationObserver(checkDarkMode);

    observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ["class"]
    });

});

const items = computed(() => {
    const baseItems = [
        { 
            label: 'Galería', 
            icon: 'pi pi-chart-bar', 
            command: () => router.push('/home/galeria'),
            class: route.path.includes('galeria') ? 'active-item' : ''
        },
    ];
    return baseItems
});

</script>

<style scoped>


:deep(.p-menubar-item-icon) {
    color: rgb(0, 0, 0) !important;
}

:deep(.p-menubar-item-label) {
    color: rgb(0, 0, 0) !important;
}

/* Hover */
:deep(.p-menubar-item-content:hover .p-menubar-item-label),
:deep(.p-menubar-item-content:hover .p-menubar-item-icon) {
    color: #ffffff !important;
}

:deep(.p-menubar-item-content:hover) {
    background-color: #DB2626 !important;
    border-radius: 8px;
}

/* Focus */
:deep(.p-menubar-item.p-focus > .p-menubar-item-content) {
    background-color: #DB2626 !important;
    border-radius: 8px;
}

:deep(.p-menubar-item.p-focus > .p-menubar-item-content .p-menubar-item-label),
:deep(.p-menubar-item.p-focus > .p-menubar-item-content .p-menubar-item-icon) {
    color: rgb(255, 255, 255) !important;
}

/* Item activo */
:deep(.active-item > .p-menubar-item-content) {
    background-color:  #091350 !important;
    border-radius: 8px;
}

:deep(.active-item > .p-menubar-item-content .p-menubar-item-label),
:deep(.active-item > .p-menubar-item-content .p-menubar-item-icon) {
    color: rgb(255, 255, 255) !important;
}


:deep(.p-menubar-mobile-active .p-menubar-root-list) {
    background-color: rgb(251, 251, 251) !important;
    border: none !important;
}

/* Botón hamburguesa */
:deep(.p-menubar-button) {
    color: rgb(0, 0, 0) !important;
}

:deep(.p-menubar-button:hover) {
    color: black !important;
}

</style>