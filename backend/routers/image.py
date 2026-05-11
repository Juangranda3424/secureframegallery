from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from pydantic import BaseModel
from typing import Optional
import json
import re
from routers.auth import get_current_user
from pathlib import Path
from uuid import UUID, uuid4
from services.file_validator import validate_file
from services.steganography_detector import detect_steganography
from services.image_processor import strip_exif
from services.rbac import require_role, Role
from services.notifications import create_notification
from config.db import supabase, supabase_admin

router = APIRouter(tags=["images"])

db = supabase_admin or supabase

#DATOS DEL FRONT
class ImageSchema(BaseModel):
    file_path: str

class ImageInDB(ImageSchema):
    id: str
    album_id: str
    status: str
    album_title: Optional[str] = None
    album: Optional[dict] = None
    image_analysis: Optional[list[dict]] = None

@router.get("/{album_id}/images", response_model=list[ImageInDB])
async def read_images(album_id: UUID, token: str = Depends(get_current_user)):
    """Get approved images for the album owner."""
    album_resp = db.table("albums").select("*").eq("id", album_id).execute()
    if not album_resp.data:
        raise HTTPException(status_code=404, detail="Álbum no encontrado")
    album = album_resp.data[0]
    
    if album.get("owner_id") != token.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver las imágenes de este álbum")
    response = (
        db.table("images")
        .select("*")
        .eq("album_id", album_id)
        .eq("status", "approved")
        .execute()
    )
    return response.data

@router.post("/{album_id}/images", response_model=ImageInDB)
async def upload_images(album_id: str, file: UploadFile = File(...), token: str = Depends(get_current_user)):
    """Upload images"""

    album_resp = db.table("albums").select("*").eq("id", album_id).execute()

    if not album_resp.data:
        raise HTTPException(status_code=404, detail="Álbum no encontrado")
    album = album_resp.data[0]

    if album.get("owner_id") != token.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para subir imágenes en este álbum")

    if album.get("status") != "approved":
        raise HTTPException(status_code=403, detail="El album aun no esta aprobado")


    content = await file.read()
    validate_file(content, file.filename)

    analysis = detect_steganography(content)
    clean_content = strip_exif(content)

    original_name = Path(file.filename or "imagen").name
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", original_name).strip("._") or "imagen"
    filename = f"{uuid4().hex}_{safe_name}"
    storage_path = f"albums/{album_id}/{filename}"
    
    # Subir a Supabase Storage
    upload_response = supabase_admin.storage.from_("archivos").upload(
        path=storage_path,
        file=clean_content,
        file_options={
            "content-type": file.content_type
        }
    )

    # Validar subida
    if not upload_response:
        raise HTTPException(
            status_code=500,
            detail="Error al subir la imagen al storage"
        )

    # Obtener URL pública
    public_url = supabase_admin.storage.from_("archivos").get_public_url(
        storage_path
    )


    image_status = "quarantined" if analysis["is_suspicious"] else "approved"

    image_data = {
        "album_id": album_id,
        "file_path": public_url,
        "status": image_status
    }

    response = db.table("images").insert(image_data).execute()

    if not response.data:
        raise HTTPException(status_code=500, detail="Error al subir la imagen")

    analysis_record = {
        "image_id": response.data[0]["id"],
        "analysis_type": "steganography",
        "result": json.dumps(analysis, ensure_ascii=False, indent=2),
        "is_suspicious": analysis["is_suspicious"]
    }
    db.table("image_analysis").insert(analysis_record).execute()

    return response.data[0]
    
