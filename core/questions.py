# ─── Las 5 Necesidades Esenciales ─────────────────────────────────────────────
NECESIDADES = ["seguridad", "reconocimiento", "amor", "autonomia", "pertenencia"]

NECESIDADES_INFO = {
    "seguridad": {
        "nombre": "Seguridad",
        "icono": "🛡️",
        "color": "#6b8fa3",
        "descripcion": "Necesidad de sentirse protegido, estable y a salvo en el mundo.",
        "infancia": "El niño necesita saber que el mundo es un lugar seguro y que hay adultos confiables cerca.",
        "hoy": "Aparece hoy como desconfianza, hipervigilancia, dificultad para relajarse o soltar el control.",
        "mensaje": "Mereces un mundo que no te lastime. Y aunque no siempre fue así, puedes crear ese espacio ahora.",
    },
    "reconocimiento": {
        "nombre": "Reconocimiento",
        "icono": "✨",
        "color": "#c9a040",
        "descripcion": "Necesidad de ser visto, valorado y reconocido por lo que uno es y hace.",
        "infancia": "El niño necesita que sus logros, esfuerzos y emociones sean notados y validados.",
        "hoy": "Aparece hoy como búsqueda de aprobación, sobreachievement o dificultad para recibir elogios.",
        "mensaje": "Ya eras suficiente antes de lograr nada. Tu valor no dependía de lo que hicieras.",
    },
    "amor": {
        "nombre": "Amor Incondicional",
        "icono": "💛",
        "color": "#c97a5a",
        "descripcion": "Necesidad de ser amado sin condiciones, sin tener que ganarse ese amor.",
        "infancia": "El niño necesita saber que será amado aunque falle, aunque sea diferente, aunque decepcione.",
        "hoy": "Aparece hoy como miedo al abandono, relaciones codependientes o dificultad para pedir lo que necesitas.",
        "mensaje": "Eras digno de amor exactamente como eras. Sin tener que cambiar nada.",
    },
    "autonomia": {
        "nombre": "Autonomía",
        "icono": "🌿",
        "color": "#7a9a6b",
        "descripcion": "Necesidad de tener voz, agencia y que la propia voluntad sea respetada.",
        "infancia": "El niño necesita que sus decisiones sean escuchadas y que tenga espacio para desarrollar su propia identidad.",
        "hoy": "Aparece hoy como dificultad para tomar decisiones, sometimiento a otros o rebeldía excesiva.",
        "mensaje": "Tu voz importaba entonces. Y sigue importando ahora.",
    },
    "pertenencia": {
        "nombre": "Pertenencia",
        "icono": "🤝",
        "color": "#8b6ba3",
        "descripcion": "Necesidad de sentirse parte de algo — una familia, un grupo, un lugar.",
        "infancia": "El niño necesita sentir que encaja, que no está solo y que hay un lugar para él en el mundo.",
        "hoy": "Aparece hoy como soledad crónica, dificultad para conectar profundamente o sensación de ser un extraño.",
        "mensaje": "Siempre hubo un lugar para ti. Aunque nadie te lo haya mostrado con claridad.",
    },
}

# ─── Etapas ────────────────────────────────────────────────────────────────────
ETAPAS = [
    {
        "id": "infancia",
        "nombre": "El niño pequeño",
        "rango": "0 a 6 años",
        "icono": "🌱",
        "color": "#6b8fa3",
        "pausa": "Antes de continuar... respira.\nAcabas de visitar una parte muy temprana de ti.",
        "preguntas_escala": [1, 2, 3, 4],
        "pregunta_abierta": 101,
    },
    {
        "id": "ninez",
        "nombre": "El niño que descubre el mundo",
        "rango": "7 a 12 años",
        "icono": "🌿",
        "color": "#7a9a6b",
        "pausa": "Este niño o niña de tu pasado hizo lo mejor que pudo con lo que tenía.\nHonra eso.",
        "preguntas_escala": [5, 6, 7, 8],
        "pregunta_abierta": 102,
    },
    {
        "id": "adolescencia",
        "nombre": "El adolescente que busca su lugar",
        "rango": "13 a 17 años",
        "icono": "🌾",
        "color": "#c9a040",
        "pausa": "Ese adolescente sobrevivió. Y llegó hasta aquí.\nEso es suficiente.",
        "preguntas_escala": [9, 10, 11, 12],
        "pregunta_abierta": 103,
    },
    {
        "id": "presente",
        "nombre": "El presente",
        "rango": "Hoy",
        "icono": "✨",
        "color": "#c97a5a",
        "pausa": None,
        "preguntas_escala": [13, 14, 15],
        "preguntas_abiertas": [104, 105],
    },
]

# ─── Preguntas de escala ───────────────────────────────────────────────────────
# Formuladas para que 1=casi nunca (poca herida) y 5=siempre (herida intensa)
# La necesidad asociada es INTERNA — el usuario nunca la ve

