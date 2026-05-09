import { createRouter, createWebHistory } from 'vue-router';

// Lazy load pages
const LoginPage = () => import('@/pages/LoginPage.vue');
const HomePage = () => import('@/pages/HomePage.vue');
const GalleryPage = () => import('@/pages/GalleryPage.vue');
const SupervisorPage = () => import('@/pages/SupervisorPage.vue');
const PublicGalleryPage = () => import('@/pages/PublicGalleryPage.vue');

const routes = [
    //rutas
    {
      path: "/",
      redirect: "/public"
    },
    {
        path: '/login', 
        name: 'login',
        component: LoginPage,
        meta: { requiresAuth: false }
    },
    {
        path: '/public',
        name: 'public-gallery',
        component: PublicGalleryPage,
        meta: { requiresAuth: false }
    },
    {
        path: '/home',
        name: 'home',
        component: HomePage,
        redirect: () => {
            const role = getStoredUserRole();
            return role === 'supervisor' ? '/home/supervisor' : '/home/galeria';
        },
        meta: { requiresAuth: true },
        children: [
            {
                path: 'galeria',
                name: 'galeria',
                component: GalleryPage,
                meta: { requiresAuth: true, blockedRoles: ['supervisor'] }
            },
            {
                path: 'supervisor',
                name: 'supervisor',
                component: SupervisorPage,
                meta: { requiresAuth: true, allowedRoles: ['supervisor', 'admin'] }
            }
        ]
    },
    {
        path: '/:pathMatch(.*)*',
        name: 'notfound',
        redirect: '/public'
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

function getStoredUserRole() {
    const user = localStorage.getItem('user');

    try {
        const userData = user ? JSON.parse(user) : null;
        return typeof userData === 'object' && userData ? userData.role : null;
    } catch (e) {
        return null;
    }
}

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
        if (to.meta.blockedRoles) {
            const role = typeof userData === 'object' && userData ? userData.role : null;
            if (to.meta.blockedRoles.includes(role)) {
                next('/home/supervisor');
                return;
            }
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
