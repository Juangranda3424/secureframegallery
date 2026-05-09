<template>
    <div>
        <Menubar
            class="app-nav"
            :model="items"
            >
            <template #start>
                <div class="nav-user">
                    <Button icon="pi pi-user" severity="contrast" variant="text" rounded aria-label="User" />
                    <div>
                        <strong>{{ userName }}</strong>
                        <span>{{ userRole }}</span>
                    </div>
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
const userRole = ref('user');
const isDark = ref(false);

// Detectar cuando PrimeVue cambia a modo oscuro
const checkDarkMode = () => {
    isDark.value = document.documentElement.classList.contains("my-app-dark");
};

onMounted(() => {
    checkDarkMode();

    const storedUser = localStorage.getItem('user');
    if (storedUser) {
        const parsedUser = JSON.parse(storedUser);
        if (typeof parsedUser === 'string') {
            userName.value = parsedUser.toUpperCase();
        } else {
            userName.value = (parsedUser.name || parsedUser.email || '').toUpperCase();
            userRole.value = parsedUser.role || 'user';
        }
    }

    // Observar cambios en la clase del <html>
    const observer = new MutationObserver(checkDarkMode);

    observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ["class"]
    });

});

const items = computed(() => {
    const baseItems = [];

    if (userRole.value !== 'supervisor') {
        baseItems.push({
            label: 'Galería',
            icon: 'pi pi-chart-bar',
            command: () => router.push('/home/galeria'),
            class: route.path.includes('galeria') ? 'active-item' : ''
        });
    }

    if (['supervisor', 'admin'].includes(userRole.value)) {
        baseItems.push({
            label: 'Supervisor',
            icon: 'pi pi-shield',
            command: () => router.push('/home/supervisor'),
            class: route.path.includes('supervisor') ? 'active-item' : ''
        });
    }

    return baseItems
});

</script>

<style scoped>


:deep(.p-menubar-item-icon) {
    color: #344054 !important;
}

:deep(.p-menubar-item-label) {
    color: #344054 !important;
}

:deep(.app-nav) {
    padding: 14px 20px;
    border: 0;
    border-bottom: 1px solid #e4e7ec;
    border-radius: 0;
    background: #fff !important;
}

.nav-user {
    display: flex;
    align-items: center;
    gap: 10px;
    min-width: 190px;
    margin-right: 14px;
}

.nav-user strong,
.nav-user span {
    display: block;
}

.nav-user strong {
    color: #101828;
    font-weight: 800;
}

.nav-user span {
    color: #667085;
    font-size: 0.82rem;
    text-transform: capitalize;
}

/* Hover */
:deep(.p-menubar-item-content:hover .p-menubar-item-label),
:deep(.p-menubar-item-content:hover .p-menubar-item-icon) {
    color: #ffffff !important;
}

:deep(.p-menubar-item-content:hover) {
    background-color: #d32626 !important;
    border-radius: 8px;
}

/* Focus */
:deep(.p-menubar-item.p-focus > .p-menubar-item-content) {
    background-color: #d32626 !important;
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
