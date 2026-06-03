import io
import re
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                 HRFlowable, KeepTogether)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from core.questions import (NECESIDADES_INFO, ETAPAS, PREGUNTAS_ABIERTAS,
                             get_intensidad, IDS_ABIERTAS)

_gemini = None


def _get_gemini():
    global _gemini
    if _gemini is None:
        from google import genai
        from core.config import GOOGLE_API_KEY
        _gemini = genai.Client(api_key=GOOGLE_API_KEY)
    return _gemini


def _sanitize_json(text: str) -> str:
    result = []
    in_string = False
    escape_next = False
    for ch in text:
        if escape_next:
            result.append(ch); escape_next = False
        elif ch == '\\' and in_string:
            result.append(ch); escape_next = True
        elif ch == '"':
            in_string = not in_string; result.append(ch)
        elif in_string and ord(ch) < 0x20:
            if ch == '\n': result.append('\\n')
            elif ch == '\r': result.append('\\r')
            elif ch == '\t': result.append('\\t')
        else:
            result.append(ch)
    return ''.join(result)


def _get_etapa_info(etapa_id: str) -> dict:
    for e in ETAPAS:
        if e["id"] == etapa_id:
            return e
    return {}


# ─── Gemini ────────────────────────────────────────────────────────────────────

def generar_analisis(nombre: str, etapa_dominante: str, etapa_co: str | None,
                     necesidad_dominante: str, necesidad_secundaria: str,
                     intensidad: str, puntajes_etapas: dict,
                     puntajes_necesidades: dict, respuestas: dict) -> dict:

    etapa_info   = _get_etapa_info(etapa_dominante)
    nec_dom_info = NECESIDADES_INFO[necesidad_dominante]
    nec_sec_info = NECESIDADES_INFO[necesidad_secundaria]

    reflexiones = []
    for pid in IDS_ABIERTAS:
        texto = respuestas.get(pid)
        if texto and str(texto).strip():
            reflexiones.append(f"- {PREGUNTAS_ABIERTAS[pid]}\n  {texto}")

    etapas_texto = "\n".join(
        f"- {_get_etapa_info(e)['nombre']} ({_get_etapa_info(e)['rango']}): {s:.1f}/5"
        for e, s in sorted(puntajes_etapas.items(), key=lambda x: x[1], reverse=True)
    )
    nec_texto = "\n".join(
        f"- {NECESIDADES_INFO[n]['nombre']}: {s:.1f}/5"
        for n, s in sorted(puntajes_necesidades.items(), key=lambda x: x[1], reverse=True)
    )

    co_nota = (f"La etapa '{_get_etapa_info(etapa_co)['nombre']}' también tiene un puntaje muy similar — "
               f"ambas etapas son relevantes." if etapa_co else "")

    prompt = f"""Eres un guía experto en psicología del niño interior, integrando los marcos de John Bradshaw, Lise Bourbeau, Alejandro Jodorowsky y Alice Miller.
Genera el reporte personalizado de {nombre} basándote en su recorrido por las etapas de la infancia.

RESULTADO DEL DIAGNÓSTICO:
- Etapa de mayor sensibilidad: {etapa_info.get('nombre','')} ({etapa_info.get('rango','')}) — puntaje {puntajes_etapas.get(etapa_dominante,0):.1f}/5
- Intensidad: {intensidad}
- Necesidad más insatisfecha: {nec_dom_info['nombre']}
- Necesidad secundaria: {nec_sec_info['nombre']}
{co_nota}

PUNTAJES POR ETAPA (1=cubierta · 5=herida intensa):
{etapas_texto}

PUNTAJES POR NECESIDAD:
{nec_texto}

REFLEXIONES DE {nombre}:
{chr(10).join(reflexiones) if reflexiones else "No compartió reflexiones abiertas."}

Genera el análisis en JSON con este formato exacto:
{{
  "etapa_dominante": {{
    "descripcion": "3-4 líneas sobre qué ocurre emocionalmente en esta etapa del desarrollo. Lenguaje accesible.",
    "manifestaciones_adulto": [
      "Patrón específico de cómo aparece hoy en el adulto (una línea)",
      "Segundo patrón",
      "Tercer patrón"
    ]
  }},
  "necesidad_dominante": {{
    "como_aparece": "2-3 líneas sobre cómo esta necesidad insatisfecha se expresa hoy en la vida de {nombre}.",
    "que_busca": "Una frase sobre qué está buscando esa parte de {nombre} — con comprensión, sin juicio."
  }},
  "carta": {{
    "parrafo1": "Primer párrafo: saludo al niño interior con su nombre y la edad aproximada de la etapa dominante. Ver a ese niño, nombrarlo, decirle que lo ves. Cálido, directo.",
    "parrafo2": "Segundo párrafo: validar la estrategia de adaptación que usó. Explicar por qué hizo lo que hizo — no era su culpa, era lo que tenía.",
    "parrafo3": "Tercer párrafo: el mensaje que nunca llegó. Lo que ese niño necesitaba escuchar sobre la necesidad dominante. Sin condiciones, sin juicio.",
    "parrafo4": "Cuarto párrafo: la promesa del adulto de hoy. En primera persona. Qué va a hacer diferente. Cierre cálido."
  }},
  "practicas": [
    {{
      "nombre": "Nombre corto de la práctica",
      "instrucciones": "3-5 líneas con instrucciones claras y accesibles. Sin tecnicismos.",
      "frecuencia": "Ej: Diaria · 5 minutos"
    }},
    {{
      "nombre": "Segunda práctica",
      "instrucciones": "...",
      "frecuencia": "..."
    }},
    {{
      "nombre": "Tercera práctica",
      "instrucciones": "...",
      "frecuencia": "..."
    }}
  ],
  "sintesis_reflexiones": "Si hay reflexiones abiertas: un párrafo que las integre — qué patrones revelan, qué tiene coherencia con el diagnóstico. Si no hay reflexiones: una frase de invitación a la reflexión."
}}

Reglas:
- La carta: segunda persona para los párrafos 1, 2 y 3. Primera persona (el adulto habla al niño) para el párrafo 4.
- Las prácticas: específicas para la necesidad '{nec_dom_info['nombre']}', accesibles sin terapeuta.
- Lenguaje: cálido, cercano, no clínico, no determinista. Siempre apertura y posibilidad.
- Sin asteriscos ni markdown. Solo texto plano.
- Responde SOLO el JSON, sin texto adicional."""

    response = _get_gemini().models.generate_content(model="gemini-2.5-flash", contents=prompt)
    texto = response.text.strip()
    texto = re.sub(r"^```json\s*", "", texto)
    texto = re.sub(r"\s*```$", "", texto)
    texto = _sanitize_json(texto)
    return json.loads(texto)


