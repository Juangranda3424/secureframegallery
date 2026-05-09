from fastapi import APIRouter, FastAPI, HTTPException, Depends
from pydantic import BaseModel
from routers.auth import get_current_user
from services.rbac import require_role, Role
from services.sanitizer import sanitize_text_input
from services.notifications import create_notification
from config.db import supabase, supabase_admin

router = APIRouter(tags=["albums"])
app = FastAPI()

db = supabase_admin or supabase

# datos del front
class AlbumSchema(BaseModel):
    title: str
    description: str
    initial_priv: bool = True

class AlbumInDB(AlbumSchema):
    id: str
    owner_id: str
    status: str

@router.get("/public")
async def read_public_albums():
    response = (
        db.table("albums")
        .select("*")
        .eq("status", "approved")
        .eq("initial_priv", False)
        .execute()
    )
    return response.data

@router.get("", response_model=list[AlbumInDB])
async def read_albums(token: str = Depends(get_current_user)):
    """Get all products"""
    try:
        response = (
            db.table("albums")
            .select("*")
            .eq("owner_id", token.id)
            .neq("status", "rejected")
            .execute()
        )
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pending")
async def read_pending_albums(token = Depends(require_role(Role.SUPERVISOR, Role.ADMIN))):
    response = (
        db.table("albums")
        .select("*")
        .eq("status", "pending")
        .execute()
    )
    return response.data

@router.post("", response_model=AlbumInDB)
def create_album(album: AlbumSchema, token: str = Depends(get_current_user)):
    """Create a new album"""
    data = album.dict()

    data["title"] = sanitize_text_input(data["title"], 100)
    data["description"] = sanitize_text_input(data["description"], 500)
    data["owner_id"] = token.id
    data["status"] = "pending"

    response = db.table("albums").insert(data).execute()
    if not response.data:
        raise HTTPException(status_code=500, detail="Error al crear el album")
    return response.data[0]

@router.delete("/{album_id}")
def delete_album(album_id: str, token: str = Depends(get_current_user)):
    """Delete an album"""
    album_resp = db.table("albums").select("*").eq("id", album_id).execute()
    if not album_resp.data:
        raise HTTPException(status_code=404, detail="Album no encontrado")
    
    album = album_resp.data[0]
    if album.get("owner_id") != token.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este álbum")
    
    response = db.table("albums").delete().eq("id", album_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Album no encontrado")
    return {"message": f"Album with ID {album_id} deleted"}

@router.patch("/{album_id}/approve")
async def approve_album(album_id: str, token=Depends(require_role(Role.SUPERVISOR, Role.ADMIN))):
    """Supervisor aprueba album pendiente"""
    album_resp = db.table("albums").select("id,title,owner_id").eq("id", album_id).execute()
    if not album_resp.data:
        raise HTTPException(status_code=404, detail="Album no encontrado")

    album = album_resp.data[0]
    response = db.table("albums").update({"status": "approved"}).eq("id", album_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Album no encontrado")

    create_notification(
        album["owner_id"],
        "Album aprobado",
        f"Tu album '{album['title']}' fue aprobado por el supervisor. Ya puedes subir imagenes.",
        "approved",
    )
    
    return {"message": f"Album {album_id} aprobado"}

@router.patch("/{album_id}/reject")
async def reject_album(album_id: str, token=Depends(require_role(Role.SUPERVISOR, Role.ADMIN))):
    """Supervisor rechaza album"""
    album_resp = db.table("albums").select("id,title,owner_id").eq("id", album_id).execute()
    if not album_resp.data:
        raise HTTPException(status_code=404, detail="Album no encontrado")

    album = album_resp.data[0]
    response = db.table("albums").update({"status": "rejected"}).eq("id", album_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Album no encontrado")

    create_notification(
        album["owner_id"],
        "Album rechazado",
        f"Tu album '{album['title']}' fue rechazado por el supervisor y ya no aparecera en tu galeria.",
        "rejected",
    )

    return {"message": f"Album {album_id} rechazado"}
