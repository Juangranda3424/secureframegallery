import magic
from pathlib import Path
from fastapi import HTTPException

ALLOWED_MIMETYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_file(file_bytes: bytes, filename: str):
    """Valida tipo real de archivo y su tamano"""
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Archivo demasiado grande. Máximo 10MB.")
    
    mime = magic.from_buffer(file_bytes, mime=True)
    if mime not in ALLOWED_MIMETYPES:
        raise HTTPException(status_code=400, detail=f"Archivo no permitido. Solo se permiten imágenes JPEG, PNG, GIF y WEBP. Tipo detectado: {mime}")
    
    return True