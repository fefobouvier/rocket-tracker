import streamlit as st
import requests
from datetime import datetime, timedelta

# YOUR COORDINATES (Colonia del Sacramento)
LAT, LON = -34.47, -57.84

st.set_page_config(page_title="Uruguay Rocket Tracker", page_icon="🚀", layout="wide")

# Custom CSS to make the matches stand out more
st.markdown("""
    <style>
    .match-badge {
        background-color: #ff4b4b;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: bold;
        margin-left: 10px;
    }
    .twilight-badge {
        background-color: #fca311;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: bold;
        margin-left: 10px;
    }
    </style>
    """, unsafe_with_stdio=True)

st.title("🚀 Uruguay Rocket Sighting Predictor")
st.markdown(f"**Monitoring Skies over:** Colonia del Sacramento ({LAT}, {LON})")

def get_launches():
    try:
        # Fetching upcoming missions
        url = "https://lldev.thespacedevs.com/2.2.0/launch/upcoming/?limit=10"
        data = requests.get(url).json()
        return data.get('results', [])
    except:
        return []

launches = get_launches()

for l in launches:
    name = l.get('name', 'Unknown Mission')
    pad = l.get('pad', {})
    location = pad.get('location', {})
    site = location.get('name', 'Unknown Site')
    
    # Official URL for "More Info"
    official_url = f"https://www.rocketlaunch.live/launch/{l.get('slug', '')}" if l.get('slug') else "https://nextspaceflight.com/launches/"
    
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

    # CREATE VISUAL LABELS FOR THE HEADER
    label = ""
    if is_high_interest:
        label += " 🎯 HIGH MATCH"
    if is_twilight:
        label += " ✨ TWILIGHT"

    # THE EXPANDER (Now with labels in the title)
    with st.expander(f"{time_uyt.strftime('%b %d - %H:%M')} | {name}{label}"):
        st.write(f"**Launch Site:** {site}")
        
        if is_high_interest:
            st.success("🎯 MATCH: This mission follows your historical sighting patterns.")
            
            # Observations Windows
            if is_chinese:
                obs_start, obs_end = time_uyt + timedelta(minutes=20), time_uyt + timedelta(minutes=50)
                look_dir, look_alt, move_to = "SOUTHWEST (220°)", "15° - 35°", "NORTH"
            else:
                obs_start, obs_end = time_uyt + timedelta(hours=2), time_uyt + timedelta(hours=4)
                look_dir, look_alt, move_to = "NORTH (0°)", "20° - 40°", "NORTHEAST"

            st.info(f"📅 **Estimated Observation Window:** {obs_start.strftime('%H:%M')} — {obs_end.strftime('%H:%M')} UYT")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Direction", look_dir)
            c2.metric("Elevation", look_alt)
            c3.metric("Movement", move_to)

            if is_twilight:
                st.error("✨ PRIME VIEWING: Classic 'Jellyfish' plume likely.")
        else:
            st.write("🔭 General Launch: Low probability for a 'jellyfish' plume.")

        # LINK TO OFFICIAL DATA
        st.link_button("🌐 View Official Mission Data", official_url)
