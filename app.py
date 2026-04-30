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
        "title": "🚀 Predictor de Cohetes Uruguay",
        "monitoring": "Ubicación:",
        "lang_label": "Idioma",
        "loc_label": "Departamento",
        "twilight": "✨ CREPÚSCULO",
        "obs_window": "📅 Ventana de observación:",
        "direction": "Dirección",
        "elevation": "Elevación",
        "movement": "Movimiento",
        "prime": "✨ PLUMA ILUMINADA PROBABLE",
        "details": "🌐 Detalles de misión",
        "sw": "SUDOESTE (220°)",
        "n": "NORTE (0°)",
        "m_n": "al NORTE",
        "m_ne": "al NORESTE",
        "err": "Error al obtener datos. Reintenta luego."
    },
    "EN": {
        "title": "🚀 Uruguay Rocket Tracker",
        "monitoring": "Location:",
        "lang_label": "Language",
        "loc_label": "Department",
        "twilight": "✨ TWILIGHT",
        "obs_window": "📅 Observation Window:",
        "direction": "Direction",
        "elevation": "Elevation",
        "movement": "Movement",
        "prime": "✨ SUNLIT PLUME LIKELY",
        "details": "🌐 Mission Details",
        "sw": "SOUTHWEST (220°)",
        "n": "NORTH (0°)",
        "m_n": "NORTH",
        "m_ne": "NORTHEAST",
        "err": "Unable to fetch data. Try again later."
    }
}

st.set_page_config(page_title="Rocket Tracker UY", page_icon="🚀", layout="wide")

# --- SIDEBAR ---
st.sidebar.header("Settings")
lang_choice = st.sidebar.radio("Idioma / Language", ("Español", "English"))
L = TEXTS["ES"] if lang_choice == "Español" else TEXTS["EN"]

selected_dept = st.sidebar.selectbox(L["loc_label"], list(DEPARTMENTS.keys()), index=0)
lat, lon = DEPARTMENTS[selected_dept]

# --- CSS DINÁMICO (Corrección de visibilidad) ---
st.markdown("""
    <style>
    /* Métricas generales */
    [data-testid="stMetricValue"] { color: #1f1f1f !important; font-size: 1.5rem; }
    .stMetric { background-color: #ffffff !important; padding: 10px; border-radius: 8px; border: 1px solid #eee; }
    
    /* FIX: Forzar texto oscuro en expanders MATCHES (Fondo Verde) */
    .element-container:has(div.match-box) + div div.stExpander p {
        color: #1a1a1a !important;
        font-weight: 600 !important;
    }
    
    .element-container:has(div.match-box) + div div.stExpander {
        background-color: #dcedc8 !important;
        border: 1px solid #c5e1a5 !important;
    }

    /* Ajuste de flecha para fondo verde */
    .element-container:has(div.match-box) + div div.stExpander svg {
        fill: #1a1a1a !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title(L["title"])
st.subheader(f"{L['monitoring']} {selected_dept}")

# --- LÓGICA DE DATOS ---
def get_data():
    try:
        # Usamos un User-Agent para evitar bloqueos de la API
        headers = {'User-Agent': 'UruguayRocketTracker/1.0'}
        response = requests.get("https://lldev.thespacedevs.com/2.2.0/launch/upcoming/?limit=10", headers=headers)
        return response.json().get('results', [])
    except:
        return []

launches = get_data()

if not launches:
    st.warning(L["err"])

for l in launches:
    name = l.get('name', 'Mission')
    site = l.get('pad', {}).get('location', {}).get('name', '')
    
    # Manejo de tiempo
    try:
        time_utc = datetime.strptime(l.get('net'), "%Y-%m-%dT%H:%M:%SZ")
        time_uyt = time_utc - timedelta(hours=3)
    except:
        continue
    
    # Clasificación de patrones
    is_chinese = any(w in site for w in ["Taiyuan", "Xichang", "Jiuquan"])
    is_usa = any(w in site for w in ["Florida", "Kennedy", "Cape Canaveral", "Vandenberg"])
    is_twilight = 18 <= time_uyt.hour <= 20
    is_match = is_chinese or is_usa

    # Marcador para el CSS
    if is_match:
        st.markdown('<div class="match-box"></div>', unsafe_allow_html=True)

    header_text = f"{time_uyt.strftime('%H:%M')} | {name}"
    if is_twilight:
        header_text += f" {L['twilight']}"

    with st.expander(header_text):
        st.write(f"**{site}**")
        
        if is_match:
            # Ventanas de tiempo basadas en tus avistamientos
            if is_chinese:
                t1, t2 = time_uyt + timedelta(minutes=20), time_uyt + timedelta(minutes=50)
                d, e, m = L["sw"], "15°-35°", L["m_n"]
            else:
                t1, t2 = time_uyt + timedelta(hours=2), time_uyt + timedelta(hours=4)
                d, e, m = L["n"], "20°-40°", L["m_ne"]

            st.info(f"{L['obs_window']} {t1.strftime('%H:%M')} — {t2.strftime('%H:%M')} UYT")
            
            c1, c2, c3 = st.columns(3)
            c1.metric(L["direction"], d)
            c2.metric(L["elevation"], e)
            c3.metric(L["movement"], m)
            
            if is_twilight:
                st.error(L["prime"])
        else:
            st.write("---")

        st.link_button(L["details"], "https://nextspaceflight.com/launches/")
