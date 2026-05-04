from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from routers.auth import router as auth_router
from routers.album import router as album_router
from routers.image import router as image_router
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi.middleware import SlowAPIMiddleware
from services.rate_limit import limiter
import os
from pathlib import Path

load_dotenv()

app = FastAPI(title="SecureFrame Gallery API", version="1.0")
uploads_dir = Path(__file__).resolve().parent / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Incluir routers
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(album_router, prefix="/api/v1/albums")
app.include_router(image_router, prefix="/api/v1/albums")
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# Aquí podrías incluir otros routers para CRUD de imágenes, etc. Es una buena utilizar /api/v1/ para versionar tu API desde el principio.
# app.include_router(router, prefix="/api/v1")
# app.include_router(crud_router, prefix="/api/v1")

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        # Evita que el navegador "adivine" el tipo de contenido (MIME sniffing)
        # Protege contra ejecución de archivos maliciosos
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Política de seguridad de contenido (CSP)
        # Define desde dónde se pueden cargar recursos (scripts, imágenes, estilos, etc.)
        response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

app.add_middleware(SecurityHeadersMiddleware)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
