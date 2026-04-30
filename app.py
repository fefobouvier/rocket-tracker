import streamlit as st
import requests
from datetime import datetime, timedelta

# COORDINATES: Colonia del Sacramento
LAT, LON = -34.47, -57.84

st.set_page_config(page_title="Uruguay Rocket Tracker", page_icon="🚀", layout="wide")

# CSS to fix the "White on White" text and force visibility
st.markdown("""
    <style>
    [data-testid="stMetricValue"] {
        color: #1f1f1f !important;
        font-size: 1.8rem;
    }
    [data-testid="stMetricLabel"] {
        color: #4f4f4f !important;
    }
    .stMetric {
        background-color: #f0f2f6 !important;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #d1d1d1;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 Uruguay Rocket Sighting Predictor")
st.markdown(f"**Monitoring Skies over:** Colonia del Sacramento")

def get_launches():
    try:
        url = "https://lldev.thespacedevs.com/2.2.0/launch/upcoming/?limit=10"
        data = requests.get(url).json()
        return data.get('results', [])
    except:
        return []

launches = get_launches()

if not launches:
    st.warning("Unable to fetch launch data. Please refresh in a few minutes.")

for l in launches:
    name = l.get('name', 'Unknown Mission')
    pad = l.get('pad', {})
    location = pad.get('location', {})
    site = location.get('name', 'Unknown Site')
    
    # Reliable URL Fallback
    official_url = "https://nextspaceflight.com/launches/"
    
    time_utc_str = l.get('net')
    if not time_utc_str: continue
        
    time_utc = datetime.strptime(time_utc_str, "%Y-%m-%dT%H:%M:%SZ")
    time_uyt = time_utc - timedelta(hours=3)
    
    # PATTERN CLASSIFICATION
    is_chinese = any(word in site for word in ["Taiyuan", "Xichang", "Jiuquan"])
    is_florida = any(word in site for word in ["Florida", "Kennedy", "Cape Canaveral"])
    is_vandenberg = "Vandenberg" in site
    
    is_twilight = 18 <= time_uyt.hour <= 20
    is_high_interest = is_chinese or is_florida or is_vandenberg

    label = ""
    if is_high_interest: label += " 🎯 MATCH"
    if is_twilight: label += " ✨ TWILIGHT"

    with st.expander(f"{time_uyt.strftime('%b %d - %H:%M')} | {name}{label}"):
        st.write(f"**Launch Site:** {site}")
        
        if is_high_interest:
            st.success("🎯 MATCH: Matches your historical sighting patterns.")
            
            if is_chinese:
                obs_start, obs_end = time_uyt + timedelta(minutes=20), time_uyt + timedelta(minutes=50)
                look_dir, look_alt, move_to = "SOUTHWEST", "15°-35°", "NORTH"
            else:
                # Florida/Vandenberg logic
                obs_start, obs_end = time_uyt + timedelta(hours=2), time_uyt + timedelta(hours=4)
                look_dir, look_alt, move_to = "NORTH", "20°-40°", "NORTHEAST"

            st.info(f"📅 **Observation Window:** {obs_start.strftime('%H:%M')} — {obs_end.strftime('%H:%M')} UYT")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Direction", look_dir)
            c2.metric("Elevation", look_alt)
            c3.metric("Movement", move_to)

            if is_twilight:
                st.error("✨ PRIME VIEWING: Classic sunlit plume likely.")
        else:
            st.write("🔭 Low probability for a sunlit plume.")

        st.link_button("🌐 Open Mission Details", official_url)
