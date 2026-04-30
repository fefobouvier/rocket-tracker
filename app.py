import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd

# YOUR COORDINATES (Colonia del Sacramento)
LAT, LON = -34.47, -57.84

st.set_page_config(page_title="Uruguay Rocket Tracker", page_icon="🚀")
st.title("🚀 Uruguay Rocket Sighting Predictor")
st.markdown(f"**Location:** Colonia del Sacramento ({LAT}, {LON})")

def get_launches():
    # Fetching the next 10 global launches
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
    if not time_utc_str:
        continue
        
    time_utc = datetime.strptime(time_utc_str, "%Y-%m-%dT%H:%M:%SZ")
    time_uyt = time_utc - timedelta(hours=3) # Convert to Uruguay Time
    
    # CHECKING THE PATTERN
    is_chinese = any(word in site for word in ["Taiyuan", "Xichang", "Jiuquan"])
    is_florida = "Florida" in site
    is_vandenberg = "Vandenberg" in site
    
    # PREDICTION LOGIC
    with st.expander(f"{name} — {time_uyt.strftime('%b %d, %H:%M UYT')}"):
        st.write(f"**Launch Site:** {site}")
        
        # 1. Check for the "Fefo Pattern"
        is_high_interest = is_chinese or is_florida or is_vandenberg
        
        # 2. Check the Time Window
        is_twilight = 18 <= time_uyt.hour <= 20
        is_high_altitude_window = 21 <= time_uyt.hour <= 23
        
        if is_high_interest:
            st.success("🎯 MATCH: This mission follows your historical sighting patterns.")
            
            if is_twilight:
                st.error("✨ PRIME VIEWING: Classic 'Jellyfish' plume likely (Sunlit at twilight).")
            elif is_high_altitude_window:
                st.warning("🌙 MIDNIGHT PLUME: Possible high-altitude glow (like your May 2024 sighting).")
            else:
                st.info("🌑 Check Horizon: Might be too late/early for sun illumination.")
        else:
            st.write("🔭 General Launch: Doesn't match your usual 'high-probability' patterns.")
        
        # Direction Logic
        if is_chinese:
            st.write("**Viewing Direction:** Look SOUTHWEST moving NORTH.")
        elif is_florida or is_vandenberg:
            st.write("**Viewing Direction:** Look NORTH/NORTHEAST horizon.")
