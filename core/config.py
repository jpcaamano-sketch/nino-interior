import os

def _get(key):
    return os.environ.get(key, "")

SUPABASE_URL   = _get("SUPABASE_URL")
SUPABASE_KEY   = _get("SUPABASE_KEY")
RESEND_API_KEY = _get("RESEND_API_KEY")
GOOGLE_API_KEY = _get("GOOGLE_API_KEY")
BASE_URL       = os.environ.get("BASE_URL", "http://localhost:8547")
FROM_EMAIL     = "Mi Niño Interior <noreply@escuelayocreo.cl>"
AGENDA_URL     = os.environ.get("AGENDA_URL", "https://jpecoachdevida.cl/agendar-sesion")
