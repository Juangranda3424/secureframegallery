# SecureFrame Gallery API

Backend FastAPI para una galeria publica segura con autenticacion Supabase, RBAC, revision de albumes, validacion de imagenes, deteccion basica de esteganografia y cabeceras de seguridad.

## Tecnologias

- FastAPI y Uvicorn
- Supabase Auth y tablas Postgres
- SlowAPI para rate limiting
- python-magic para validar tipo real de archivo
- Pillow, piexif y numpy para procesamiento y analisis de imagenes

## Variables de Entorno

Crea `backend/.env`:

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_ANON_KEY=tu-llave-anon
# Opcional, solo backend: evita el limite de emails de Supabase al registrar usuarios
SUPABASE_SERVICE_ROLE_KEY=tu-service-role-key
CORS_ORIGINS=http://localhost:5173
```

Si `SUPABASE_SERVICE_ROLE_KEY` esta configurada, `POST /api/v1/auth/register` crea el usuario con Supabase Admin y lo deja confirmado sin enviar correo. No pongas esta llave en el frontend ni en codigo publico.

El frontend debe tener `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_API_TIMEOUT=100000
```

## Instalacion

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

En Linux, si `python-magic` falla, instala tambien `libmagic1`.

## Ejecutar Backend

```bash
cd backend
python server.py
```

La API queda en `http://localhost:8000`.

## Ejecutar Frontend

```bash
cd frontend
npm install
npm run dev
```

## Flujo Principal

1. Un usuario se registra o inicia sesion.
2. El usuario crea un album, que queda con estado `pending`.
3. Un supervisor o admin aprueba o rechaza el album.
4. El usuario solo puede subir imagenes a albumes `approved`.
5. El backend valida tamano, MIME real, limpia EXIF y analiza esteganografia.
6. Imagen limpia queda `approved`; imagen sospechosa queda `quarantined`.
7. Supervisor/admin puede aprobar o rechazar imagenes en cuarentena.
8. Visitantes solo ven albumes e imagenes `approved`.

## Roles

- `user`: crea albumes y sube imagenes a sus albumes aprobados.
- `supervisor`: revisa albumes pendientes e imagenes en cuarentena.
- `admin`: tiene permisos de supervisor.
- `visitor`: acceso publico solo a contenido aprobado.

## Endpoints Principales

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

## Justificacion de Seguridad

- RBAC consulta el rol real en `profiles`.
- El login tiene rate limiting para reducir fuerza bruta.
- La subida valida permisos antes de leer/procesar archivos.
- `python-magic` valida el MIME real para evitar archivos renombrados.
- Las imagenes se reescriben sin EXIF para reducir fuga de metadatos.
- La deteccion de esteganografia combina analisis LSB, entropia y datos extra al final del archivo.
- La API agrega cabeceras `X-Content-Type-Options`, `Content-Security-Policy`, `X-Frame-Options` y `X-XSS-Protection`.
