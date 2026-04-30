import streamlit as st
import requests
from datetime import datetime, timedelta

# YOUR COORDINATES (Colonia del Sacramento)
LAT, LON = -34.47, -57.84

st.set_page_config(page_title="Uruguay Rocket Tracker", page_icon="🚀")
st.title("🚀 Uruguay Rocket Sighting Predictor")
st.markdown(f"**Location:** Colonia del Sacramento ({LAT}, {LON})")

def get_launches():
    try:
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
    
    time_utc_str = l.get('net')
    if not time_utc_str: continue
        
    time_utc = datetime.strptime(time_utc_str, "%Y-%m-%dT%H:%M:%SZ")
    time_uyt = time_utc - timedelta(hours=3)
    
    # PATTERN CLASSIFICATION
    is_chinese = any(word in site for word in ["Taiyuan", "Xichang", "Jiuquan"])
    is_florida = "Florida" in site or "Kennedy" in site or "Cape Canaveral" in site
    is_vandenberg = "Vandenberg" in site

    with st.expander(f"{name} — {time_uyt.strftime('%b %d, %H:%M UYT')}"):
        st.write(f"**Launch Site:** {site}")
        
        # 1. TIME OF OBSERVATION LOGIC
        # Plumes usually appear 15-45 mins after launch for Chinese rockets, 
        # but 2+ hours later for high-orbit Florida missions (like today).
        if is_chinese:
            obs_start = time_uyt + timedelta(minutes=20)
            obs_end = time_uyt + timedelta(minutes=50)
            look_dir = "SOUTHWEST (220°)"
            look_alt = "15° - 35° (Low to Mid-horizon)"
            move_to = "NORTH"
        elif is_florida:
            # High-orbit missions (like Falcon Heavy) are often visible 2-4 hours later
            obs_start = time_uyt + timedelta(hours=2)
            obs_end = time_uyt + timedelta(hours=4)
            look_dir = "NORTH (0°)"
            look_alt = "20° - 40° (Mid-horizon)"
            move_to = "NORTHEAST"
        else:
            obs_start, obs_end = time_uyt, time_uyt + timedelta(minutes=30)
            look_dir, look_alt, move_to = "Unknown", "Unknown", "Unknown"

        # 2. VISIBILITY STATUS
        is_twilight = 18 <= time_uyt.hour <= 20
        is_midnight = 21 <= time_uyt.hour <= 23
        
        if is_chinese or is_florida:
            st.success("🎯 MATCH FOUND")
            st.info(f"📅 **Estimated Observation Window:** {obs_start.strftime('%H:%M')} — {obs_end.strftime('%H:%M')} UYT")
            
            # THE SMART COMPASS
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Initial Direction", look_dir)
            with col2:
                st.metric("Elevation", look_alt)
            
            st.write(f"➡️ **Movement:** Watch for it moving toward the **{move_to}**.")
            
            if is_twilight:
                st.error("✨ PRIME: Perfect Sunlit Plume conditions.")
            elif is_midnight:
                st.warning("🌙 LATE NIGHT: High-altitude glow possible (check for upper-stage burns).")
        else:
            st.write("🔭 Not a standard 'Uruguay Pattern' launch.")
