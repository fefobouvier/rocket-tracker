import streamlit as st
import requests
from datetime import datetime, timedelta

# COORDINATES: Colonia del Sacramento
LAT, LON = -34.47, -57.84

st.set_page_config(page_title="Rocket Tracker", page_icon="🚀", layout="wide")

# --- MULTILINGUAL DICTIONARY ---
TEXTS = {
    "ES": {
        "title": "🚀 Predictor de Avistamientos de Cohetes",
        "monitoring": "Monitoreando cielos sobre: Colonia del Sacramento",
        "lang_label": "Seleccionar Idioma / Select Language",
        "match": "🎯 COINCIDENCIA",
        "twilight": "✨ CREPÚSCULO",
        "high_match_desc": "🎯 COINCIDENCIA: Sigue tus patrones históricos de avistamiento.",
        "low_match_desc": "🔭 Baja probabilidad de ver un 'jellyfish' (pluma iluminada).",
        "obs_window": "📅 Ventana de observación estimada:",
        "direction": "Dirección",
        "elevation": "Elevación",
        "movement": "Movimiento",
        "prime_viewing": "✨ VISIÓN ÓPTIMA: Pluma iluminada por el sol muy probable.",
        "midnight_glow": "🌙 BRILLO NOCTURNO: Posible brillo a gran altitud (etapa superior).",
        "check_horizon": "🌑 Revisar horizonte: Podría estar muy oscuro o iluminado.",
        "btn_details": "🌐 Ver detalles de la misión",
        "fetching_error": "No se pudieron obtener datos. Intenta refrescar en unos minutos.",
        "site_label": "Sitio de Lanzamiento",
        "sw_logic": "SUDOESTE (220°)",
        "n_logic": "NORTE (0°)",
        "move_n": "al NORTE",
        "move_ne": "al NORESTE"
    },
    "EN": {
        "title": "🚀 Rocket Sighting Predictor",
        "monitoring": "Monitoring skies over: Colonia del Sacramento",
        "lang_label": "Select Language",
        "match": "🎯 MATCH",
        "twilight": "✨ TWILIGHT",
        "high_match_desc": "🎯 MATCH: Matches your historical sighting patterns.",
        "low_match_desc": "🔭 Low probability for a sunlit 'jellyfish' plume.",
        "obs_window": "📅 Estimated Observation Window:",
        "direction": "Direction",
        "elevation": "Elevation",
        "movement": "Movement",
        "prime_viewing": "✨ PRIME VIEWING: Classic sunlit plume likely.",
        "midnight_glow": "🌙 MIDNIGHT GLOW: Possible high-altitude glow (upper stage).",
        "check_horizon": "🌑 Check Horizon: Might be too dark or too bright.",
        "btn_details": "🌐 View Mission Details",
        "fetching_error": "Unable to fetch launch data. Please refresh in a few minutes.",
        "site_label": "Launch Site",
        "sw_logic": "SOUTHWEST (220°)",
        "n_logic": "NORTH (0°)",
        "move_n": "NORTH",
        "move_ne": "NORTHEAST"
    }
}

# --- SIDEBAR LANGUAGE TOGGLE ---
st.sidebar.title("Settings / Ajustes")
lang_choice = st.sidebar.radio("Idioma / Language", ("Español", "English"))
L = TEXTS["ES"] if lang_choice == "Español" else TEXTS["EN"]

# --- STYLING ---
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { color: #1f1f1f !important; font-size: 1.6rem; }
    [data-testid="stMetricLabel"] { color: #4f4f4f !important; }
    .stMetric { background-color: #f0f2f6 !important; padding: 15px; border-radius: 10px; border: 1px solid #d1d1d1; }
    </style>
    """, unsafe_allow_html=True)

st.title(L["title"])
st.markdown(f"**{L['monitoring']}**")

# --- DATA FETCHING ---
def get_launches():
    try:
        url = "https://lldev.thespacedevs.com/2.2.0/launch/upcoming/?limit=10"
        return requests.get(url).json().get('results', [])
    except: return []

launches = get_launches()
if not launches: st.warning(L["fetching_error"])

for l in launches:
    name = l.get('name', 'Unknown')
    site = l.get('pad', {}).get('location', {}).get('name', 'Unknown Site')
    time_utc = datetime.strptime(l.get('net'), "%Y-%m-%dT%H:%M:%SZ")
    time_uyt = time_utc - timedelta(hours=3)
    
    is_chinese = any(w in site for w in ["Taiyuan", "Xichang", "Jiuquan"])
    is_usa = any(w in site for w in ["Florida", "Kennedy", "Cape Canaveral", "Vandenberg"])
    is_twilight = 18 <= time_uyt.hour <= 20
    is_midnight = 21 <= time_uyt.hour <= 23
    
    # Visual Badges
    label = ""
    if is_chinese or is_usa: label += f" {L['match']}"
    if is_twilight: label += f" {L['twilight']}"

    with st.expander(f"{time_uyt.strftime('%b %d - %H:%M')} | {name}{label}"):
        st.write(f"**{L['site_label']}:** {site}")
        
        if is_chinese or is_usa:
            st.success(L["high_match_desc"])
            
            # Pattern Geometry
            if is_chinese:
                obs_start, obs_end = time_uyt + timedelta(minutes=20), time_uyt + timedelta(minutes=50)
                look_dir, look_alt, move_to = L["sw_logic"], "15°-35°", L["move_n"]
            else:
                obs_start, obs_end = time_uyt + timedelta(hours=2), time_uyt + timedelta(hours=4)
                look_dir, look_alt, move_to = L["n_logic"], "20°-40°", L["move_ne"]

            st.info(f"{L['obs_window']} {obs_start.strftime('%H:%M')} — {obs_end.strftime('%H:%M')} UYT")
            
            c1, c2, c3 = st.columns(3)
            c1.metric(L["direction"], look_dir)
            c2.metric(L["elevation"], look_alt)
            c3.metric(L["movement"], move_to)

            if is_twilight: st.error(L["prime_viewing"])
            elif is_midnight: st.warning(L["midnight_glow"])
        else:
            st.write(L["low_match_desc"])

        st.link_button(L["btn_details"], "https://nextspaceflight.com/launches/")
