import apiClient from './api.js';

export const authService = {    

    /**
     * Login de usuario
     */
    login(credentials) {
        return apiClient.post('/auth/login', credentials);
    },

    /**
     * Refrescar access token
     */
    refreshToken(token) {
        return apiClient.post('/auth/refresh-token', { token });
    },

    /**
     * Logout del usuario
     */
    logout() {
        return apiClient.post('/auth/logout');
    },

    /**
     * Guardar tokens en localStorage
     */
    setTokens(accessToken, refreshToken) {
        localStorage.setItem('accessToken', accessToken);
        localStorage.setItem('refreshToken', refreshToken);
    },

    /**
     * Obtener el access token
     */
    getAccessToken() {
        return localStorage.getItem('accessToken');
    },

    /**
     * Obtener el refresh token
     */
    getRefreshToken() {
        return localStorage.getItem('refreshToken');
    },

    /**
     * Limpiar tokens
     */
    clearTokens() {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
    },

    /**
     * Verificar si existe token
     */
    isAuthenticated() {
        return !!localStorage.getItem('accessToken');
    }
};

export default authService;
