-- ============================================================
-- Mi Niño Interior — Setup DB
-- Ejecutar en Supabase SQL Editor
-- ============================================================

CREATE TABLE IF NOT EXISTS nino_procesos (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre                TEXT NOT NULL,
    correo                TEXT NOT NULL,
    estado                TEXT DEFAULT 'en_progreso',
    etapa_dominante       TEXT,
    etapa_co_dominante    TEXT,
    necesidad_dominante   TEXT,
    necesidad_secundaria  TEXT,
    intensidad            TEXT,
    puntajes_etapas       TEXT,
    puntajes_necesidades  TEXT,
    analisis              TEXT,
    fecha_creacion        TIMESTAMPTZ DEFAULT now(),
    fecha_completado      TIMESTAMPTZ
);

ALTER TABLE nino_procesos DISABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS nino_respuestas (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proceso_id      UUID NOT NULL REFERENCES nino_procesos(id) ON DELETE CASCADE,
    pregunta_id     INTEGER NOT NULL,
    valor_escala    INTEGER,
    texto_respuesta TEXT,
    UNIQUE (proceso_id, pregunta_id)
);

ALTER TABLE nino_respuestas DISABLE ROW LEVEL SECURITY;
