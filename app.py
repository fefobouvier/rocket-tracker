import streamlit as st
import requests
from datetime import datetime, timedelta
import math

# --- CONFIGURACIÓN FIJA ---
LOCATION_NAME = "Colonia del Sacramento"
LAT, LON = -34.47, -57.84

st.set_page_config(page_title="Rocket Tracker", page_icon="🚀", layout="wide")

# --- FUNCIONES DE APOYO ---
def es_crepusculo_real(fecha_uyt):
    """Calcula si la hora del lanzamiento cae en la ventana de crepúsculo en Colonia."""
    dia_del_año = fecha_uyt.timetuple().tm_yday
    # Curva para estimar la puesta del sol en Colonia del Sacramento
    # Invierno (junio) ~17:40, Verano (enero) ~20:10
    hora_puesta = 18.9 + 1.2 * math.cos(2 * math.pi * (dia_del_año + 10) / 365)
    
    # Ventana óptima: desde la puesta hasta 1.5 horas después
    inicio_ventana = hora_puesta
    fin_ventana = hora_puesta + 1.5
    
    hora_decimal = fecha_uyt.hour + fecha_uyt.minute / 60
    return inicio_ventana <= hora_decimal <= fin_ventana

def generar_ical(nombre, inicio, fin, descripcion):
    """Genera un string en formato iCalendar."""
    fmt = "%Y%m%dT%H%M%SZ"
    # Convertimos de UYT a UTC para el estándar iCal (UYT es UTC-3)
    inicio_utc = inicio + timedelta(hours=3)
    fin_utc = fin + timedelta(hours=3)
    
    ical = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Fefo Bouvier//Rocket Tracker//ES",
        "BEGIN:VEVENT",
        f"SUMMARY:🚀 Avistamiento: {nombre}",
        f"DTSTART:{inicio_utc.strftime(fmt)}",
        f"DTEND:{fin_utc.strftime(fmt)}",
        f"DESCRIPTION:{descripcion}",
        f"LOCATION:{LOCATION_NAME}",
        "END:VEVENT",
        "END:VCALENDAR"
    ]
    return "\n".join(ical)

# --- DICCIONARIO MULTILINGÜE ---
TEXTS = {
    "ES": {
        "title": "🚀 Lanzamientos de cohetes visibles desde Uruguay: horarios y predicción",
        "monitoring": f"Monitoreando: {LOCATION_NAME} ({LAT}, {LON})",
        "intro": "Esta app predice cuándo la **pluma de luz** de un cohete será visible desde Uruguay. Creado por **Fefo Bouvier**.",
        "web_link": "🌐 Visitar fefobouvier.com",
        "twilight": "✨ CREPÚSCULO",
        "high_match_desc": "🎯 Patrón histórico detectado para Uruguay.",
        "obs_window": "📅 Ventana de observación estimada:",
        "next_day_suffix": "(+1 día)",
        "direction": "Dirección",
        "elevation": "Elevación",
        "movement": "Movimiento",
        "prime_viewing": "✨ VISIÓN ÓPTIMA: Pluma iluminada por el sol (Efecto Jellyfish).",
        "btn_details": "🌐 Ver detalles de la misión",
        "btn_cal": "📅 Agregar al calendario",
        "fetching_error": "Error al obtener datos.",
        "site_label": "Sitio de Lanzamiento",
        "sw_logic": "SUDOESTE (220°)",
        "n_logic": "NORTE (0°)",
        "move_n": "al NORTE",
        "move_ne": "al NORESTE"
    },
    "EN": {
        "title": "🚀 Rocket launches visible from Uruguay: Timings & predictions",
        "monitoring": f"Monitoring: {LOCATION_NAME} ({LAT}, {LON})",
        "intro": "This app predicts rocket plume visibility from Uruguay. Created by Fefo Bouvier.",
        "web_link": "🌐 Visit fefobouvier.com",
        "twilight": "✨ TWILIGHT",
        "high_match_desc": "🎯 Historical sighting pattern detected.",
        "obs_window": "📅 Estimated Observation Window:",
        "next_day_suffix": "(+1 day)",
        "direction": "Direction",
        "elevation": "Elevation",
        "movement": "Movement",
        "prime_viewing": "✨ PRIME VIEWING: Sunlit plume (Jellyfish effect).",
        "btn_details": "🌐 View Mission Details",
        "btn_cal": "📅 Add to Calendar",
        "fetching_error": "Unable to fetch data.",
        "site_label": "Launch Site",
        "sw_logic": "SOUTHWEST (220°)",
        "n_logic": "NORTH (0°)",
        "move_n": "NORTH",
        "move_ne": "NORTHEAST"
    }
}

