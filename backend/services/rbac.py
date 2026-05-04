from enum import Enum
from fastapi import HTTPException, Depends
from routers.auth import get_current_user
from config.db import supabase

class Role(str, Enum):
    USER = "user"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"
    VISITOR = "visitor"

def get_user_role(user_id: str) -> str:
    profile = (
        supabase.table("profiles")
        .select("role")
        .eq("id", user_id)
        .single()
        .execute()
    )

    if not profile.data:
        return Role.VISITOR.value
    
    return profile.data.get("role", Role.VISITOR.value)

def require_role(*allowed_roles: Role):
    async def verify_role(user = Depends(get_current_user)):
        role = get_user_role(user.id)
        allowed_values = [r.value for r in allowed_roles]

        if role not in allowed_values:
            raise HTTPException(status_code=403, detail="Rol insuficiente")
        return user
    return verify_role