# ─── Gráfico ───────────────────────────────────────────────────────────────────

def generar_grafico(puntajes_necesidades: dict, necesidad_dominante: str,
                    necesidad_secundaria: str) -> bytes:
    from core.questions import NECESIDADES_INFO
    sorted_n = sorted(puntajes_necesidades.items(), key=lambda x: x[1], reverse=True)
    nombres  = [NECESIDADES_INFO[n]["nombre"] for n, _ in sorted_n]
    valores  = [s for _, s in sorted_n]
    ids      = [n for n, _ in sorted_n]

    def bar_color(n):
        if n == necesidad_dominante:   return NECESIDADES_INFO[n]["color"]
        if n == necesidad_secundaria:  return "#8b7a5a"
        return "#2d2416"

    colores = [bar_color(n) for n in ids]

    fig, ax = plt.subplots(figsize=(10, 4.2))
    fig.patch.set_facecolor("#1a1208")
    ax.set_facecolor("#1a1208")

    bars = ax.barh(nombres, valores, color=colores, height=0.52, zorder=3)
    ax.set_xlim(0, 5.5)
    ax.axvline(x=5, color="#3d3020", linewidth=0.8, zorder=0)

    for bar, val in zip(bars, valores):
        if val > 0:
            ax.text(val + 0.08, bar.get_y() + bar.get_height() / 2,
                    f"{val:.1f}", va="center", ha="left",
                    color="#f5ecd7", fontsize=9, fontweight="bold")

    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_xticklabels(["1\nCubierta", "2", "3", "4", "5\nIntensa"],
                       color="#7a6a52", fontsize=7.5)
    ax.tick_params(axis="y", colors="#c4b090", labelsize=9)
    ax.spines[:].set_visible(False)
    ax.grid(axis="x", color="#251d10", linewidth=0.8, zorder=0)
    ax.set_title("Mapa de tus Necesidades del Niño Interior", color="#d4a853",
                 fontsize=11, fontweight="bold", pad=12)

    p = mpatches.Patch(color=NECESIDADES_INFO[necesidad_dominante]["color"], label="Necesidad dominante")
    s = mpatches.Patch(color="#8b7a5a", label="Necesidad secundaria")
    o = mpatches.Patch(color="#2d2416", label="Otras necesidades")
    ax.legend(handles=[p, s, o], loc="lower right", framealpha=0,
              labelcolor="#c4b090", fontsize=8)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor="#1a1208")
    buf.seek(0)
    img_bytes = buf.read()
    plt.close()
    return img_bytes


