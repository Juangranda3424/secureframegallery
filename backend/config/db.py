import os
from dotenv import load_dotenv
from supabase import create_client, Client
from typing import Optional

# Cargamos las variables de entorno desde un archivo .env
load_dotenv()

# Obtenemos las credenciales (asegúrate de que los nombres coincidan en tu .env)
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_ANON_KEY")
service_role_key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    raise ValueError("Faltan las credenciales de Supabase en el archivo .env")

# Inicializamos el cliente de forma global
supabase: Client = create_client(url, key)
supabase_admin: Optional[Client] = (
    create_client(url, service_role_key) if service_role_key else None
)

def get_supabase():
    """
    Función de utilidad para obtener el cliente. 
    Útil si luego decides implementar lógica de sesión o cierre.
    """
    return supabase
