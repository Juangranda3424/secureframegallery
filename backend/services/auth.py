from fastapi import HTTPException
from config.db import supabase

async def login(username: str, password: str):
    try:
        # 1. Autenticación en Supabase Auth
        auth_response = supabase.auth.sign_in_with_password({
            "email": username,
            "password": password
        })
        
        # Obtenemos el ID del usuario autenticado
        user_id = auth_response.user.id

        # 2. Buscamos los datos extra en la tabla 'profiles'
        # Usamos .single() porque sabemos que solo hay un perfil por cada ID de usuario
        profile_query = supabase.table("profiles") \
            .select("name, role") \
            .eq("id", user_id) \
            .single() \
            .execute()

        profile_data = profile_query.data

        # 3. Devolvemos todo junto
        return {
            "message": "Login exitoso",
            "user": {
                "id": user_id,
                "email": auth_response.user.email,
                "name": profile_data.get("name") if profile_data else "Sin nombre",
                "role": profile_data.get("role") if profile_data else "user"
            },
            "session": {
                "access_token": auth_response.session.access_token,
                "refresh_token": auth_response.session.refresh_token,
                "expires_at": auth_response.session.expires_at
            }
        }

    except Exception as e:
        # Si quieres ver el error real en consola mientras programas:
        print(f"Error en login: {e}")
        raise HTTPException(
            status_code=401,
            detail="Credenciales invalidas"
        )
