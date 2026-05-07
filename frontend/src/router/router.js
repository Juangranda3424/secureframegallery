import { createRouter, createWebHistory } from 'vue-router';

// Lazy load pages
const LoginPage = () => import('@/pages/LoginPage.vue');
const HomePage = () => import('@/pages/HomePage.vue');
const GalleryPage = () => import('@/pages/GalleryPage.vue');
const SupervisorPage = () => import('@/pages/SupervisorPage.vue');

const routes = [
    //rutas
    {
      path: "/",
      redirect: "/login"
    },
    {
        path: '/:pathMatch(.*)*',
        name: 'notfound',
        redirect: '/login'
    },
    {
        path: '/login', 
        name: 'login',
        component: LoginPage,
        meta: { requiresAuth: false }
    },
    {
        path: '/home',
        name: 'home',
        component: HomePage,
        redirect: '/home/galeria',
        meta: { requiresAuth: true },
        children: [
            {
                path: 'galeria',
                name: 'galeria',
                component: GalleryPage,
                meta: { requiresAuth: true }
            },
            {
                path: 'supervisor',
                name: 'supervisor',
                component: SupervisorPage,
                meta: { requiresAuth: true, allowedRoles: ['supervisor', 'admin'] }
            }
        ]
    }

];


const router = createRouter({
    history: createWebHistory(),
    routes,
    scrollBehavior(to, from, savedPosition) {
        if (to.hash) {
            return {
                el: to.hash,
                behavior: 'smooth'
            }
        }
        return { top: 0 }
    }
});

// Guard global para proteger rutas
router.beforeEach((to, from, next) => {
    // Verificar token en localStorage
    const accessToken = localStorage.getItem('accessToken');
    const user = localStorage.getItem('user');
    const isAuthenticated = !!accessToken;

    let userData = null;
    try {
        userData = user ? JSON.parse(user) : null;
    } catch (e) {
        userData = null;
    }

    // Si la ruta requiere autenticación
    if (to.meta.requiresAuth) {
        if (!isAuthenticated) {
            next('/login');
            return;
        }
        if (to.meta.allowedRoles) {
            const role = typeof userData === 'object' && userData ? userData.role : null;
            if (!to.meta.allowedRoles.includes(role)) {
                next('/home/galeria');
                return;
            }
        }
        next();
    }
    // Si la ruta es solo para usuarios no autenticados (login/register)
    else if (to.meta.requiresGuest) {
        if (isAuthenticated) {
            next('/home');
            return;
        }
        next();
    }
    else {
        next();
    }

});

export default router;
