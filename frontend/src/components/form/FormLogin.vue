<template>
    
    <Card :class="{ 'container-login': true, 'register': mode === 'register' }">
        <template #header>
            <div class="container-login-card">
                <!-- Imagen corregida: usa hero.png como placeholder -->
                <img alt="user header" src="@/assets/hero.png" class="img-logo" />
            </div>
        </template>
        <template #content>
            <div class="auth-mode">
                <button type="button" :class="{ active: mode === 'login' }" @click="setMode('login')">
                    Iniciar sesion
                </button>
                <button type="button" :class="{ active: mode === 'register' }" @click="setMode('register')">
                    Registrarse
                </button>
            </div>
            <div class="container-login-card">
                <IftaLabel v-if="mode === 'register'" class="login-div">
                    <IconField>
                        <InputIcon class="pi pi-user" />
                        <InputText id="nameuser" v-model="name" class="components-login" @keypress.enter="submitAuth()" :disabled="isLoading"/>
                    </IconField>
                    <label for="nameuser">Nombre</label>
                </IftaLabel>
                <IftaLabel class="login-div">
                    <IconField>
                        <InputIcon class="pi pi-envelope" />
                        <InputText id="emailuser" v-model="email" type="email" class="components-login" @keypress.enter="submitAuth()" :disabled="isLoading"/>
                    </IconField>
                    <label for="emailuser">Correo electrónico</label>
                </IftaLabel>
            </div>
            <div class="container-login-card">
                    <IftaLabel class="login-div">
                        <IconField>
                            <InputIcon class="pi pi-lock" />
                            <Password
                                id="password"
                                v-model="password"
                                toggleMask
                                :feedback="mode === 'register'"
                                class="components-login"
                                @keypress.enter="submitAuth()"
                                :disabled="isLoading"
                            />
                        </IconField>
                        <label for="password">Contraseña</label>
                    </IftaLabel>
  
                    <IftaLabel v-if="mode === 'register'"    class="login-div">
                        <IconField>
                            <InputIcon class="pi pi-lock" />
                            <Password
                                id="confirmPassword"
                                v-model="confirmPassword"
                                toggleMask
                                :feedback="mode === 'register'"
                                class="components-login"
                                @keypress.enter="submitAuth()"
                                :disabled="isLoading"
                            />
                        </IconField>
                        <label for="confirmPassword">Repita contraseña</label>
                    </IftaLabel>
            </div>
            <div v-if="mode === 'register' && password" class="password-rules">
                <span :class="{ ok: passwordChecks.length }">12 caracteres</span>
                <span :class="{ ok: passwordChecks.upper }">Mayuscula</span>
                <span :class="{ ok: passwordChecks.lower }">Minuscula</span>
                <span :class="{ ok: passwordChecks.number }">Numero</span>
                <span :class="{ ok: passwordChecks.symbol }">Simbolo</span>
            </div>
            <div class="container-login-card">
                <Button
                    :label="mode === 'login' ? 'INICIAR SESION' : 'CREAR CUENTA'"
                    :icon="mode === 'login' ? 'pi pi-sign-in' : 'pi pi-user-plus'"
                    class="boton"
                    severity="danger"
                    @click="submitAuth()"
                    :loading="isLoading"
                    :disabled="isLoading"
                />
            </div>
        </template>
    </Card>
    
    <!-- Loading Overlay with Spinner -->
    <div v-if="isLoading" class="loading-overlay">
        <ProgressSpinner 
            style="width: 40%; height: 40%;" 
            strokeWidth="8" 
            fill="transparent"
            animationDuration=".5s" 
            aria-label="Custom ProgressSpinner" 
        />
    </div>
    <Toast position="bottom-right" style="width: auto; margin-left: 5vw;"/>
</template>

<script setup>

import Password from 'primevue/password';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import IftaLabel from 'primevue/iftalabel';
import IconField from 'primevue/iconfield';
import InputIcon from 'primevue/inputicon';
import ProgressSpinner from 'primevue/progressspinner';
import Card from 'primevue/card';
import Toast from 'primevue/toast';
import { useAuth } from '@/helpers/useAuth.js';
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useToastGlobal } from '@/helpers/utils.js';


const router = useRouter();
const { login: authLogin, register: authRegister } = useAuth();
const { msjShow } = useToastGlobal();

const mode = ref('login');
const name = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const isLoading = ref(false);