# --- BARRA LATERAL ---
st.sidebar.title("Settings")
lang_choice = st.sidebar.radio("Idioma / Language", ("Español", "English"))
L = TEXTS["ES"] if lang_choice == "Español" else TEXTS["EN"]

# --- STYLING (DISEÑO ORIGINAL OSCURO) ---
st.markdown(f"""
    <style>
    .location-text {{
        font-family: 'Source Code Pro', monospace;
        font-size: 0.9rem;
        color: #A0A0A0;
        margin-bottom: 20px;
    }}
    [data-testid="stMetricValue"] {{ color: #FFFFFF !important; font-size: 1.5rem !important; }}
    div[data-testid="stMetric"] {{
        background-color: #262730 !important;
        padding: 15px !important;
        border-radius: 10px !important;
        border: 1px solid #464855 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- ENCABEZADO ---
st.title(L["title"])
st.markdown(f'<p class="location-text">{L["monitoring"]}</p>', unsafe_allow_html=True)
st.write(L["intro"])
st.link_button(L["web_link"], "https://fefobouvier.com")
st.divider()

# --- DATA (PRÓXIMOS 30 PARA FILTRAR) ---
@st.cache_data(ttl=300)
def get_launches():
    try:
        url = "https://lldev.thespacedevs.com/2.2.0/launch/upcoming/?limit=30"
        return requests.get(url, timeout=10).json().get('results', [])
    except: return []

launches = get_launches()
if not launches: st.warning(L["fetching_error"])

for l in launches:
    site = l.get('pad', {}).get('location', {}).get('name', 'Unknown')
    
    # Filtro estricto: Solo China y Florida (Trayectorias confirmadas)
    is_chinese = any(w in site for w in ["Taiyuan", "Xichang", "Jiuquan", "Wenchang"])
    is_florida = any(w in site for w in ["Florida", "Kennedy", "Cape Canaveral"])
    
    if not (is_chinese or is_florida):
        continue

    name = l.get('name', 'Mission')
    mission_id = l.get('id', name)
    raw_time = l.get('net') or l.get('window_start')
    
    try:
        time_utc = datetime.strptime(raw_time, "%Y-%m-%dT%H:%M:%SZ")
        launch_uyt = time_utc - timedelta(hours=3)
    except: continue
    
    country_emoji = "🇺🇸" if is_florida else "🇨🇳"
    is_twilight = es_crepusculo_real(launch_uyt)
    label = f" {L['twilight']}" if is_twilight else ""

    with st.expander(f"{launch_uyt.strftime('%b %d | %H:%M')} - {country_emoji} {name}{label}"):
        st.write(f"**Hora de lanzamiento:** {launch_uyt.strftime('%H:%M')} UYT")
        st.write(f"**{L['site_label']}:** {site}")
        st.success(L["high_match_desc"])
        
        if is_chinese:
            t1, t2 = launch_uyt + timedelta(minutes=15), launch_uyt + timedelta(minutes=45)
            d, e, m = L["sw_logic"], "15°-35°", L["move_n"]
        else: # Florida
            t1, t2 = launch_uyt + timedelta(hours=1, minutes=45), launch_uyt + timedelta(hours=3, minutes=30)
            d, e, m = L["n_logic"], "20°-40°", L["move_ne"]

        suffix = f" {L['next_day_suffix']}" if (t1.date() > launch_uyt.date() or t2.date() > launch_uyt.date()) else ""
        st.info(f"{L['obs_window']} **{t1.strftime('%H:%M')} — {t2.strftime('%H:%M')}{suffix} UYT**")
        
        c1, c2, c3 = st.columns(3)
        c1.metric(L["direction"], d)
        c2.metric(L["elevation"], e)
        c3.metric(L["movement"], m)
        
        if is_twilight: st.error(L["prime_viewing"])

        # Generar iCal dinámico
        cal_desc = f"Direccion: {d}\\nElevacion: {e}\\nMovimiento: {m}\\n\\nPrediccion por fefobouvier.com"
        ical_data = generar_ical(name, t1, t2, cal_desc)

        # Botones de acción con keys únicas para evitar el error de duplicación
        col_a, col_b = st.columns(2)
        with col_a:
            st.link_button(L["btn_details"], f"https://nextspaceflight.com/launches/details/{mission_id}")
        with col_b:
            st.download_button(
                label=L["btn_cal"],
                data=ical_data,
                file_name=f"cohete_{launch_uyt.strftime('%Y%m%d')}.ics",
                mime="text/calendar",
                key=f"dl_{mission_id}"
            )