PREGUNTAS_ESCALA = {
    # Etapa 1 — Infancia (0-6)
    1: {
        "texto": "Me costaba sentirme tranquilo/a o en calma, aunque estuviera en casa.",
        "necesidad": "seguridad",
        "etapa": "infancia",
    },
    2: {
        "texto": "Sentía que mis emociones o esfuerzos pasaban desapercibidos para quienes me cuidaban.",
        "necesidad": "reconocimiento",
        "etapa": "infancia",
    },
    3: {
        "texto": "Echaba de menos más contacto, cercanía o cariño de mis figuras de cuidado.",
        "necesidad": "amor",
        "etapa": "infancia",
    },
    4: {
        "texto": "Me sentía diferente o fuera de lugar dentro de mi familia.",
        "necesidad": "pertenencia",
        "etapa": "infancia",
    },
    # Etapa 2 — Niñez (7-12)
    5: {
        "texto": "Hacía cosas especiales para que me notaran o para llamar la atención.",
        "necesidad": "reconocimiento",
        "etapa": "ninez",
    },
    6: {
        "texto": "Me preguntaba si era suficientemente bueno/a para merecer el cariño que recibía.",
        "necesidad": "amor",
        "etapa": "ninez",
    },
    7: {
        "texto": "Sentía que mis opiniones, ideas o deseos no contaban o no importaban.",
        "necesidad": "autonomia",
        "etapa": "ninez",
    },
    8: {
        "texto": "Me costaba sentirme parte del grupo — ya sea en casa o entre amigos.",
        "necesidad": "pertenencia",
        "etapa": "ninez",
    },
    # Etapa 3 — Adolescencia (13-17)
    9: {
        "texto": "Tenía que seguir las reglas o expectativas de otros aunque no estuviera de acuerdo.",
        "necesidad": "autonomia",
        "etapa": "adolescencia",
    },
    10: {
        "texto": "Necesitaba la aprobación de otros para sentirme bien conmigo mismo/a.",
        "necesidad": "reconocimiento",
        "etapa": "adolescencia",
    },
    11: {
        "texto": "Me sentía incomprendido/a o solo/a, incluso estando rodeado/a de personas.",
        "necesidad": "pertenencia",
        "etapa": "adolescencia",
    },
    12: {
        "texto": "Vivía con la sensación de que algo podía salir mal o que el mundo no era un lugar seguro.",
        "necesidad": "seguridad",
        "etapa": "adolescencia",
    },
    # El presente
    13: {
        "texto": "Necesito que otros validen lo que hago para sentir que vale la pena.",
        "necesidad": "reconocimiento",
        "etapa": "presente",
    },
    14: {
        "texto": "Me cuesta confiar plenamente en las personas cercanas, aunque no haya razones concretas.",
        "necesidad": "seguridad",
        "etapa": "presente",
    },
    15: {
        "texto": "Dudo de si merezco ser amado/a tal como soy, sin necesitar cambiar nada.",
        "necesidad": "amor",
        "etapa": "presente",
    },
}

# ─── Preguntas abiertas ────────────────────────────────────────────────────────
PREGUNTAS_ABIERTAS = {
    101: "Si pudieras ver a ese niño o niña pequeño/a, ¿qué imagen o sensación aparece?",
    102: "¿Hay algún momento de esa época que recuerdes con tristeza o con nostalgia?",
    103: "¿Qué parte de ese adolescente crees que aún vive en ti hoy?",
    104: "¿En qué situaciones actuales sientes que tu niño interior aparece con más fuerza?",
    105: "¿Qué le dirías hoy a ese niño o niña que fuiste, si pudieras encontrarte con él o ella?",
}

PLACEHOLDERS_ABIERTOS = {
    101: "No necesitas recordar nada específico. Escribe lo que llegue...",
    102: "Puede ser una imagen, una sensación, un momento...",
    103: "No hay respuesta correcta. Solo lo que sientes...",
    104: "Cuando me siento..., cuando alguien..., en momentos de...",
    105: "Puedes empezar con: 'Quería decirte que...'",
}

# ─── Opciones de escala ────────────────────────────────────────────────────────
OPCIONES_ESCALA = {
    1: "Casi nunca",
    2: "Pocas veces",
    3: "A veces",
    4: "Frecuentemente",
    5: "Siempre o casi siempre",
}

# ─── Niveles de intensidad ─────────────────────────────────────────────────────
def get_intensidad(promedio: float) -> tuple[str, str]:
    if promedio <= 2.0:
        return "leve", "Las marcas de esta etapa son suaves. Con pequeños gestos puedes seguir sanando."
    elif promedio <= 3.0:
        return "moderado", "Hay algo que aún pide atención en esta etapa. El reconocerlo ya es un primer paso."
    elif promedio <= 4.0:
        return "intenso", "Esta etapa guardó heridas significativas. Merece ser mirada con cuidado y compasión."
    else:
        return "profundo", "Esta parte de ti cargó mucho. Hay una profundidad de dolor que merece ser acompañada."

# ─── Mapeo necesidades por etapa ──────────────────────────────────────────────
NECESIDAD_PREGUNTAS = {
    "seguridad":      [1, 12, 14],
    "reconocimiento": [2, 5, 10, 13],
    "amor":           [3, 6, 15],
    "autonomia":      [7, 9],
    "pertenencia":    [4, 8, 11],
}

ETAPA_PREGUNTAS = {
    "infancia":    [1, 2, 3, 4],
    "ninez":       [5, 6, 7, 8],
    "adolescencia":[9, 10, 11, 12],
    "presente":    [13, 14, 15],
}

IDS_ABIERTAS = [101, 102, 103, 104, 105]
