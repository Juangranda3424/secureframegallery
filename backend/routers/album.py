from fastapi import APIRouter,FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client
import os
from routers.auth import get_current_user
from services.rbac import require_role, Role
from services.sanitizer import sanitize_text_input

#TRAIGO LAS VARIABLES DEL ENV
load_dotenv(dotenv_path="./.env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")


router = APIRouter(tags=["albums"])
app = FastAPI()

#creo el cliente al supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# datos del front
class AlbumSchema(BaseModel):
    title: str
    description: str
    initial_priv: bool = True

class AlbumInDB(AlbumSchema):
    id: str
    owner_id: str

@router.get("/public")
async def read_public_albums():
    response = supabase.table("albums").select("*").eq("status", "approved").execute()
    return response.data

@router.get("", response_model=list[AlbumInDB])
async def read_albums(token: str = Depends(get_current_user)):
    """Get all products"""
    try:
        response = supabase.table("albums").select("*").eq("owner_id", token.id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pending")
async def read_pending_albums(token = Depends(require_role(Role.SUPERVISOR, Role.ADMIN))):
    response = (
        supabase.table("albums")
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

    response = supabase.table("albums").insert(data).execute()
    if not response.data:
        raise HTTPException(status_code=500, detail="Error al crear el album")
    return response.data[0]

@router.delete("/{album_id}")
def delete_album(album_id: str, token: str = Depends(get_current_user)):
    """Delete an album"""
    album_resp = supabase.table("albums").select("*").eq("id", album_id).execute()
    if not album_resp.data:
        raise HTTPException(status_code=404, detail="Album no encontrado")
    
    album = album_resp.data[0]
    if album.get("owner_id") != token.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este álbum")
    
    response = supabase.table("albums").delete().eq("id", album_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Album no encontrado")
    return {"message": f"Album with ID {album_id} deleted"}

@router.patch("/{album_id}/approve")
async def approve_album(album_id: str, token=Depends(require_role(Role.SUPERVISOR, Role.ADMIN))):
    """Supervisor aprueba album pendiente"""
    response = supabase.table("albums").update({"status": "approved"}).eq("id", album_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Album no encontrado")
    
    return {"message": f"Album {album_id} aprobado"}

@router.patch("/{album_id}/reject")
async def reject_album(album_id: str, token=Depends(require_role(Role.SUPERVISOR, Role.ADMIN))):
    """Supervisor rechaza album"""
    response = supabase.table("albums").update({"status": "rejected"}).eq("id", album_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Album no encontrado")
    return {"message": f"Album {album_id} rechazado"}
