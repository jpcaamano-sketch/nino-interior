from core.questions import (NECESIDAD_PREGUNTAS, ETAPA_PREGUNTAS,
                             NECESIDADES, ETAPAS, get_intensidad)


def calcular_puntajes_etapa(respuestas: dict) -> dict:
    """Promedio de las preguntas de escala por etapa. Rango 1-5."""
    scores = {}
    for etapa in ETAPAS:
        ids = etapa["preguntas_escala"]
        vals = [respuestas[i] for i in ids if i in respuestas and respuestas[i]]
        scores[etapa["id"]] = round(sum(vals) / len(vals), 2) if vals else 0.0
    return scores


def calcular_puntajes_necesidad(respuestas: dict) -> dict:
    """Promedio de las preguntas asociadas a cada necesidad. Rango 1-5."""
    scores = {}
    for nec, ids in NECESIDAD_PREGUNTAS.items():
        vals = [respuestas[i] for i in ids if i in respuestas and respuestas[i]]
        scores[nec] = round(sum(vals) / len(vals), 2) if vals else 0.0
    return scores


def determinar_etapa_dominante(scores_etapa: dict) -> tuple[str, str | None]:
    """Retorna (etapa_dominante, etapa_co_dominante | None)."""
    sorted_e = sorted(scores_etapa.items(), key=lambda x: x[1], reverse=True)
    dominante = sorted_e[0][0]
    co = sorted_e[1][0] if abs(sorted_e[0][1] - sorted_e[1][1]) <= 0.5 else None
    return dominante, co


def determinar_necesidad_dominante(scores_nec: dict) -> tuple[str, str]:
    """Retorna (necesidad_dominante, necesidad_secundaria)."""
    sorted_n = sorted(scores_nec.items(), key=lambda x: x[1], reverse=True)
    return sorted_n[0][0], sorted_n[1][0]


def get_etapa_info(etapa_id: str) -> dict:
    for e in ETAPAS:
        if e["id"] == etapa_id:
            return e
    return {}
