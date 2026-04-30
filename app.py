import streamlit as st
import requests
from datetime import datetime, timedelta

# --- CONFIGURACIÓN DE DEPARTAMENTOS ---
DEPARTMENTS = {
    "Montevideo": (-34.9011, -56.1645),
    "Artigas": (-30.4000, -56.4667),
    "Canelones": (-34.5228, -56.2778),
    "Cerro Largo": (-32.3717, -54.1833),
    "Colonia": (-34.4714, -57.8442),
    "Durazno": (-33.3794, -56.5228),
    "Flores": (-33.5333, -56.9000),
    "Florida": (-34.1000, -56.2167),
    "Lavalleja": (-34.3758, -54.9469),
    "Maldonado": (-34.9000, -54.9500),
    "Paysandú": (-32.3167, -58.0833),
    "Río Negro": (-33.1333, -58.3000),
    "Rivera": (-30.9053, -55.5508),
    "Rocha": (-34.4833, -54.3333),
    "Salto": (-31.3833, -57.9667),
    "San José": (-34.3375, -56.7136),
    "Soriano": (-33.2522, -58.0306),
    "Tacuarembó": (-31.7125, -55.9811),
    "Treinta y Tres": (-33.2333, -54.3833)
}

TEXTS = {
    "ES": {
        "title": "🚀 Predictor de Avistamientos de Cohetes",
        "intro": """
        Esta app nació de mi hábito de observar el cielo y de los reportes constantes que recibo de personas que me siguen en redes sociales. 
        El objetivo es predecir cuándo un lanzamiento será visible desde Uruguay (especialmente las famosas 'plumas' de luz). 
        Creado por **Fefo Bouvier**.
        """,
        "web_link": "🌐 Visitar mi web",
        "monitoring": "Ubicación seleccionada:",
        "timezone_notice": "⚠️ *Todos los horarios están expresados en la hora oficial de Uruguay (UYT).* ",
        "lang_label": "Idioma",
        "loc_label": "Departamento",
        "match": "🎯 COINCIDENCIA",
        "twilight": "✨ CREPÚSCULO",
        "launch_time": "⏰ Hora exacta de lanzamiento:",
        "high_match_desc": "🎯 COINCIDENCIA: Sigue tus patrones históricos de avistamiento.",
        "low_match_desc": "🔭 Baja probabilidad de ver un 'jellyfish' (pluma iluminada).",
        "obs_window": "📅 Ventana de observación estimada:",
        "direction": "Dirección",
        "elevation": "Elevación",
        "movement": "Movimiento",
        "prime_viewing": "✨ VISIÓN ÓPTIMA: Pluma iluminada por el sol muy probable.",
        "midnight_glow": "🌙 BRILLO NOCTURNO: Posible brillo a gran altitud.",
        "btn_details": "🌐 Ver detalles de la misión",
        "fetching_error": "No se pudieron obtener datos. Intenta refrescar luego.",
        "site_label": "Sitio de Lanzamiento",
        "sw_logic": "SUDOESTE (220°)",
        "n_logic": "NORTE (0°)",
        "move_n": "al NORTE",
        "move_ne": "al NORESTE"
    },
    "EN": {
        "title": "🚀 Rocket Sighting Predictor",
        "intro": """
        This app was born from my habit of skywatching and the constant reports I receive from my followers on social media. 
        The goal is to predict when a launch will be visible from Uruguay (especially the famous light plumes). 
        Created by **Fefo Bouvier**.
        """,
        "web_link": "🌐 Visit my website",
        "monitoring": "Selected Location:",
        "timezone_notice": "⚠️ *All times are expressed in Uruguay Standard Time (UYT).* ",
        "lang_label": "Language",
        "loc_label": "Department",
        "match": "🎯 MATCH",
        "twilight": "✨ TWILIGHT",
        "launch_time": "⏰ Exact launch time:",
        "high_match_desc": "🎯 MATCH: Matches your historical sighting patterns.",
        "low_match_desc": "🔭 Low probability for a sunlit 'jellyfish' plume.",
        "obs_window": "📅 Estimated Observation Window:",
        "direction": "Direction",
        "elevation": "Elevation",
        "movement": "Movement",
        "prime_viewing": "✨ PRIME VIEWING: Classic sunlit plume likely.",
        "midnight_glow": "🌙 MIDNIGHT GLOW: Possible high-altitude glow.",
        "btn_details": "🌐 View Mission Details",
        "fetching_error": "Unable to fetch launch data. Please refresh later.",
        "site_label": "Launch Site",
        "sw_logic": "SOUTHWEST (220°)",
        "n_logic": "NORTH (0°)",
        "move_n": "NORTH",
        "move_ne": "NORTHEAST"
    }
}

