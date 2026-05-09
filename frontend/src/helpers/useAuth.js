import { ref, computed } from 'vue';
import authService from '@/services/authService.js';
import router from '@/router/router.js';

const user = ref(null);
const loading = ref(false);
const error = ref(null);


export function useAuth() {

    /**
     * Login de usuario
     */
    async function login(email, password) {
        loading.value = true;
        error.value = null;
        try {
            const { data } = await authService.login({ email, password });
            
            // Guardar tokens
            authService.setTokens(data.session.access_token, data.session.refresh_token);
            
            // Guardar datos del usuario
            user.value = data.user;
            localStorage.setItem('user', JSON.stringify(data.user));
            
            return data;
        } catch (err) {
            error.value = err.response?.data?.detail || err.response?.data?.message || 'Error en el login';
            throw error.value;
        } finally {
            loading.value = false;
        }
    }

    /**
     * Registro de usuario
     */
    async function register(name, email, password) {
        loading.value = true;
        error.value = null;
        try {
            const { data } = await authService.register({ name, email, password });
            return data;
        } catch (err) {
            error.value = err.response?.data?.detail || err.response?.data?.message || 'No se pudo completar el registro';
            throw error.value;
        } finally {
            loading.value = false;
        }
    }

    /**
     * Logout del usuario
     */
    async function logout() {

        loading.value = true;
        error.value = null;
        authService.clearTokens();
        user.value = null;
        loading.value = false;
        router.push('/login');
        
    }

    /**
     * Cargar usuario desde localStorage al iniciar la app
     */
    function loadUserFromStorage() {
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            user.value = JSON.parse(storedUser);
        }
    }

    /**
     * Computed: verificar si está autenticado
     */
    const isAuthenticated = computed(() => authService.isAuthenticated());

    return {
        // Estado
        user,
        loading,
        error,
        
        // Métodos
        login,
        register,
        logout,
        loadUserFromStorage,
        
        // Computados
        isAuthenticated
    };
}
