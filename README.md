# SecureFrame Gallery

Aplicacion web para gestion segura de albumes e imagenes. Incluye registro e inicio de sesion, revision manual por supervisor, validacion de archivos, limpieza de metadatos, deteccion basica de esteganografia y galeria publica segura.

## Tecnologias

- Backend: FastAPI, Uvicorn, Supabase Auth/Postgres, SlowAPI.
- Frontend: Vue 3, Vite, PrimeVue, Axios.
- Seguridad de imagenes: python-magic, Pillow, piexif, numpy.

## Requisitos

- Python 3.11 o superior.
- Node.js 18 o superior.
- Cuenta/proyecto en Supabase.
- En Linux, `python-magic` requiere la libreria del sistema `libmagic`.

```bash
sudo apt install libmagic1
```

## Variables de entorno

Crea `backend/.env`:

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu-llave-anon
SUPABASE_SERVICE_ROLE_KEY=tu-service-role-key
CORS_ORIGINS=http://localhost:5173
```

`SUPABASE_SERVICE_ROLE_KEY` es opcional, pero recomendada para que el backend pueda crear usuarios confirmados desde `/api/v1/auth/register`. No debe exponerse en el frontend.

Crea `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_API_TIMEOUT=100000
```

## Instalacion

Backend:

Linux 

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Windows (PowerShell):

```bash
cd backend
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

Frontend:

Windows/Linux/MacOS:
```bash
cd frontend
npm install
```

## Ejecucion en desarrollo

Levantar backend:

Linux
```bash
cd backend
source venv/bin/activate
python server.py
```

Windows (PowerShell):
```bash
cd backend
source venv/Scripts/activate
python server.py
```

La API queda disponible en:

```text
http://localhost:8000
```

Levantar frontend:

```bash
cd frontend
npm run dev
```

La aplicacion queda disponible normalmente en:

```text
http://localhost:5173
```

## Supabase

- Crea un proyecto en Supabase.
- Corre el script `supabase.sql` para crear las tablas
- En Storage, crea un bucket llamado `archivos` con acceso público y un tamaño máximo de 10MB.


## Docker

Este proyecto no incluye `Dockerfile` ni `docker-compose.yml`. Para ejecutarlo se usan los comandos anteriores de backend y frontend.

## Credenciales de prueba

Estas cuentas deben existir en Supabase Auth y en la tabla `profiles` para probar los roles.

Supervisor:

```text
correo: admin@test.com
password: Password1234!.
rol: supervisor
```

Usuario:

```text
correo: user@test.com
password: Password1234!.
rol: user
```

Si las cuentas no existen, puedes crearlas desde la pantalla de registro o desde Supabase. Para que `admin@test.com` tenga permisos de supervisor, actualiza su perfil en la tabla `profiles` con `role = 'supervisor'`.

## Flujo principal

1. El usuario se registra o inicia sesion.
2. El usuario solicita un album. El album queda en estado `pending`.
3. El supervisor revisa la solicitud y aprueba o rechaza.
4. Si el album es aprobado, el usuario puede subir imagenes.
5. La imagen se valida antes de guardarse definitivamente.
6. Si la imagen es limpia, queda `approved`.
7. Si la imagen es sospechosa, queda `quarantined`.
8. El supervisor revisa imagenes en cuarentena y decide aprobar o eliminar.
9. Los visitantes pueden navegar `/public` y ver solo albumes publicos aprobados e imagenes aprobadas.

## Seguridad implementada

### Autenticacion y autorizacion

- Registro e inicio de sesion con Supabase Auth.
- Supabase Auth se encarga del almacenamiento seguro/hash de contrasenas.
- Validacion de contrasenas fuertes en registro: minimo 12 caracteres, mayuscula, minuscula, numero y simbolo.
- Rate limiting con SlowAPI:
  - login: `5/minute`
  - registro: `3/minute`
- Mensajes genericos para reducir enumeracion de usuarios, por ejemplo `Credenciales invalidas`.
- RBAC por rol (`user`, `supervisor`, `admin`) consultando la tabla `profiles`.

### Gestion de albumes

- Los usuarios no publican albumes directamente.
- `POST /api/v1/albums` crea una solicitud en estado `pending`.
- Solo `supervisor` o `admin` puede aprobar o rechazar.
- Los campos de texto se sanitizan en backend para conservar texto plano y evitar XSS.

### Visualizacion publica segura

- `GET /api/v1/albums/public` solo devuelve albumes `approved` y publicos (`initial_priv = false`).
- `GET /api/v1/albums/{album_id}/images/public` solo devuelve imagenes `approved` de albumes aprobados y publicos.
- Cabeceras de seguridad configuradas en FastAPI:
  - `Content-Security-Policy`
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `X-XSS-Protection`

## Justificacion tecnica de deteccion de esteganografia

La deteccion se implementa en `backend/services/steganography_detector.py`. Se eligio un enfoque estadistico simple porque el requisito no exige IA avanzada y permite analizar indicios frecuentes de esteganografia con bajo costo computacional.

Metodos usados:

- Analisis LSB: se inspecciona el bit menos significativo de los canales RGB. Muchas tecnicas de esteganografia ocultan datos modificando esos bits. Una distribucion demasiado balanceada o anomala puede ser una senal de manipulacion.
- Entropia: se calcula la aleatoriedad de los valores de pixeles. Entropia muy alta combinada con LSB sospechoso puede indicar datos ocultos o ruido artificial.
- EOF/trailing data: se detectan datos agregados despues del final real del archivo en JPEG, PNG, GIF o WEBP. Esto cubre ataques donde se concatena informacion oculta al final del archivo.

Flujo de subida:

1. El backend lee el archivo en memoria.
2. `python-magic` verifica el MIME real por contenido, no por extension.
3. Pillow abre la imagen y se reescribe una copia sin EXIF/metadatos.
4. El detector analiza LSB, entropia y datos extra al final.
5. Si `is_suspicious = false`, la imagen se guarda como `approved`.
6. Si `is_suspicious = true`, la imagen queda como `quarantined` y no se publica.

Este enfoque reduce riesgos de:

- archivos renombrados como imagen;
- fuga de ubicacion GPS o metadatos EXIF;
- payloads agregados al final del archivo;
- esteganografia basica basada en LSB.

## Endpoints principales

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh-token`
- `GET /api/v1/albums/public`
- `GET /api/v1/albums`
- `POST /api/v1/albums`
- `GET /api/v1/albums/pending`
- `PATCH /api/v1/albums/{album_id}/approve`
- `PATCH /api/v1/albums/{album_id}/reject`
- `POST /api/v1/albums/{album_id}/images`
- `GET /api/v1/albums/{album_id}/images/public`
- `GET /api/v1/albums/quarantine`
- `PATCH /api/v1/albums/quarantine/{image_id}/approve`
- `DELETE /api/v1/albums/quarantine/{image_id}/reject`