st.set_page_config(page_title="Rocket Tracker UY", page_icon="🚀", layout="wide")

# --- SIDEBAR ---
st.sidebar.title("Settings / Ajustes")
lang_choice = st.sidebar.radio("Idioma / Language", ("Español", "English"))
L = TEXTS["ES"] if lang_choice == "Español" else TEXTS["EN"]

selected_dept = st.sidebar.selectbox(L["loc_label"], list(DEPARTMENTS.keys()), index=0)
lat, lon = DEPARTMENTS[selected_dept]

# --- STYLING ---
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { color: #1f1f1f !important; font-size: 1.5rem; }
    [data-testid="stMetricLabel"] { color: #4f4f4f !important; }
    .stMetric { background-color: #f0f2f6 !important; padding: 10px; border-radius: 8px; border: 1px solid #d1d1d1; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER & INTRO ---
st.title(L["title"])
st.write(L["intro"])
st.link_button(L["web_link"], "https://fefobouvier.com")
st.divider()
st.subheader(f"{L['monitoring']} {selected_dept}")
st.info(L["timezone_notice"])

# --- DATA FETCHING ---
def get_launches():
    try:
        url = "https://lldev.thespacedevs.com/2.2.0/launch/upcoming/?limit=10"
        return requests.get(url).json().get('results', [])
    except: return []

launches = get_launches()
if not launches: st.warning(L["fetching_error"])

for l in launches:
    name = l.get('name', 'Mission')
    site = l.get('pad', {}).get('location', {}).get('name', 'Unknown')
    
    try:
        time_utc = datetime.strptime(l.get('net'), "%Y-%m-%dT%H:%M:%SZ")
        time_uyt = time_utc - timedelta(hours=3)
    except: continue
    
    is_chinese = any(w in site for w in ["Taiyuan", "Xichang", "Jiuquan"])
    is_usa = any(w in site for w in ["Florida", "Kennedy", "Cape Canaveral", "Vandenberg"])
    is_twilight = 18 <= time_uyt.hour <= 20
    is_midnight = 21 <= time_uyt.hour <= 23
    
    # Visual Badges
    label = ""
    if is_chinese or is_usa: label += f" {L['match']}"
    if is_twilight: label += f" {L['twilight']}"

    with st.expander(f"{time_uyt.strftime('%b %d - %H:%M')} | {name}{label}"):
        st.write(f"**{L['launch_time']}** {time_uyt.strftime('%H:%M')} UYT")
        st.write(f"**{L['site_label']}:** {site}")
        
        if is_chinese or is_usa:
            st.success(L["high_match_desc"])
            
            if is_chinese:
                t1, t2 = time_uyt + timedelta(minutes=20), time_uyt + timedelta(minutes=50)
                d, e, m = L["sw_logic"], "15°-35°", L["move_n"]
            else:
                t1, t2 = time_uyt + timedelta(hours=2), time_uyt + timedelta(hours=4)
                d, e, m = L["n_logic"], "20°-40°", L["move_ne"]

            st.info(f"{L['obs_window']} {t1.strftime('%H:%M')} — {t2.strftime('%H:%M')} UYT")
            
            c1, c2, c3 = st.columns(3)
            c1.metric(L["direction"], d)
            c2.metric(L["elevation"], e)
            c3.metric(L["movement"], m)

            if is_twilight: st.error(L["prime_viewing"])
            elif is_midnight: st.warning(L["midnight_glow"])
        else:
            st.write(L["low_match_desc"])

        st.link_button(L["btn_details"], "https://nextspaceflight.com/launches/")