@router.delete("/{album_id}/images/{image_id}")
async def delete_image(image_id: UUID, album_id: UUID, token: str = Depends(get_current_user)):
    """Delete an image"""
    album_resp = db.table("albums").select("*").eq("id", album_id).execute()
    if not album_resp.data:
        raise HTTPException(status_code=404, detail="Álbum no encontrado")
    album = album_resp.data[0]

    if album.get("owner_id") != token.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para subir imágenes en este álbum")

    image_resp = db.table("images").select("*").eq("id", image_id).eq("album_id", album_id).execute()
    if not image_resp.data:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    image = image_resp.data[0]

    file_url = image["file_path"]

    marker = "/storage/v1/object/public/archivos/"
    if marker in file_url:
        storage_path = file_url.split(marker)[1]
    else:
        raise HTTPException(
            status_code=500,
            detail="No se pudo determinar la ruta del archivo en Storage"
        )
    
    storage_response = (
        supabase_admin.storage
        .from_("archivos")
        .remove([storage_path])
    )

    db.table("image_analysis").delete().eq("image_id", image_id).execute()

    delete_resp = (
        db.table("images")
        .delete()
        .eq("id", image_id)
        .eq("album_id", album_id)
        .execute()
    )

    if not delete_resp.data:
        raise HTTPException(
            status_code=500,
            detail="No se pudo eliminar la imagen de la base de datos"
        )

    return {
        "message": f"Imagen {image_id} eliminada correctamente",
        "storage_path": storage_path
    }


#Estos endpoints son para revision manual de las imagenes
@router.get("/quarantine", response_model=list[ImageInDB])
async def list_quarantine(token=Depends(require_role(Role.SUPERVISOR, Role.ADMIN))):
    """Ver imagenes en cuarentena"""
    resp = (
        db.table("images")
        .select("*, albums(id,title,description), image_analysis(*)")
        .eq("status", "quarantined")
        .execute()
    )
    images = resp.data or []
    album_ids = list({str(image["album_id"]) for image in images if image.get("album_id")})

    albums_by_id = {}
    if album_ids:
        albums_resp = db.table("albums").select("id,title,description").in_("id", album_ids).execute()
        albums_by_id = {str(album["id"]): album for album in (albums_resp.data or [])}

    for image in images:
        album = image.get("albums") or albums_by_id.get(str(image.get("album_id")))
        image["album"] = album
        image["album_title"] = album.get("title") if album else "Album no encontrado"

    return images

@router.patch("/quarantine/{image_id}/approve")
async def approve_image(image_id: UUID, token=Depends(require_role(Role.SUPERVISOR, Role.ADMIN))):
    """Supervisor aprueba la imagen de cuarentena"""
    image_resp = db.table("images").select("*").eq("id", image_id).single().execute()
    image = image_resp.data
    if not image:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    album_resp = db.table("albums").select("id,title,owner_id").eq("id", image["album_id"]).single().execute()
    album = album_resp.data

    response = db.table("images").update({"status": "approved"}).eq("id", image_id).execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    if album:
        image_name = Path(image["file_path"]).name
        create_notification(
            album["owner_id"],
            "Imagen aprobada",
            f"La imagen '{image_name}' del album '{album['title']}' fue aprobada por el supervisor.",
            "approved",
        )

    return {"message": f"Imagen {image_id} aprobada"}

@router.delete("/quarantine/{image_id}/reject")
async def reject_quarantine_image(image_id: UUID, token=Depends(require_role(Role.SUPERVISOR, Role.ADMIN))):
    """Supervisor rechaza y borra imagen de cuarentena"""
    img = db.table("images").select("*").eq("id", image_id).single().execute().data
    if not img:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    album_resp = db.table("albums").select("id,title,owner_id").eq("id", img["album_id"]).single().execute()
    album = album_resp.data

    upload_path = Path(__file__).resolve().parent.parent / img["file_path"].lstrip("/")
    upload_path.unlink(missing_ok=True)

    db.table("images").delete().eq("id", image_id).execute()

    if album:
        image_name = Path(img["file_path"]).name
        create_notification(
            album["owner_id"],
            "Imagen rechazada",
            f"La imagen '{image_name}' del album '{album['title']}' fue rechazada y eliminada por el supervisor.",
            "rejected",
        )

    return {"message": f"IMagen {image_id} rechazada y eliminada"}

#validacion y control de acceso publico
@router.get("/{album_id}/images/public")
async def get_public_images(album_id: UUID):
    """Visitantes ven solo imagenes aprobadas de albumes aprobados"""

    album = (
        db.table("albums")
        .select("*")
        .eq("id", album_id)
        .eq("status", "approved")
        .eq("initial_priv", False)
        .execute()
    )
    if not album.data:
        raise HTTPException(status_code=404, detail="Álbum no disponible")

    images = db.table("images").select("*").eq("album_id", album_id).eq("status", "approved").execute()
    return images.data
