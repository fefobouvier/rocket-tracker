# --- UPGRADED PREDICTION LOGIC ---
        
        # 1. Check for the "Fefo Pattern" (Chinese or SpaceX high-orbit)
        is_high_interest = any(word in site for word in ["Taiyuan", "Xichang", "Jiuquan", "Kennedy", "Vandenberg"])
        
        # 2. Check the Time Window
        # Evening Twilight: Best for lower altitude plumes (Falcon 9)
        is_twilight = 18 <= time_uyt.hour <= 20
        
        # High Altitude Night: Best for upper-stage burns (Long March / Falcon Heavy)
        is_high_altitude_window = 21 <= time_uyt.hour <= 23
        
        if is_high_interest:
            st.success("🎯 MATCH: This mission follows your historical sighting patterns.")
            
            if is_twilight:
                st.error("✨ PRIME VIEWING: Classic 'Jellyfish' plume likely (Sunlit at twilight).")
            elif is_high_altitude_window:
                st.warning("🌙 MIDNIGHT PLUME: Possible high-altitude glow (like your May 2024 sighting).")
            else:
                st.info("🌑 Check Horizon: Might be too late/early for sun illumination.")
        
        st.write(f"**Viewing Direction:** {'Southwest' if is_chinese else 'North/Northeast'}")
