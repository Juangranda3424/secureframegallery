from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client
import os
from routers.auth import get_current_user
from pathlib import Path
from uuid import UUID, uuid4
from services.file_validator import validate_file
from services.steganography_detector import detect_steganography
from services.image_processor import strip_exif
from services.rbac import require_role, Role

load_dotenv(dotenv_path='./env')

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

router = APIRouter(tags=["images"])

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

#DATOS DEL FRONT
class ImageSchema(BaseModel):
    file_path: str

class ImageInDB(ImageSchema):
    id: str
    album_id: str

@router.get("/{album_id}/images", response_model=list[ImageInDB])
async def read_images(album_id: UUID, token: str = Depends(get_current_user)):
    """Get all images"""
    album_resp = supabase.table("albums").select("*").eq("id", album_id).execute()
    if not album_resp.data:
        raise HTTPException(status_code=404, detail="Álbum no encontrado")
    album = album_resp.data[0]
    
    if album.get("owner_id") != token.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver las imágenes de este álbum")
    response = supabase.table("images").select("*").eq("album_id", album_id).execute()
    return response.data

@router.post("/{album_id}/images", response_model=ImageInDB)
async def upload_images(album_id: str, file: UploadFile = File(...), token: str = Depends(get_current_user)):
    """Upload images"""

    album_resp = supabase.table("albums").select("*").eq("id", album_id).execute()

    if not album_resp.data:
        raise HTTPException(status_code=404, detail="Álbum no encontrado")
    album = album_resp.data[0]

    if album.get("owner_id") != token.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para subir imágenes en este álbum")

    if album.get("status") != "approved":
        raise HTTPException(status_code=403, detail="El album aun no esta aprobado")


    content = await file.read()
    validate_file(content, file.filename)

    clean_content = strip_exif(content)
    analysis = detect_steganography(clean_content)

    uploads_dir = Path(__file__).resolve().parent.parent / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid4().hex}.jpg"
    file_path = uploads_dir / filename
    file_path.write_bytes(clean_content)


    image_status = "quarantined" if analysis["is_suspicious"] else "approved"

    image_data = {
        "album_id": album_id,
        "file_path": f"/uploads/{filename}",
        "status": image_status
    }

    response = supabase.table("images").insert(image_data).execute()

    if not response.data:
        raise HTTPException(status_code=500, detail="Error al subir la imagen")

    analysis_record = {
        "image_id": response.data[0]["id"],
        "analysis_type": "steganography",
        "result": str(analysis),
        "is_suspicious": analysis["is_suspicious"]
    }
    supabase.table("image_analysis").insert(analysis_record).execute()

    return response.data[0]
    
@router.delete("/{album_id}/images/{image_id}")
async def delete_image(image_id: UUID, album_id: UUID, token: str = Depends(get_current_user)):
    """Delete an image"""
    album_resp = supabase.table("albums").select("*").eq("id", album_id).execute()
    if not album_resp.data:
        raise HTTPException(status_code=404, detail="Álbum no encontrado")
    album = album_resp.data[0]

    if album.get("owner_id") != token.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para subir imágenes en este álbum")

    response = supabase.table("images").delete().eq("id", image_id).eq("album_id", album_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")
    return {"message": f"Imagen with ID {image_id} deleted"} 


#Estos endpoints son para revision manual de las imagenes
@router.get("/quarantine", response_model=list[ImageInDB])
async def list_quarantine(token=Depends(require_role(Role.SUPERVISOR, Role.ADMIN))):
    """Ver imagenes en cuarentena"""
    resp = supabase.table("images").select("*, image_analysis(*)").eq("status", "quarantined").execute()
    return resp.data

@router.patch("/quarantine/{image_id}/approve")
async def approve_image(image_id: UUID, token=Depends(require_role(Role.SUPERVISOR, Role.ADMIN))):
    """Supervisor aprueba la imagen de cuarentena"""
    response = supabase.table("images").update({"status": "approved"}).eq("id", image_id).execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    return {"message": f"Imagen {image_id} aprobada"}

@router.delete("/quarantine/{image_id}/reject")
async def reject_quarantine_image(image_id: UUID, token=Depends(require_role(Role.SUPERVISOR, Role.ADMIN))):
    """Supervisor rechaza y borra imagen de cuarentena"""
    img = supabase.table("images").select("*").eq("id", image_id).single().execute().data

    Path(f"backend{img['file_path']}").unlink(missing_ok=True)

    supabase.table("images").delete().eq("id", image_id).execute()

    return {"message": f"IMagen {image_id} rechazada y eliminada"}

#validacion y control de acceso publico
@router.get("/{album_id}/images/public")
async def get_public_images(album_id: UUID):
    """Visitantes ven solo imagenes aprobadas de albumes aprobados"""

    album = supabase.table("albums").select("*").eq("id", album_id).eq("status", "approved").execute()
    if not album.data:
        raise HTTPException(status_code=404, detail="Álbum no disponible")

    images = supabase.table("images").select("*").eq("album_id", album_id).eq("status", "approved").execute()
    return images.data
