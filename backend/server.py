from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from routers.auth import router as auth_router
from routers.album import router as album_router
from routers.image import router as image_router
from routers.notification import router as notification_router
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from services.rate_limit import limiter
import os
from pathlib import Path

load_dotenv()

app = FastAPI(title="SecureFrame Gallery API", version="1.0")
uploads_dir = Path(__file__).resolve().parent / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)

# Incluir routers
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(album_router, prefix="/api/v1/albums")
app.include_router(image_router, prefix="/api/v1/albums")
app.include_router(notification_router, prefix="/api/v1/notifications")
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

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
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

app.add_middleware(SecurityHeadersMiddleware)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS debe agregarse de último para quedar como middleware más externo.
# Así cubre las respuestas de error que genera BaseHTTPMiddleware (500s) y
# garantiza que el header Access-Control-Allow-Origin esté siempre presente.
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
