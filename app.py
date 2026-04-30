import streamlit as st
import requests
from datetime import datetime, timedelta
import time

# --- CONFIGURACIÓN DE DEPARTAMENTOS ---
DEPARTMENTS = {
    "Montevideo": (-34.9011, -56.1645), "Artigas": (-30.4000, -56.4667),
    "Canelones": (-34.5228, -56.2778), "Cerro Largo": (-32.3717, -54.1833),
    "Colonia": (-34.4714, -57.8442), "Durazno": (-33.3794, -56.5228),
    "Flores": (-33.5333, -56.9000), "Florida": (-34.1000, -56.2167),
    "Lavalleja": (-34.3758, -54.9469), "Maldonado": (-34.9000, -54.9500),
    "Paysandú": (-32.3167, -58.0833), "Río Negro": (-33.1333, -58.3000),
    "Rivera": (-30.9053, -55.5508), "Rocha": (-34.4833, -54.3333),
    "Salto": (-31.3833, -57.9667), "San José": (-34.3375, -56.7136),
    "Soriano": (-33.2522, -58.0306), "Tacuarembó": (-31.7125, -55.9811),
    "Treinta y Tres": (-33.2333, -54.3833)
}

TEXTS = {
    "ES": {
        "title": "🚀 Rastreador de Plumas UY",
        "web_link": "🌐 Visitar fefobouvier.com",
        "timezone_notice": "⚠️ *Horarios sincronizados con la Hora Oficial de Uruguay (UYT).* ",
        "next_probable": "⏱️ PRÓXIMO AVISTAMIENTO PROBABLE",
        "countdown_msg": "Faltan:",
        "go_to_details": "Ver detalles y trayectoria ↓",
        "loc_label": "Departamento",
        "match": "🎯 COINCIDENCIA",
        "twilight": "✨ CREPÚSCULO",
        "launch_time": "⏰ Hora de lanzamiento (T-0):",
        "obs_window": "📅 Ventana de avistamiento de la pluma:",
        "direction": "Dirección", "elevation": "Elevación", "movement": "Movimiento",
        "prime_viewing": "✨ VISIÓN ÓPTIMA: Pluma iluminada por el sol.",
        "btn_details": "🌐 Datos técnicos del lanzamiento"
    },
    "EN": {
        "title": "🚀 Plume Tracker UY",
        "web_link": "🌐 Visit fefobouvier.com",
        "timezone_notice": "⚠️ *All times are synced with Uruguay Standard Time (UYT).* ",
        "next_probable": "⏱️ NEXT PROBABLE SIGHTING",
        "countdown_msg": "Time left:",
        "go_to_details": "View details and path ↓",
        "loc_label": "Department",
        "match": "🎯 MATCH",
        "twilight": "✨ TWILIGHT",
        "launch_time": "⏰ Launch time (T-0):",
        "obs_window": "📅 Plume sighting window:",
        "direction": "Direction", "elevation": "Elevation", "movement": "Movement",
        "prime_viewing": "✨ PRIME VIEWING: Sunlit plume likely.",
        "btn_details": "🌐 Launch Technical Data"
    }
}

st.set_page_config(page_title="Rastreador de Plumas UY", page_icon="🚀", layout="wide")

# --- ESTADO DE SESIÓN PARA EXPANDERS ---
if "expanded_id" not in st.session_state:
    st.session_state.expanded_id = None

# --- SIDEBAR ---
st.sidebar.title("Configuración")
lang_choice = st.sidebar.radio("Language / Idioma", ("Español", "English"))
L = TEXTS["ES"] if lang_choice == "Español" else TEXTS["EN"]
selected_dept = st.sidebar.selectbox(L["loc_label"], list(DEPARTMENTS.keys()), index=0)