# ─── PDF ───────────────────────────────────────────────────────────────────────

def generar_pdf(nombre: str, etapa_dominante: str, etapa_co: str | None,
                necesidad_dominante: str, necesidad_secundaria: str,
                intensidad: str, puntajes_etapas: dict, puntajes_necesidades: dict,
                analisis: dict, grafico_bytes: bytes, respuestas: dict) -> bytes:

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles  = getSampleStyleSheet()
    gold    = colors.HexColor("#d4a853")
    amber   = colors.HexColor("#c97a5a")
    oscuro  = colors.HexColor("#1a1208")
    gris    = colors.HexColor("#5a4a32")
    muted   = colors.HexColor("#7a6a52")
    verde   = colors.HexColor("#7a9a6b")

    s_titulo = ParagraphStyle("titulo", parent=styles["Heading1"],
                               textColor=gold, fontSize=22, spaceAfter=4,
                               alignment=TA_CENTER, fontName="Helvetica-Bold")
    s_sub    = ParagraphStyle("sub", parent=styles["Normal"],
                               textColor=muted, fontSize=11, spaceAfter=16,
                               alignment=TA_CENTER)
    s_frase  = ParagraphStyle("frase", parent=styles["Normal"],
                               textColor=gold, fontSize=11, spaceAfter=8,
                               alignment=TA_CENTER, fontName="Helvetica-Oblique")
    s_h2     = ParagraphStyle("h2", parent=styles["Heading2"],
                               textColor=gold, fontSize=13,
                               spaceBefore=18, spaceAfter=8,
                               fontName="Helvetica-Bold")
    s_h3     = ParagraphStyle("h3", parent=styles["Heading3"],
                               textColor=amber, fontSize=11,
                               spaceBefore=12, spaceAfter=6,
                               fontName="Helvetica-Bold")
    s_body   = ParagraphStyle("body", parent=styles["Normal"],
                               fontSize=10, leading=16, spaceAfter=10,
                               textColor=colors.HexColor("#2d2010"),
                               alignment=TA_JUSTIFY)
    s_carta  = ParagraphStyle("carta", parent=styles["Normal"],
                               fontSize=10.5, leading=18, spaceAfter=14,
                               textColor=colors.HexColor("#1a1208"),
                               leftIndent=10, rightIndent=10,
                               alignment=TA_JUSTIFY)
    s_cita   = ParagraphStyle("cita", parent=styles["Normal"],
                               fontSize=10, leading=16, spaceAfter=10,
                               textColor=colors.HexColor("#3d3020"),
                               leftIndent=20, fontName="Helvetica-Oblique")
    s_label  = ParagraphStyle("label", parent=styles["Normal"],
                               fontSize=9, textColor=muted, spaceAfter=2)
    s_prac_n = ParagraphStyle("prac_n", parent=styles["Normal"],
                               fontSize=10, fontName="Helvetica-Bold",
                               textColor=amber, spaceAfter=4)
    s_prac_f = ParagraphStyle("prac_f", parent=styles["Normal"],
                               fontSize=9, textColor=muted,
                               spaceBefore=2, spaceAfter=8)

    from datetime import date
    story = []

    # Encabezado
    story.append(Paragraph("Mi Niño Interior", s_titulo))
    story.append(Paragraph(f"Reporte de {nombre}  ·  {date.today().strftime('%d/%m/%Y')}", s_sub))
    story.append(Paragraph(
        "<i>Lo que encontraste hoy no es una debilidad. Es el camino.</i>", s_frase))
    story.append(Spacer(1, 0.3*cm))

    # Gráfico
    graf_buf = io.BytesIO(grafico_bytes)
    img = Image(graf_buf, width=16*cm, height=7*cm)
    img.hAlign = "CENTER"
    story.append(img)
    story.append(Spacer(1, 0.3*cm))

    # Etapa dominante
    etapa_info = _get_etapa_info(etapa_dominante)
    _, intens_desc = get_intensidad(puntajes_etapas.get(etapa_dominante, 0))
    story.append(HRFlowable(width="100%", thickness=0.5, color=gold, spaceAfter=8))
    story.append(Paragraph(
        f"Tu etapa de mayor sensibilidad: {etapa_info.get('nombre','')} {etapa_info.get('icono','')} — {etapa_info.get('rango','')}",
        s_h2))
    story.append(Paragraph(f"<b>Intensidad:</b> {intensidad.upper()} — {intens_desc}", s_body))

    desc_etapa = analisis.get("etapa_dominante", {}).get("descripcion", "")
    if desc_etapa:
        story.append(Paragraph(desc_etapa, s_body))

    manifests = analisis.get("etapa_dominante", {}).get("manifestaciones_adulto", [])
    if manifests:
        story.append(Paragraph("<b>Cómo aparece hoy en tu vida:</b>", s_body))
        for m in manifests:
            story.append(Paragraph(f"• {m}", s_body))

    if etapa_co:
        etapa_co_info = _get_etapa_info(etapa_co)
        story.append(Paragraph(
            f"<i>La etapa {etapa_co_info.get('nombre','')} ({etapa_co_info.get('rango','')}) "
            f"también tiene una marca importante en tu historia.</i>", s_cita))

    # Necesidad dominante
    nec_info = NECESIDADES_INFO[necesidad_dominante]
    story.append(HRFlowable(width="100%", thickness=0.5, color=amber, spaceAfter=8))
    story.append(Paragraph(
        f"Tu necesidad más profunda: {nec_info['nombre']} {nec_info['icono']}", s_h2))
    story.append(Paragraph(nec_info["infancia"], s_body))

    como_aparece = analisis.get("necesidad_dominante", {}).get("como_aparece", "")
    if como_aparece:
        story.append(Paragraph(como_aparece, s_body))

    que_busca = analisis.get("necesidad_dominante", {}).get("que_busca", "")
    if que_busca:
        story.append(Paragraph(f"<i>{que_busca}</i>", s_cita))

    story.append(Paragraph(f"<b>Lo que tu niño interior sigue buscando:</b> {nec_info['mensaje']}", s_body))

    # La carta
    carta = analisis.get("carta", {})
    if carta:
        story.append(HRFlowable(width="100%", thickness=0.5, color=gold, spaceAfter=8))
        story.append(Paragraph("La Carta — de tu adulto a tu niño interior", s_h2))
        carta_items = [Spacer(1, 0.2*cm)]
        for key in ["parrafo1", "parrafo2", "parrafo3", "parrafo4"]:
            p = carta.get(key, "")
            if p:
                carta_items.append(Paragraph(p, s_carta))
        story.append(KeepTogether(carta_items))

    # Prácticas
    practicas = analisis.get("practicas", [])
    if practicas:
        story.append(HRFlowable(width="100%", thickness=0.5, color=gold, spaceAfter=8))
        story.append(Paragraph("Tus Prácticas de Sanación", s_h2))
        story.append(Paragraph(
            f"Estas prácticas están diseñadas para la necesidad de {nec_info['nombre']}. "
            f"Son accesibles y no requieren acompañamiento profesional para realizarlas.", s_body))
        for i, prac in enumerate(practicas[:3], 1):
            story.append(Paragraph(f"{i}. {prac.get('nombre','')}", s_prac_n))
            story.append(Paragraph(prac.get("instrucciones", ""), s_body))
            story.append(Paragraph(f"Frecuencia: {prac.get('frecuencia','')}", s_prac_f))

    # Reflexiones abiertas
    abiertas = [(pid, respuestas[pid]) for pid in IDS_ABIERTAS
                if pid in respuestas and str(respuestas.get(pid, "")).strip()]
    if abiertas:
        story.append(HRFlowable(width="100%", thickness=0.5, color=gold, spaceAfter=8))
        story.append(Paragraph("Lo que tú ya sabes", s_h2))
        sintesis = analisis.get("sintesis_reflexiones", "")
        if sintesis:
            story.append(Paragraph(sintesis, s_body))
        for pid, texto in abiertas:
            story.append(Paragraph(f"<i>{PREGUNTAS_ABIERTAS[pid]}</i>", s_label))
            story.append(Paragraph(str(texto), s_cita))

    # Cierre
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=muted, spaceAfter=12))
    story.append(Paragraph(
        "<i>Sanar no es olvidar lo que viviste. "
        "Es aprender a acompañarte como nadie pudo hacerlo entonces.</i>", s_frase))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "<i>Este viaje que acabas de hacer toma valor. Si quieres seguir explorando "
        "con acompañamiento, estoy aquí para caminar contigo. — Juan Pablo</i>", s_cita))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "<i>Esta herramienta es una experiencia de autoconocimiento. "
        "No es un diagnóstico clínico ni reemplaza la psicoterapia.</i>",
        ParagraphStyle("disclaimer", parent=styles["Normal"],
                       fontSize=8, textColor=muted, alignment=TA_CENTER)))

    doc.build(story)
    buf.seek(0)
    return buf.read()
