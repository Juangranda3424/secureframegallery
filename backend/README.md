# Configuracion del Backend
## Requisitos
- Python 3.11 o superior
- pip (v20 o superior)
## Instalación
1. Clona el repositorio del backend:
    ```bash
    git clone
     ```
2. Navega al directorio del backend:
    ```bash
    cd secureframegallery/backend
     ```
3. Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
## Configuración
1. Crea un archivo `.env` en la raíz del proyecto con la siguiente configuración:
    ```env
    SUPABASE_URL=https://tu-proyecto.supabase.co
    SUPABASE_ANON_KEY=tu-llave-anon-muy-larga-aqui
    ```
    Asegúrate de reemplazar `tu-proyecto` y `tu-llave-anon-muy-larga-aqui` con los valores correspondientes de tu proyecto en Supabase.
## Ejecución
1. Inicia el servidor de desarrollo:
    ```bash
    python server.py
    ```
2. El backend estará corriendo en `http://localhost:8000`.