# --- STYLING ---
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { color: #FFFFFF !important; font-size: 1.5rem !important; }
    div[data-testid="stMetric"] { background-color: #262730 !important; padding: 15px !important; border-radius: 10px !important; }
    .countdown-box { background-color: #1E1E1E; padding: 20px; border-radius: 12px; border: 2px solid #FF4B4B; text-align: center; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)

# --- DATA FETCHING ---
@st.cache_data(ttl=300)
def get_launches():
    try:
        url = "https://lldev.thespacedevs.com/2.2.0/launch/upcoming/?limit=10"
        return requests.get(url, timeout=10).json().get('results', [])
    except: return []

launches = get_launches()

# --- LÓGICA DE PRÓXIMO AVISTAMIENTO ---
upcoming_matches = []
now = datetime.utcnow()

for l in launches:
    site = l.get('pad', {}).get('location', {}).get('name', '')
    is_match = any(w in site for w in ["Taiyuan", "Xichang", "Jiuquan", "Florida", "Kennedy", "Cape Canaveral", "Vandenberg"])
    raw_time = l.get('net')
    if is_match and raw_time:
        t_utc = datetime.strptime(raw_time, "%Y-%m-%dT%H:%M:%SZ")
        if t_utc > now:
            upcoming_matches.append((t_utc, l))

# --- HEADER ---
st.title(L["title"])
st.link_button(L["web_link"], "https://fefobouvier.com")
st.info(L["timezone_notice"])

# --- CAJA DE COUNTDOWN ---
if upcoming_matches:
    next_time, next_launch = upcoming_matches[0]
    diff = next_time - datetime.utcnow()
    
    with st.container():
        st.markdown(f'<div class="countdown-box">', unsafe_allow_html=True)
        st.subheader(L["next_probable"])
        
        # Countdown dinámico (Streamlit refresca cada segundo con este truco simple)
        placeholder = st.empty()
        
        hours, remainder = divmod(int(diff.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        placeholder.markdown(f"### {L['countdown_msg']} {hours:02d}h {minutes:02d}m {seconds:02d}s")
        
        if st.button(L["go_to_details"], key="btn_scroll"):
            st.session_state.expanded_id = next_launch['id']
            # JS para scroll suave al elemento
            st.components.v1.html(f"""
                <script>
                window.parent.document.getElementById('{next_launch['id']}').scrollIntoView({{behavior: 'smooth'}});
                </script>
            """, height=0)
        st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# --- LISTA DE LANZAMIENTOS ---
for l in launches:
    l_id = l.get('id')
    name = l.get('name', 'Mission')
    site = l.get('pad', {}).get('location', {}).get('name', 'Unknown')
    raw_time = l.get('net')
    
    try:
        time_uyt = datetime.strptime(raw_time, "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=3)
    except: continue
    
    is_match = any(w in site for w in ["Taiyuan", "Xichang", "Jiuquan", "Florida", "Kennedy", "Cape Canaveral", "Vandenberg"])
    is_twilight = 18 <= time_uyt.hour <= 20
    
    label = f" {L['match']}" if is_match else ""
    if is_twilight: label += f" {L['twilight']}"

    # Ancla HTML para el scroll
    st.markdown(f"<div id='{l_id}'></div>", unsafe_allow_html=True)
    
    # El expander se abre si el ID coincide con el del countdown
    is_expanded = st.session_state.expanded_id == l_id
    
    with st.expander(f"{time_uyt.strftime('%b %d | %H:%M')} - {name}{label}", expanded=is_expanded):
        st.write(f"**{L['launch_time']}** {time_uyt.strftime('%H:%M')} UYT")
        st.write(f"**Sitio:** {site}")
        
        if is_match:
            # Ventana estimada
            t1 = time_uyt + (timedelta(minutes=15) if "China" in site else timedelta(hours=1, minutes=45))
            t2 = time_uyt + (timedelta(minutes=45) if "China" in site else timedelta(hours=3, minutes=30))
            
            st.info(f"{L['obs_window']} **{t1.strftime('%H:%M')} — {t2.strftime('%H:%M')} UYT**")
            
            c1, c2, c3 = st.columns(3)
            c1.metric(L["direction"], "NORTE" if "USA" in site else "SUDOESTE")
            c2.metric(L["elevation"], "20°-40°")
            c3.metric(L["movement"], "NORESTE" if "USA" in site else "NORTE")
            
            if is_twilight: st.error(L["prime_viewing"])

        st.link_button(L["btn_details"], f"https://nextspaceflight.com/launches/details/{l_id}")
