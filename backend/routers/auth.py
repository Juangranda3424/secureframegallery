from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from services.auth import login as auth_login


router = APIRouter()

# Definimos qué datos esperamos del frontend
class LoginSchema(BaseModel):
    email: str
    password: str


@router.post("/login")
async def login(data: LoginSchema):
    try:
        # Llamamos a la función de login en services/auth.py
        result = await auth_login(data.email, data.password)
        return result
    except HTTPException as e:
        # Si hay un error, lo propagamos al frontend
        raise e