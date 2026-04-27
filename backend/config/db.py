import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargamos las variables de entorno desde un archivo .env
load_dotenv()

# Obtenemos las credenciales (asegúrate de que los nombres coincidan en tu .env)
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_ANON_KEY")

if not url or not key:
    raise ValueError("Faltan las credenciales de Supabase en el archivo .env")

# Inicializamos el cliente de forma global
supabase: Client = create_client(url, key)

def get_supabase():
    """
    Función de utilidad para obtener el cliente. 
    Útil si luego decides implementar lógica de sesión o cierre.
    """
    return supabase