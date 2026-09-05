import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import LocateControl

st.set_page_config(page_title="AI Route Planner", page_icon="🗺️", layout="wide")

# Custom Dark Theme CSS for consistency
st.markdown(
    """
    <style>
    .stApp { background-color: #0b0f19; color: #e2e8f0; font-family: 'Inter', sans-serif; }
    .nav-card { background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 20px; margin-bottom: 20px; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🧭 Smart Transit & Route Optimization")
st.caption("Dynamic A-to-B navigation with automated landslide detour routing.")

# Pre-defined coordinates for Sikkim nodes
locations = {
    "Majitar (SMIT Campus)": [27.190, 88.504],
    "Rangpo": [27.176, 88.525],
    "Singtam": [27.230, 88.500],
    "Namchi": [27.160, 88.350],
    "Gangtok": [27.331, 88.613],
    "Mangan": [27.505, 88.534]
}

# --- NAVIGATION UI ---
st.markdown("<div class='nav-card'>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    use_gps = st.toggle("📍 Use Device GPS as Start", value=False)
    if use_gps:
        start_point = "Majitar (SMIT Campus)" # Simulated GPS snap
        st.info("Snapped to nearest node: Majitar")
    else:
        start_point = st.selectbox("Origin:", list(locations.keys()), index=0)

with col2:
    end_point = st.selectbox("Destination:", list(locations.keys()), index=4)

with col3:
    st.markdown("<br>", unsafe_allow_html=True)
    calculate_btn = st.button("Calculate Route", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- ROUTING LOGIC & MAP ---
if start_point == end_point:
    st.warning("Origin and Destination cannot be the same.")
else:
    # Initialize map centered between start and end
    start_coords = locations[start_point]
    end_coords = locations[end_point]
    mid_lat = (start_coords[0] + end_coords[0]) / 2
    mid_lon = (start_coords[1] + end_coords[1]) / 2
    
    route_map = folium.Map(location=[mid_lat, mid_lon], zoom_start=11, tiles="OpenStreetMap")
    LocateControl(auto_start=use_gps, flyTo=True).add_to(route_map)

    # Start & End Markers
    folium.Marker(start_coords, popup=f"<b>Start:</b> {start_point}", icon=folium.Icon(color="blue", icon="play")).add_to(route_map)
    folium.Marker(end_coords, popup=f"<b>Destination:</b> {end_point}", icon=folium.Icon(color="green", icon="flag")).add_to(route_map)

    # Trigger Demo Landslide Scenario: Majitar/Rangpo to Gangtok
    if start_point in ["Majitar (SMIT Campus)", "Rangpo"] and end_point == "Gangtok":
        st.error(f"🚨 **ACTIVE LANDSLIDE DETECTED:** The primary route via NH-10 (Singtam) is impassable.")
        st.success(f"✅ **ALTERNATE ROUTE FOUND:** Rerouting via Namchi bypass.")
        
        # Blocked Primary Route
        blocked_path = [start_coords, locations["Singtam"], end_coords]
        folium.PolyLine(blocked_path, color="#ef233c", weight=6, dash_array="8, 8", tooltip="Blocked: NH-10").add_to(route_map)
        folium.Marker(locations["Singtam"], icon=folium.Icon(color="red", icon="remove")).add_to(route_map)
        
        # Safe Detour Route
        safe_path = [start_coords, locations["Namchi"], [27.280, 88.500], end_coords]
        folium.PolyLine(safe_path, color="#06d6a0", weight=6, tooltip="Safe Detour Route").add_to(route_map)
        
    else:
        st.success("✅ **ROUTE CLEAR:** No geological hazards detected on this corridor.")
        # Standard direct line routing for other combinations
        folium.PolyLine([start_coords, end_coords], color="#38bdf8", weight=5, tooltip="Primary Route").add_to(route_map)

    st_folium(route_map, width="100%", height=500)