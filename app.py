"""Mi Niño Interior — Streamlit App"""
import re
import time
import streamlit as st

st.set_page_config(
    page_title="Mi Niño Interior",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbarActions"], [data-testid="stDeployButton"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }
header[data-testid="stHeader"] { background: transparent !important; border-bottom: none !important; box-shadow: none !important; }

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
  background: #4E32AD !important;
}
[data-testid="stAppViewContainer"] > .main { background: #4E32AD; }
[data-testid="stVerticalBlock"] { background: transparent !important; }
section[data-testid="stSidebar"] { display: none !important; }
.block-container { max-width: 700px; padding: 2rem 1.5rem; }

* { font-family: 'Inter', sans-serif !important; }
h1, h2, h3 { color: #DCFE77 !important; }
p, li { color: #F0ECFF !important; }

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
  background: rgba(255,255,255,.1) !important;
  color: #F0ECFF !important;
  border: 1px solid rgba(255,255,255,.2) !important;
  border-radius: 8px !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
  border-color: rgba(220,254,119,.5) !important;
  box-shadow: 0 0 0 2px rgba(220,254,119,.1) !important;
}

[data-testid="stRadio"] label { color: rgba(240,236,255,.8) !important; }
[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p { color: #F0ECFF !important; font-size: .97rem; }

[data-testid="stButton"] > button {
  background: #FF6B4E !important; color: #fff !important;
  border: none !important; border-radius: 8px !important;
  font-weight: 700 !important; font-size: 15px !important;
  padding: 12px 32px !important; width: 100% !important; transition: .2s !important;
}
[data-testid="stButton"] > button:hover { background: #ff8570 !important; transform: translateY(-1px) !important; }
[data-testid="stButton"] > button:disabled { background: #2B1D8A !important; color: rgba(240,236,255,.4) !important; }

.btn-secondary > button {
  background: transparent !important; color: rgba(240,236,255,.6) !important;
  border: 1px solid rgba(240,236,255,.25) !important;
}
.btn-secondary > button:hover { border-color: rgba(220,254,119,.5) !important; color: #DCFE77 !important; }

[data-testid="stDownloadButton"] > button {
  background: #2B1D8A !important; color: #DCFE77 !important;
  border: 1px solid rgba(220,254,119,.3) !important; border-radius: 8px !important; width: 100%;
}

[data-testid="stProgress"] > div { background: #2B1D8A !important; border-radius: 6px; }
[data-testid="stProgress"] > div > div { background: #FF6B4E !important; border-radius: 6px; }

hr { border-color: rgba(255,255,255,.1) !important; }
</style>
""", unsafe_allow_html=True)


# ─── Helpers ──────────────────────────────────────────────────────────────────
def ir_a(pagina: str):
    st.session_state.pagina = pagina
    st.rerun()


def gold(txt: str) -> str:
    return f'<span style="color:#DCFE77">{txt}</span>'


def muted(txt: str) -> str:
    return f'<span style="color:rgba(240,236,255,.65);font-size:.88rem">{txt}</span>'


def card(contenido: str, padding="28px", border_color="rgba(220,254,119,.15)"):
    st.markdown(
        f'<div style="background:#2B1D8A;border:1px solid {border_color};'
        f'border-radius:12px;padding:{padding};margin-bottom:16px;">{contenido}</div>',
        unsafe_allow_html=True)


def carta_visual(parrafos: list[str]):
    html = (
        '<div style="background:#faf6ee;border:1px solid rgba(212,168,83,.3);'
        'border-radius:8px;padding:32px 36px;font-family:Georgia,serif;'
        'color:#2d2010;line-height:1.95;">'
    )
    for p in parrafos:
        html += f'<p style="margin-bottom:18px">{p}</p>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# ─── Inicializar estado ────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "pagina": "inicio",
        "nombre": "",
        "correo": "",
        "proceso_id": None,
        "respuestas": {},
        "etapa_idx": 0,
        "q_idx": 0,
        "en_pausa": False,
        "analisis": None,
        "pdf_bytes": None,
        "grafico_bytes": None,
        "email_enviado": False,
        "resultado_id": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ─── Estructura del cuestionario ──────────────────────────────────────────────
from core.questions import ETAPAS, PREGUNTAS_ESCALA, PREGUNTAS_ABIERTAS, OPCIONES_ESCALA, PLACEHOLDERS_ABIERTOS

def get_preguntas_etapa(etapa_idx: int) -> list[dict]:
    """Retorna lista de preguntas para la etapa: [{tipo, id, texto, ...}]"""
    etapa = ETAPAS[etapa_idx]
    preguntas = []
    for pid in etapa["preguntas_escala"]:
        preguntas.append({"tipo": "escala", "id": pid, "texto": PREGUNTAS_ESCALA[pid]["texto"]})
    if "pregunta_abierta" in etapa:
        pid = etapa["pregunta_abierta"]
        preguntas.append({"tipo": "abierta", "id": pid, "texto": PREGUNTAS_ABIERTAS[pid]})
    elif "preguntas_abiertas" in etapa:
        for pid in etapa["preguntas_abiertas"]:
            preguntas.append({"tipo": "abierta", "id": pid, "texto": PREGUNTAS_ABIERTAS[pid]})
    return preguntas


def total_preguntas() -> int:
    return sum(len(get_preguntas_etapa(i)) for i in range(len(ETAPAS)))


def preguntas_respondidas() -> int:
    return len([v for v in st.session_state.respuestas.values() if v is not None])


# ─── Página: Inicio ───────────────────────────────────────────────────────────
def page_inicio():
    st.markdown(
        f'<h1 style="text-align:center;font-size:2.8rem;margin-bottom:.3rem">Mi Niño Interior</h1>',
        unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align:center;color:rgba(240,236,255,.7);'
        'font-style:italic;font-size:1.15rem;margin-bottom:2rem">'
        'Un viaje hacia la parte de ti que aún espera ser vista</p>',
        unsafe_allow_html=True)

    card(
        '<p style="color:rgba(240,236,255,.85);line-height:1.9;margin:0">'
        'En algún momento de tu infancia, una parte de ti aprendió a protegerse. '
        'Desarrolló estrategias para sobrevivir lo que sentía — y esas estrategias '
        'siguen activas hoy, aunque ya no las necesites de la misma manera.<br><br>'
        'Esta herramienta te ayuda a encontrar a ese niño o niña, entender qué necesitaba, '
        'y escribirle la carta que nunca llegó.</p>'
    )

    st.markdown(
        '<p style="color:rgba(240,236,255,.55);font-size:.82rem;text-align:center;margin-bottom:1.5rem">'
        '⏱ 10 a 15 minutos · Pago único vía Flow</p>',
        unsafe_allow_html=True)

    with st.form("form_inicio"):
        nombre = st.text_input("Tu nombre de pila", placeholder="Solo tu primer nombre",
                               value=st.session_state.nombre)
        correo = st.text_input("Tu correo", placeholder="Para recibir tu carta y reporte",
                               value=st.session_state.correo)
        st.markdown(
            '<p style="color:rgba(240,236,255,.5);font-size:.78rem;margin-top:8px">'
            '<b>Aviso:</b> Esta herramienta es una experiencia de autoconocimiento. '
            'No es un diagnóstico clínico ni reemplaza la psicoterapia. '
            'Si sientes angustia intensa durante o después, busca apoyo profesional.</p>',
            unsafe_allow_html=True)
        submitted = st.form_submit_button("Comenzar el viaje →")

    if submitted:
        nombre = nombre.strip()
        correo = correo.strip().lower()
        if not nombre:
            st.error("Ingresa tu nombre para comenzar.")
            return
        if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
            st.error("Ingresa un correo válido.")
            return
        st.session_state.nombre = nombre
        st.session_state.correo = correo
        ir_a("instrucciones")


# ─── Página: Instrucciones ────────────────────────────────────────────────────
def page_instrucciones():
    st.markdown(
        f'<h2 style="text-align:center">Antes de comenzar</h2>',
        unsafe_allow_html=True)
    st.markdown(f'<p style="text-align:center;color:#9a8872">Hola, {st.session_state.nombre}</p>',
                unsafe_allow_html=True)

    card(
        '<p style="color:#c4b090;line-height:1.95;margin:0">'
        'Vas a recorrer tres momentos de tu infancia y luego el presente.<br><br>'
        '<b style="color:#d4a853">No necesitas recordar eventos específicos.</b> '
        'Solo conectar con cómo te sentías — las sensaciones, las frecuencias, los patrones.<br><br>'
        'No hay respuestas correctas ni incorrectas. '
        'Responde desde lo primero que sientas, sin pensar demasiado.<br><br>'
        'Entre etapas habrá pequeñas pausas — son parte de la experiencia. No las saltes.</p>'
    )

    col1, col2 = st.columns([3, 2])
    with col1:
        if st.button("Estoy listo/a →"):
            ir_a("cuestionario")
    with col2:
        st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
        if st.button("← Volver"):
            ir_a("inicio")
        st.markdown('</div>', unsafe_allow_html=True)


# ─── Página: Cuestionario ─────────────────────────────────────────────────────
def page_cuestionario():
    from core.database import create_proceso, save_respuesta

    # Crear proceso en DB si aún no existe
    if not st.session_state.proceso_id:
        proceso = create_proceso(st.session_state.nombre, st.session_state.correo)
        st.session_state.proceso_id = proceso["id"]

    etapa_idx = st.session_state.etapa_idx
    q_idx     = st.session_state.q_idx

    # Si estamos en pausa entre etapas
    if st.session_state.en_pausa:
        etapa_anterior = ETAPAS[etapa_idx - 1] if etapa_idx > 0 else ETAPAS[0]
        pausa_texto = etapa_anterior.get("pausa", "")
        if pausa_texto:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                f'<div style="text-align:center;padding:48px 24px">'
                f'<p style="font-family:\'EB Garamond\',serif;font-style:italic;'
                f'font-size:1.35rem;color:#d4a853;line-height:1.8">'
                f'{pausa_texto.replace(chr(10), "<br>")}</p></div>',
                unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Continuar →"):
                st.session_state.en_pausa = False
                st.rerun()
        else:
            st.session_state.en_pausa = False
            st.rerun()
        return

    if etapa_idx >= len(ETAPAS):
        ir_a("transicion")
        return

    etapa     = ETAPAS[etapa_idx]
    preguntas = get_preguntas_etapa(etapa_idx)

    if q_idx >= len(preguntas):
        # Etapa completada — pausa si tiene
        if etapa.get("pausa"):
            st.session_state.etapa_idx += 1
            st.session_state.q_idx = 0
            st.session_state.en_pausa = True
            st.rerun()
        else:
            st.session_state.etapa_idx += 1
            st.session_state.q_idx = 0
            st.rerun()
        return

    pregunta = preguntas[q_idx]

    # Barra de progreso
    respondidas = preguntas_respondidas()
    total       = total_preguntas()
    progreso    = respondidas / total if total > 0 else 0
    st.progress(progreso)
    st.markdown(
        f'<p style="color:#6a5a3a;font-size:.8rem;text-align:right;margin-top:-8px">'
        f'{respondidas} / {total} preguntas</p>',
        unsafe_allow_html=True)

    # Encabezado de etapa
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">'
        f'<span style="font-size:1.4rem">{etapa["icono"]}</span>'
        f'<span style="font-family:\'EB Garamond\',serif;color:#d4a853;font-size:1.1rem">'
        f'{etapa["nombre"]}</span>'
        f'<span style="color:#6a5a3a;font-size:.82rem">· {etapa["rango"]}</span>'
        f'</div>',
        unsafe_allow_html=True)

    # Pregunta
    st.markdown(
        f'<p style="color:#f5ecd7;font-size:1.08rem;line-height:1.75;'
        f'margin:16px 0 20px">{pregunta["texto"]}</p>',
        unsafe_allow_html=True)

    respuesta_actual = st.session_state.respuestas.get(pregunta["id"])
    puede_avanzar = False

    if pregunta["tipo"] == "escala":
        opciones = list(OPCIONES_ESCALA.values())
        idx_actual = None
        if respuesta_actual is not None:
            try:
                idx_actual = list(OPCIONES_ESCALA.keys()).index(respuesta_actual)
            except ValueError:
                idx_actual = None

        seleccion = st.radio(
            "Selecciona una opción",
            options=opciones,
            index=idx_actual,
            label_visibility="collapsed",
        )

        if seleccion:
            valor = opciones.index(seleccion) + 1
            st.session_state.respuestas[pregunta["id"]] = valor
            puede_avanzar = True
            save_respuesta(st.session_state.proceso_id, pregunta["id"], valor_escala=valor)

    else:  # abierta
        placeholder = PLACEHOLDERS_ABIERTOS.get(pregunta["id"], "Escribe lo que llegue...")
        texto = st.text_area(
            "Tu respuesta",
            value=str(respuesta_actual) if respuesta_actual else "",
            placeholder=placeholder,
            label_visibility="collapsed",
        )
        st.markdown(
            '<p style="color:#6a5a3a;font-size:.8rem;margin-top:-8px">'
            'Opcional — puedes dejarlo en blanco si prefieres.</p>',
            unsafe_allow_html=True)
        if texto.strip():
            st.session_state.respuestas[pregunta["id"]] = texto.strip()
            save_respuesta(st.session_state.proceso_id, pregunta["id"], texto=texto.strip())
        puede_avanzar = True  # abiertas siempre permiten avanzar

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])

    with col2:
        if st.button("Siguiente →", disabled=not puede_avanzar):
            st.session_state.q_idx += 1
            st.rerun()

    with col1:
        st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
        if st.button("← Anterior"):
            if q_idx > 0:
                st.session_state.q_idx -= 1
            elif etapa_idx > 0:
                st.session_state.etapa_idx -= 1
                preguntas_ant = get_preguntas_etapa(etapa_idx - 1)
                st.session_state.q_idx = len(preguntas_ant) - 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ─── Página: Transición ───────────────────────────────────────────────────────
def page_transicion():
    from core.scoring import (calcular_puntajes_etapa, calcular_puntajes_necesidad,
                               determinar_etapa_dominante, determinar_necesidad_dominante)
    from core.report import generar_analisis, generar_grafico, generar_pdf
    from core.database import completar_proceso
    from core.questions import get_intensidad

    if st.session_state.analisis:
        ir_a("resultado")
        return

    st.markdown(
        '<div style="text-align:center;padding:80px 24px">'
        '<p style="font-family:\'EB Garamond\',serif;font-style:italic;'
        'font-size:1.5rem;color:#d4a853;line-height:1.8">'
        'Tu niño interior tiene algo que decirte...<br>'
        '<span style="font-size:1rem;color:#9a8872">Estamos preparando tu carta</span>'
        '</p></div>',
        unsafe_allow_html=True)

    with st.spinner(""):
        respuestas = st.session_state.respuestas
        scores_etapa = calcular_puntajes_etapa(respuestas)
        scores_nec   = calcular_puntajes_necesidad(respuestas)
        etapa_dom, etapa_co = determinar_etapa_dominante(scores_etapa)
        nec_dom, nec_sec    = determinar_necesidad_dominante(scores_nec)
        intensidad, _       = get_intensidad(scores_etapa[etapa_dom])

        analisis = generar_analisis(
            nombre=st.session_state.nombre,
            etapa_dominante=etapa_dom,
            etapa_co=etapa_co,
            necesidad_dominante=nec_dom,
            necesidad_secundaria=nec_sec,
            intensidad=intensidad,
            puntajes_etapas=scores_etapa,
            puntajes_necesidades=scores_nec,
            respuestas=respuestas,
        )

        grafico_bytes = generar_grafico(scores_nec, nec_dom, nec_sec)
        pdf_bytes = generar_pdf(
            nombre=st.session_state.nombre,
            etapa_dominante=etapa_dom,
            etapa_co=etapa_co,
            necesidad_dominante=nec_dom,
            necesidad_secundaria=nec_sec,
            intensidad=intensidad,
            puntajes_etapas=scores_etapa,
            puntajes_necesidades=scores_nec,
            analisis=analisis,
            grafico_bytes=grafico_bytes,
            respuestas=respuestas,
        )

        completar_proceso(
            proceso_id=st.session_state.proceso_id,
            etapa_dominante=etapa_dom,
            etapa_co_dominante=etapa_co,
            necesidad_dominante=nec_dom,
            necesidad_secundaria=nec_sec,
            intensidad=intensidad,
            puntajes_etapas=scores_etapa,
            puntajes_necesidades=scores_nec,
            analisis=analisis,
        )

        st.session_state.analisis        = analisis
        st.session_state.grafico_bytes   = grafico_bytes
        st.session_state.pdf_bytes       = pdf_bytes
        st.session_state.etapa_dominante = etapa_dom
        st.session_state.etapa_co        = etapa_co
        st.session_state.nec_dom         = nec_dom
        st.session_state.nec_sec         = nec_sec
        st.session_state.intensidad      = intensidad
        st.session_state.scores_etapa    = scores_etapa
        st.session_state.scores_nec      = scores_nec

    ir_a("resultado")


# ─── Página: Resultado ────────────────────────────────────────────────────────
def page_resultado():
    from core.questions import NECESIDADES_INFO, get_intensidad
    from core.email_service import enviar_reporte
    from core.config import BASE_URL

    nombre    = st.session_state.nombre
    analisis  = st.session_state.analisis
    etapa_dom = st.session_state.etapa_dom if hasattr(st.session_state, "etapa_dom") else st.session_state.get("etapa_dominante", "")
    etapa_co  = st.session_state.get("etapa_co")
    nec_dom   = st.session_state.get("nec_dom", "")
    nec_sec   = st.session_state.get("nec_sec", "")
    intensidad= st.session_state.get("intensidad", "")
    scores_etapa = st.session_state.get("scores_etapa", {})
    scores_nec   = st.session_state.get("scores_nec", {})
    grafico_bytes = st.session_state.grafico_bytes
    pdf_bytes     = st.session_state.pdf_bytes

    if not analisis:
        ir_a("inicio")
        return

    etapa_info   = next((e for e in ETAPAS if e["id"] == etapa_dom), {})
    nec_dom_info = NECESIDADES_INFO.get(nec_dom, {})
    nec_sec_info = NECESIDADES_INFO.get(nec_sec, {})
    _, intens_desc = get_intensidad(scores_etapa.get(etapa_dom, 0))

    st.markdown(
        f'<h1 style="text-align:center;font-size:2.2rem">Tu viaje, {nombre}</h1>',
        unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align:center;color:#9a8872;font-style:italic;font-family:\'EB Garamond\',serif">'
        'Lo que encontraste hoy no es una debilidad. Es el camino.</p>',
        unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Gráfico
    if grafico_bytes:
        st.image(grafico_bytes, use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Etapa dominante
    st.markdown(
        f'<h2>{etapa_info.get("icono","")} Tu etapa de mayor sensibilidad</h2>',
        unsafe_allow_html=True)
    card(
        f'<p style="color:#d4a853;font-size:1.05rem;margin-bottom:8px">'
        f'<b>{etapa_info.get("nombre","")} · {etapa_info.get("rango","")}</b></p>'
        f'<p style="color:#9a8872;font-size:.85rem;margin-bottom:12px">'
        f'Intensidad: <b>{intensidad.upper()}</b> — {intens_desc}</p>'
        f'<p style="color:#c4b090;line-height:1.85">'
        f'{analisis.get("etapa_dominante",{}).get("descripcion","")}</p>'
    )

    manifests = analisis.get("etapa_dominante", {}).get("manifestaciones_adulto", [])
    if manifests:
        st.markdown('<p style="color:#9a8872;font-size:.88rem">Cómo aparece hoy en tu vida:</p>',
                    unsafe_allow_html=True)
        for m in manifests:
            st.markdown(f'<p style="color:#c4b090;padding-left:16px">· {m}</p>',
                        unsafe_allow_html=True)

    # Necesidad dominante
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<h2>{nec_dom_info.get("icono","")} Tu necesidad más profunda</h2>',
        unsafe_allow_html=True)
    card(
        f'<p style="color:#d4a853;font-size:1.05rem;margin-bottom:8px">'
        f'<b>{nec_dom_info.get("nombre","")}</b></p>'
        f'<p style="color:#c4b090;line-height:1.85;margin-bottom:10px">'
        f'{nec_dom_info.get("infancia","")}</p>'
        f'<p style="color:#c4b090;line-height:1.85">'
        f'{analisis.get("necesidad_dominante",{}).get("como_aparece","")}</p>'
        f'<p style="color:#9a8872;font-style:italic;margin-top:10px">'
        f'"{analisis.get("necesidad_dominante",{}).get("que_busca","")}"</p>'
    )

    # La Carta
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<h2>✉️ La Carta</h2>', unsafe_allow_html=True)
    st.markdown(
        '<p style="color:#9a8872;font-size:.88rem;margin-bottom:16px">'
        'Escrita desde el adulto que eres hoy hacia el niño o niña que fuiste.</p>',
        unsafe_allow_html=True)
    carta = analisis.get("carta", {})
    parrafos = [carta.get(k, "") for k in ["parrafo1","parrafo2","parrafo3","parrafo4"] if carta.get(k)]
    if parrafos:
        carta_visual(parrafos)

    # Prácticas
    practicas = analisis.get("practicas", [])
    if practicas:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<h2>🌱 Tus Prácticas de Sanación</h2>', unsafe_allow_html=True)
        for i, prac in enumerate(practicas[:3], 1):
            card(
                f'<p style="color:#d4a853;font-weight:600;margin-bottom:6px">'
                f'{i}. {prac.get("nombre","")}</p>'
                f'<p style="color:#c4b090;line-height:1.85;margin-bottom:8px">'
                f'{prac.get("instrucciones","")}</p>'
                f'<p style="color:#6a5a3a;font-size:.82rem">'
                f'⏱ {prac.get("frecuencia","")}</p>'
            )

    # Reflexiones
    abiertas_resp = [(pid, st.session_state.respuestas.get(pid))
                     for pid in [101, 102, 103, 104, 105]
                     if st.session_state.respuestas.get(pid) and str(st.session_state.respuestas.get(pid)).strip()]
    if abiertas_resp:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<h2>🪞 Lo que tú ya sabes</h2>', unsafe_allow_html=True)
        sintesis = analisis.get("sintesis_reflexiones", "")
        if sintesis:
            st.markdown(
                f'<p style="color:#c4b090;font-style:italic;line-height:1.85;margin-bottom:16px">{sintesis}</p>',
                unsafe_allow_html=True)
        from core.questions import PREGUNTAS_ABIERTAS
        for pid, texto in abiertas_resp:
            st.markdown(
                f'<p style="color:#6a5a3a;font-size:.85rem;margin-bottom:4px">'
                f'{PREGUNTAS_ABIERTAS[pid]}</p>'
                f'<p style="color:#c4b090;font-style:italic;padding-left:14px;'
                f'border-left:2px solid rgba(212,168,83,.3);margin-bottom:16px">'
                f'{texto}</p>',
                unsafe_allow_html=True)

    # Cierre
    st.markdown("<br>", unsafe_allow_html=True)
    card(
        '<p style="color:#9a8872;font-style:italic;text-align:center;line-height:1.9">'
        'Este viaje que acabas de hacer toma valor. Si quieres seguir explorando '
        'con acompañamiento, estoy aquí para caminar contigo. — Juan Pablo</p>',
        border_color="rgba(212,168,83,.12)"
    )
    from core.config import AGENDA_URL
    st.markdown(
        f'<div style="text-align:center;margin-bottom:24px">'
        f'<a href="{AGENDA_URL}" target="_blank" style="color:#d4a853;font-size:.9rem">'
        f'Agendar una conversación →</a></div>',
        unsafe_allow_html=True)

    # Acciones
    st.markdown("<hr style='border-color:rgba(212,168,83,.15)'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📧 Recibir mi carta por correo",
                     disabled=st.session_state.email_enviado):
            with st.spinner("Enviando..."):
                link = f"{BASE_URL}/?resultado={st.session_state.proceso_id}"
                enviar_reporte(nombre, st.session_state.correo, link, pdf_bytes)
                st.session_state.email_enviado = True
            st.success(f"Enviado a {st.session_state.correo}")
            st.rerun()
        if st.session_state.email_enviado:
            st.markdown(
                f'<p style="color:#7a9a6b;font-size:.85rem;text-align:center">'
                f'✓ Enviado a {st.session_state.correo}</p>',
                unsafe_allow_html=True)

    with col2:
        if pdf_bytes:
            st.download_button(
                "⬇ Descargar PDF",
                data=pdf_bytes,
                file_name=f"nino_interior_{nombre.lower().replace(' ','_')}.pdf",
                mime="application/pdf",
            )

    st.markdown(
        '<p style="color:#4a3a22;font-size:.78rem;text-align:center;margin-top:24px">'
        'Esta herramienta es una experiencia de autoconocimiento. '
        'No es un diagnóstico clínico ni reemplaza la psicoterapia.</p>',
        unsafe_allow_html=True)


# ─── Página: Resultado desde DB ───────────────────────────────────────────────
def page_resultado_from_db(proceso_id: str):
    import json as _json
    from core.database import get_proceso, get_respuestas
    from core.report import generar_grafico, generar_pdf
    from core.questions import NECESIDADES_INFO, get_intensidad, ETAPAS

    if not re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", proceso_id.lower()):
        st.error("Enlace inválido.")
        return

    proceso = get_proceso(proceso_id)
    if not proceso or proceso.get("estado") != "completado":
        st.error("Reporte no encontrado o aún no completado.")
        return

    analisis = _json.loads(proceso["analisis"]) if isinstance(proceso["analisis"], str) else proceso["analisis"]
    scores_etapa = _json.loads(proceso["puntajes_etapas"]) if isinstance(proceso["puntajes_etapas"], str) else {}
    scores_nec   = _json.loads(proceso["puntajes_necesidades"]) if isinstance(proceso["puntajes_necesidades"], str) else {}
    respuestas   = get_respuestas(proceso_id)

    st.session_state.nombre        = proceso["nombre"]
    st.session_state.analisis      = analisis
    st.session_state.etapa_dominante = proceso["etapa_dominante"]
    st.session_state.etapa_co      = proceso.get("etapa_co_dominante")
    st.session_state.nec_dom       = proceso["necesidad_dominante"]
    st.session_state.nec_sec       = proceso["necesidad_secundaria"]
    st.session_state.intensidad    = proceso["intensidad"]
    st.session_state.scores_etapa  = scores_etapa
    st.session_state.scores_nec    = scores_nec
    st.session_state.respuestas    = respuestas
    st.session_state.email_enviado = True

    etapa_dom = proceso["etapa_dominante"]
    nec_dom   = proceso["necesidad_dominante"]
    nec_sec   = proceso["necesidad_secundaria"]

    grafico_bytes = generar_grafico(scores_nec, nec_dom, nec_sec)
    pdf_bytes     = generar_pdf(
        nombre=proceso["nombre"],
        etapa_dominante=etapa_dom,
        etapa_co=proceso.get("etapa_co_dominante"),
        necesidad_dominante=nec_dom,
        necesidad_secundaria=nec_sec,
        intensidad=proceso["intensidad"],
        puntajes_etapas=scores_etapa,
        puntajes_necesidades=scores_nec,
        analisis=analisis,
        grafico_bytes=grafico_bytes,
        respuestas=respuestas,
    )
    st.session_state.grafico_bytes = grafico_bytes
    st.session_state.pdf_bytes     = pdf_bytes
    st.session_state.proceso_id    = proceso_id

    page_resultado()


# ─── Router principal ─────────────────────────────────────────────────────────
def main():
    init_state()

    # Routing por parámetros URL
    params = st.query_params
    if "resultado" in params:
        page_resultado_from_db(params["resultado"])
        return

    pagina = st.session_state.pagina

    if pagina == "inicio":
        page_inicio()
    elif pagina == "instrucciones":
        page_instrucciones()
    elif pagina == "cuestionario":
        page_cuestionario()
    elif pagina == "transicion":
        page_transicion()
    elif pagina == "resultado":
        page_resultado()
    else:
        ir_a("inicio")


main()
