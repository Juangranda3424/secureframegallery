import { createApp } from 'vue';
import App from './App.vue';
import PrimeVue from 'primevue/config';
import Aura from '@primeuix/themes/aura';
import router from '@/router/router.js';
import 'primeicons/primeicons.css'
import ConfirmationService from 'primevue/confirmationservice';
import ToastService from 'primevue/toastservice';
import '@/css/general.css'
import Tooltip from 'primevue/tooltip';
import AnimateOnScroll from 'primevue/animateonscroll';

createApp(App)
.use(router)
.use(PrimeVue, {
    theme: {
        preset: Aura,
        options: {
            darkModeSelector: '.my-app-dark',
        }
    }
})
.use(ConfirmationService)
.use(ToastService)
.directive('tooltip', Tooltip)
.directive('animateonscroll', AnimateOnScroll)
.mount('#app')