const passwordChecks = computed(() => ({
    length: password.value.length >= 12,
    upper: /[A-Z]/.test(password.value),
    lower: /[a-z]/.test(password.value),
    number: /[0-9]/.test(password.value),
    symbol: /[^A-Za-z0-9]/.test(password.value),
}));

const passwordIsStrong = computed(() => Object.values(passwordChecks.value).every(Boolean));

const setMode = (nextMode) => {
    mode.value = nextMode;
    password.value = '';
    confirmPassword.value = ''; 
};

const submitAuth = async () => {
    if (mode.value === 'register') {
        await register();
        return;
    }

    await login();
};

const login = async () => {

    // 1. Validación básica de campos vacíos
    if (!email.value.trim() || !password.value.trim()) {
        msjShow('error', 'Campos requeridos', 'Por favor complete todos los campos', 3000);
        return; // Detenemos la ejecución
    }

    const normalizedEmail = email.value.trim().toLowerCase();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalizedEmail)) {
        msjShow('error', 'Correo inválido', 'Ingrese el correo electrónico completo', 3000);
        return;
    }

    isLoading.value = true;

    try {
        // 2. Llamada al servicio de autenticación
        await authLogin(normalizedEmail, password.value);

        msjShow('success', 'Éxito', 'Inicio de sesión exitoso', 2000);

        // 3. Si todo sale bien, redirigimos después de 1 segundo
        setTimeout(1000);
        router.push('/home');
        
    } catch (error) {
        const status = error?.response?.status;
        if (status === 429) {
            msjShow('warn', 'Demasiados intentos', 'Has superado el límite de intentos. Espera un momento antes de volver a intentarlo.', 6000);
        } else {
            msjShow('error', 'Error al iniciar sesión', 'Credenciales invalidas', 4000);
        }
    } finally {
        isLoading.value = false;
    }
};

const register = async () => {
    const normalizedName = name.value.trim();
    const normalizedEmail = email.value.trim().toLowerCase();

    if (!normalizedName || !normalizedEmail || !password.value.trim() || !confirmPassword.value.trim()) {
        msjShow('error', 'Campos requeridos', 'Por favor complete todos los campos', 3000);
        return;
    }

    if (password.value !== confirmPassword.value) {
        msjShow('error', 'Contraseñas no coinciden', 'Las contraseñas ingresadas no coinciden', 3000);
        return;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalizedEmail)) {
        msjShow('error', 'Correo inválido', 'Ingrese el correo electrónico completo', 3000);
        return;
    }

    if (!passwordIsStrong.value) {
        msjShow('error', 'Contraseña débil', 'Use una contraseña de al menos 12 caracteres con mayúscula, minúscula, número y símbolo.', 4500);
        return;
    }

    isLoading.value = true;

    try {
        await authRegister(normalizedName, normalizedEmail, password.value);
        msjShow('success', 'Cuenta creada', 'Ahora puedes iniciar sesion con tus credenciales.', 3500);
        mode.value = 'login';
        name.value = '';
        email.value = normalizedEmail;
        password.value = '';
        confirmPassword.value = '';
    } catch (error) {
        msjShow('error', 'No se pudo registrar', error || 'No se pudo completar el registro', 4000);
    } finally {
        isLoading.value = false;
    }
};


</script>

<style scoped>

::v-deep(.p-password-input) {
    width: 100% !important;
}

.container-login {
    width: 100%;
    max-width: 25rem;
}

.container-login.register {
    width: 100%;
    max-width: 40rem;
}

.auth-mode {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 6px;
    width: 90%;
    margin: 0 auto 1rem;
    padding: 5px;
    border: 1px solid #e4e7ec;
    border-radius: 8px;
    background: #f9fafb;
}

.auth-mode button {
    min-height: 36px;
    border: 0;
    border-radius: 6px;
    background: transparent;
    color: #475467;
    font-weight: 800;
    cursor: pointer;
}

.auth-mode button.active {
    background: #091350;
    color: #fff;
}

.password-rules {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    width: 90%;
    margin: -0.5rem auto 1rem;
}

.password-rules span {
    padding: 2px;
    border-radius: 999px;
    background: #f2f4f7;
    color: #667085;
    font-size: 0.8rem;
    font-weight: 800;
}

.password-rules span.ok {
    background: #e7f6ec;
    color: #157347;
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
