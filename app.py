import streamlit as st
import requests
from datetime import datetime, timedelta

# --- CONFIGURACIÓN FIJA ---
LOCATION_NAME = "Colonia del Sacramento"
# Coordenadas base para la lógica de la app
LAT, LON = -34.47, -57.84

st.set_page_config(page_title="Rastreador de Plumas UY", page_icon="🚀", layout="wide")

# --- DICCIONARIO MULTILINGÜE ---
TEXTS = {
    "ES": {
        "title": "🚀 Rastreador de Plumas UY",
        "monitoring": f"Monitoreando cielos sobre: {LOCATION_NAME}",
        "intro": """
        Esta app nació de mi hábito de observar el cielo y de los reportes constantes que recibo de personas que me siguen en redes sociales. 
        El objetivo es predecir cuándo la **pluma de luz** (o 'jellyfish') de un cohete será visible desde Uruguay. 
        Creado por **Fefo Bouvier**.
        """,
        "web_link": "🌐 Visitar fefobouvier.com",
        "timezone_notice": "⚠️ *Horarios sincronizados con la Hora Oficial de Uruguay (UYT).* ",
        "match": "🎯 COINCIDENCIA",
        "twilight": "✨ CREPÚSCULO",
        "high_match_desc": "🎯 COINCIDENCIA: Patrón histórico detectado para Uruguay.",
        "low_match_desc": "🔭 Baja probabilidad de ver pluma iluminada.",
        "obs_window": "📅 Ventana de avistamiento de la pluma:",
        "direction": "Dirección",
        "elevation": "Elevación",
        "movement": "Movimiento",
        "prime_viewing": "✨ VISIÓN ÓPTIMA: Pluma iluminada por el sol (Efecto Jellyfish).",
        "btn_details": "🌐 Datos técnicos del lanzamiento",
        "fetching_error": "Error al conectar con la base de datos de lanzamientos.",
        "site_label": "Sitio de Lanzamiento",
        "sw_logic": "SUDOESTE (220°)",
        "n_logic": "NORTE (0°)",
        "move_n": "Hacia el NORTE",
        "move_ne": "Hacia el NORESTE"
    },
    "EN": {
        "title": "🚀 Plume Tracker UY",
        "monitoring": f"Monitoring skies over: {LOCATION_NAME}",
        "intro": """
        This app was born from my habit of skywatching and the constant reports I receive from my followers. 
        The goal is to predict when a rocket's **light plume** (or 'jellyfish') will be visible from Uruguay. 
        Created by **Fefo Bouvier**.
        """,
        "web_link": "🌐 Visit fefobouvier.com",
        "timezone_notice": "⚠️ *All times are synced with Uruguay Standard Time (UYT).* ",
        "match": "🎯 MATCH",
        "twilight": "✨ TWILIGHT",
        "high_match_desc": "🎯 MATCH: Historical sighting pattern detected.",
        "low_match_desc": "🔭 Low probability for a sunlit plume.",
        "obs_window": "📅 Plume sighting window:",
        "direction": "Direction",
        "elevation": "Elevation",
        "movement": "Movement",
        "prime_viewing": "✨ PRIME VIEWING: Sunlit plume (Jellyfish effect).",
        "btn_details": "🌐 Launch Technical Data",
        "fetching_error": "Unable to connect to the launch database.",
        "site_label": "Launch Site",
        "sw_logic": "SOUTHWEST (220°)",
        "n_logic": "NORTH (0°)",
        "move_n": "Moving NORTH",
        "move_ne": "Moving NORTHEAST"
    }
}

# --- BARRA LATERAL ---
st.sidebar.title("Configuración")
lang_choice = st.sidebar.radio("Language / Idioma", ("Español", "English"))
L = TEXTS["ES"] if lang_choice == "Español" else TEXTS["EN"]

# --- ESTILOS (MANTENIENDO TU CONFIGURACIÓN DE CONTRASTE) ---
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { 
        color: #FFFFFF !important; 
        font-size: 1.5rem !important; 
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] { 
        color: #E0E0E0 !important; 
    }
    div[data-testid="stMetric"] {
        background-color: #262730 !important;
        padding: 15px !important;
        border-radius: 10px !important;
        border: 1px solid #464855 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ENCABEZADO ---
st.title(L["title"])
st.subheader(L["monitoring"])
st.write(L["intro"])
st.link_button(L["web_link"], "https://fefobouvier.com")
st.divider()
st.info(L["timezone_notice"])

# --- OBTENCIÓN DE DATOS ---
def get_launches():
    try:
        url = "https://lldev.thespacedevs.com/2.2.0/launch/upcoming/?limit=10"
        return requests.get(url, timeout=10).json().get('results', [])
    except: return []

launches = get_launches()
if not launches: st.warning(L["fetching_error"])

# --- LISTADO DE LANZAMIENTOS ---
for l in launches:
    name = l.get('name', 'Mission')
    site = l.get('pad', {}).get('location', {}).get('name', 'Unknown')
    
    # Lógica de tiempo precisa (NET)
    raw_time = l.get('net') or l.get('window_start')
    if not raw_time: continue
    
    try:
        time_utc = datetime.strptime(raw_time, "%Y-%m-%dT%H:%M:%SZ")
        time_uyt = time_utc - timedelta(hours=3)
    except: continue
    
    is_chinese = any(w in site for w in ["Taiyuan", "Xichang", "Jiuquan"])
    is_usa = any(w in site for w in ["Florida", "Kennedy", "Cape Canaveral", "Vandenberg"])
    is_twilight = 18 <= time_uyt.hour <= 20
    is_match = is_chinese or is_usa

    label = ""
    if is_match: label += f" {L['match']}"
    if is_twilight: label += f" {L['twilight']}"

    with st.expander(f"{time_uyt.strftime('%b %d | %H:%M')} - {name}{label}"):
        st.write(f"**Hora de lanzamiento:** {time_uyt.strftime('%H:%M')} UYT")
        st.write(f"**{L['site_label']}:** {site}")
        
        if is_match:
            st.success(L["high_match_desc"])
            
            if is_chinese:
                t1, t2 = time_uyt + timedelta(minutes=15), time_uyt + timedelta(minutes=45)
                d, e, m = L["sw_logic"], "15°-35°", L["move_n"]
            else:
                t1, t2 = time_uyt + timedelta(hours=1, minutes=45), time_uyt + timedelta(hours=3, minutes=30)
                d, e, m = L["n_logic"], "20°-40°", L["move_ne"]

            st.info(f"{L['obs_window']} **{t1.strftime('%H:%M')} — {t2.strftime('%H:%M')} UYT**")
            
            c1, c2, c3 = st.columns(3)
            c1.metric(L["direction"], d)
            c2.metric(L["elevation"], e)
            c3.metric(L["movement"], m)

            if is_twilight: st.error(L["prime_viewing"])
        else:
            st.write(L["low_match_desc"])

        st.link_button(L["btn_details"], f"https://nextspaceflight.com/launches/details/{l.get('id')}")
