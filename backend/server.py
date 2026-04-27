from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers.auth import router as auth_router
import os

load_dotenv()

app = FastAPI(title="SecureFrame Gallery API", version="1.0")

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

# Aquí podrías incluir otros routers para CRUD de imágenes, etc. Es una buena utilizar /api/v1/ para versionar tu API desde el principio.
# app.include_router(router, prefix="/api/v1")
# app.include_router(crud_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)