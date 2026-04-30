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
        "title": "🚀 Rastreador de Plumas UY",
        "intro": """
        Esta app nació de mi hábito de observar el cielo y de los reportes constantes que recibo de personas que me siguen en redes sociales. 
        El objetivo es predecir cuándo la **pluma de luz** (o 'jellyfish') de un cohete será visible desde Uruguay. 
        Creado por **Fefo Bouvier**.
        """,
        "web_link": "🌐 Visitar fefobouvier.com",
        "monitoring": "Ubicación de observación:",
        "timezone_notice": "⚠️ *Horarios sincronizados con la Hora Oficial de Uruguay (UYT).* ",
        "lang_label": "Idioma",
        "loc_label": "Departamento",
        "match": "🎯 COINCIDENCIA",
        "twilight": "✨ CREPÚSCULO",
        "launch_time": "⏰ Hora de lanzamiento (T-0):",
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
        "intro": """
        This app was born from my habit of skywatching and the constant reports I receive from my followers. 
        The goal is to predict when a rocket's **light plume** (or 'jellyfish') will be visible from Uruguay. 
        Created by **Fefo Bouvier**.
        """,
        "web_link": "🌐 Visit fefobouvier.com",
        "monitoring": "Observation Location:",
        "timezone_notice": "⚠️ *All times are synced with Uruguay Standard Time (UYT).* ",
        "lang_label": "Language",
        "loc_label": "Department",
        "match": "🎯 MATCH",
        "twilight": "✨ TWILIGHT",
        "launch_time": "⏰ Launch time (T-0):",
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

st.set_page_config(page_title="Rastreador de Plumas UY", page_icon="🚀", layout="wide")

# --- SIDEBAR ---
st.sidebar.title("Configuración")
lang_choice = st.sidebar.radio("Language / Idioma", ("Español", "English"))
L = TEXTS["ES"] if lang_choice == "Español" else TEXTS["EN"]

selected_dept = st.sidebar.selectbox(L["loc_label"], list(DEPARTMENTS.keys()), index=0)
lat, lon = DEPARTMENTS[selected_dept]

# --- STYLING (FIXED CONTRAST) ---
st.markdown("""
    <style>
    /* Estilo para los valores de las métricas (Dirección, Elevación, Movimiento) */
    [data-testid="stMetricValue"] { 
        color: #FFFFFF !important; 
        font-size: 1.5rem !important; 
        font-weight: 700 !important;
    }
    /* Estilo para las etiquetas de las métricas */
    [data-testid="stMetricLabel"] { 
        color: #E0E0E0 !important; 
    }
    /* Contenedor de la métrica: Fondo oscuro para asegurar visibilidad del texto blanco */
    div[data-testid="stMetric"] {
        background-color: #262730 !important;
        padding: 15px !important;
        border-radius: 10px !important;
        border: 1px solid #464855 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER ---
st.title(L["title"])
st.write(L["intro"])
st.link_button(L["web_link"], "https://fefobouvier.com")
st.divider()
st.subheader(f"{L['monitoring']} {selected_dept}")
st.info(L["timezone_notice"])

# --- DATA ---
def get_launches():
    try:
        url = "https://lldev.thespacedevs.com/2.2.0/launch/upcoming/?limit=10"
        return requests.get(url, timeout=10).json().get('results', [])
    except: return []

launches = get_launches()
if not launches: st.warning(L["fetching_error"])

for l in launches:
    name = l.get('name', 'Mission')
    site = l.get('pad', {}).get('location', {}).get('name', 'Unknown')
    
    # Priorizar hora NET para evitar el error de ventana de las 23:00
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
        st.write(f"**{L['launch_time']}** {time_uyt.strftime('%H:%M')} UYT")
        st.write(f"**{L['site_label']}:** {site}")
        
        if is_match:
            st.success(L["high_match_desc"])
            
            if is_chinese:
                t1, t2 = time_uyt + timedelta(minutes=15), time_uyt + timedelta(minutes=45)
                d, e, m = L["sw_logic"], "15°-35°", L["move_n"]
            else:
                # Ventana para Florida: la pluma aparece tiempo después del despegue
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
