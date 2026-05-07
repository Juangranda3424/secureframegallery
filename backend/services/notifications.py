from config.db import supabase, supabase_admin

db = supabase_admin or supabase


def create_notification(user_id: str, title: str, message: str, notification_type: str = "info"):
    try:
        db.table("notifications").insert({
            "user_id": user_id,
            "title": title,
            "message": message,
            "type": notification_type,
            "read": False,
        }).execute()
    except Exception as e:
        print(f"Error al crear notificacion: {type(e).__name__}: {e}")
