from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from routers.auth import get_current_user
from config.db import supabase, supabase_admin

router = APIRouter(tags=["notifications"])
db = supabase_admin or supabase


class NotificationInDB(BaseModel):
    id: str
    title: str
    message: str
    type: str
    read: bool
    created_at: Optional[str] = None


@router.get("", response_model=list[NotificationInDB])
async def list_notifications(user=Depends(get_current_user)):
    try:
        response = (
            db.table("notifications")
            .select("id,title,message,type,read,created_at")
            .eq("user_id", user.id)
            .order("created_at", desc=True)
            .limit(20)
            .execute()
        )
        return response.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener notificaciones: {e}")


@router.get("/unread", response_model=list[NotificationInDB])
async def list_unread_notifications(user=Depends(get_current_user)):
    try:
        response = (
            db.table("notifications")
            .select("id,title,message,type,read,created_at")
            .eq("user_id", user.id)
            .eq("read", False)
            .order("created_at", desc=True)
            .execute()
        )
        return response.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener notificaciones: {e}")


@router.patch("/{notification_id}/read")
async def mark_notification_read(notification_id: str, user=Depends(get_current_user)):
    response = (
        db.table("notifications")
        .update({"read": True})
        .eq("id", notification_id)
        .eq("user_id", user.id)
        .execute()
    )

    if not response.data:
        raise HTTPException(status_code=404, detail="Notificacion no encontrada")

    return {"message": "Notificacion marcada como leida"}
