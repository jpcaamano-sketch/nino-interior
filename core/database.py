import json
from datetime import datetime, timezone

_client = None


def _db():
    global _client
    if _client is None:
        from core.config import SUPABASE_URL, SUPABASE_KEY
        from supabase import create_client
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client


# ─── Procesos ──────────────────────────────────────────────────────────────────

def create_proceso(nombre: str, correo: str) -> dict:
    r = _db().table("nino_procesos").insert({
        "nombre": nombre,
        "correo": correo,
        "estado": "en_progreso",
    }).execute()
    return r.data[0]


def get_proceso(proceso_id: str) -> dict | None:
    r = _db().table("nino_procesos").select("*").eq("id", proceso_id).execute()
    return r.data[0] if r.data else None


def update_proceso(proceso_id: str, **kwargs):
    _db().table("nino_procesos").update(kwargs).eq("id", proceso_id).execute()


def completar_proceso(proceso_id: str, etapa_dominante: str, etapa_co_dominante: str | None,
                      necesidad_dominante: str, necesidad_secundaria: str,
                      intensidad: str, puntajes_etapas: dict,
                      puntajes_necesidades: dict, analisis: dict):
    now = datetime.now(timezone.utc).isoformat()
    update_proceso(
        proceso_id,
        estado="completado",
        etapa_dominante=etapa_dominante,
        etapa_co_dominante=etapa_co_dominante,
        necesidad_dominante=necesidad_dominante,
        necesidad_secundaria=necesidad_secundaria,
        intensidad=intensidad,
        puntajes_etapas=json.dumps(puntajes_etapas),
        puntajes_necesidades=json.dumps(puntajes_necesidades),
        analisis=json.dumps(analisis),
        fecha_completado=now,
    )


# ─── Respuestas ────────────────────────────────────────────────────────────────

def save_respuesta(proceso_id: str, pregunta_id: int, valor_escala=None, texto=None):
    row = {"proceso_id": proceso_id, "pregunta_id": pregunta_id}
    if valor_escala is not None:
        row["valor_escala"] = int(valor_escala)
    if texto:
        row["texto_respuesta"] = str(texto)
    _db().table("nino_respuestas").upsert(
        row, on_conflict="proceso_id,pregunta_id"
    ).execute()


def get_respuestas(proceso_id: str) -> dict:
    r = _db().table("nino_respuestas").select("*").eq("proceso_id", proceso_id).execute()
    result = {}
    for row in r.data:
        pid = row["pregunta_id"]
        result[pid] = row["valor_escala"] if row["valor_escala"] is not None else row["texto_respuesta"]
    return result
