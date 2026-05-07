from fastapi import APIRouter, HTTPException, Depends, Header, Request
from pydantic import BaseModel
from services.auth import login as auth_login
from config.db import supabase, supabase_admin
from services.rate_limit import limiter
import re


router = APIRouter()

# Definimos qué datos esperamos del frontend
class LoginSchema(BaseModel):
    email: str
    password: str

class RegisterSchema(BaseModel):
    email: str
    password: str
    name: str

class RefreshTokenSchema(BaseModel):
    token: str

async def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail='Token no proporcionado')
    parts = authorization.split()
    if len(parts) != 2:
        raise HTTPException(status_code=401, detail='Formato de token inválido')
    scheme, token = parts
    if scheme.lower() != 'bearer':
        raise HTTPException(status_code=401, detail='Esquema de autenticación no soportado')

    try:
        user = supabase.auth.get_user(token)
        return user.user
    except HTTPException as e:
        raise e

def validate_password(password: str):
    if len(password) < 12:
        raise HTTPException(status_code=400, detail="La contrasena debe tener al menos 12 caracteres")
    if not re.search(r"[A-Z]", password):
        raise HTTPException(status_code=400, detail="La contrasena debe incluir una mayuscula")
    if not re.search(r"[a-z]", password):
        raise HTTPException(status_code=400, detail="La contrasena debe incluir una minuscula")
    if not re.search(r"[0-9]", password):
        raise HTTPException(status_code=400, detail="La contrasena debe incluir un numero")
    if not re.search(r"[^A-Za-z0-9]", password):
        raise HTTPException(status_code=400, detail="La contrasena debe incluir un simbolo")

@router.post("/register")
async def register(data: RegisterSchema):
    validate_password(data.password)

    try:
        if supabase_admin:
            auth_response = supabase_admin.auth.admin.create_user({
                "email": data.email,
                "password": data.password,
                "email_confirm": True,
                "user_metadata": {"name": data.name},
            })
        else:
            auth_response = supabase.auth.sign_up({
                "email": data.email,
                "password": data.password,
                "options": {
                    "data": {"name": data.name}
                }
            })

        if not auth_response.user:
            raise HTTPException(status_code=400, detail="Supabase no devolvio un usuario al registrarse")

        user_id = auth_response.user.id

        db = supabase_admin or supabase
        db.table("profiles").upsert({
            "id": user_id,
            "name": data.name,
            "role": "user"
        }).execute()

        return { "message" : "Usuario registrado correctamente"}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error al registrar usuario: {type(e).__name__}: {e}")
        error_text = str(e)
        if "rate limit" in error_text.lower():
            raise HTTPException(
                status_code=429,
                detail=(
                    "Supabase alcanzo el limite de envio de emails. "
                    "Espera a que se reinicie la cuota o configura SUPABASE_SERVICE_ROLE_KEY "
                    "en backend/.env para registrar usuarios confirmados desde el backend."
                )
            )
        raise HTTPException(status_code=400, detail=f"Error al registrar el usuario: {e}")


@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, data: LoginSchema):
    try:
        # Llamamos a la función de login en services/auth.py
        result = await auth_login(data.email, data.password)
        return result
    except HTTPException as e:
        # Si hay un error, lo propagamos al frontend
        raise e

@router.post("/refresh-token")
async def refresh_token(data: RefreshTokenSchema):
    try:
        auth_response = supabase.auth.refresh_session(data.token)

        if not auth_response.session:
            raise HTTPException(status_code=401, detail="Refresh token inválido")

        session = auth_response.session
        return {
            "message": "Token refrescado",
            "accessToken": session.access_token,
            "refreshToken": session.refresh_token,
            "expiresAt": session.expires_at,
            "session": {
                "access_token": session.access_token,
                "refresh_token": session.refresh_token,
                "expires_at": session.expires_at
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error al refrescar token: {e}")
        raise HTTPException(status_code=401, detail="Refresh token inválido o expirado")
