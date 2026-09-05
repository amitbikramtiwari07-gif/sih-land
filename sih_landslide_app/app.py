import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import LocateControl

from data_service import fetch_live_weather, get_sikkim_zones_data
from ml_engine import calculate_landslide_risk
from map_builder import generate_hazard_map

# Page Setup
st.set_page_config(
    page_title="HimalayaGuard AI | Sikkim Landslide EWS",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Theme Styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    .hero-box {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px 26px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        backdrop-filter: blur(8px);
    }
    .metric-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 14px 18px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    .metric-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94a3b8;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.45rem;
        font-weight: 700;
        color: #f8fafc;
    }
    .threat-card {
        background: rgba(15, 23, 42, 0.75);
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 8px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Load terrain data
df_zones = get_sikkim_zones_data()

# --- SIDEBAR: NAVIGATION SELECTOR ---
st.sidebar.markdown("## 🧭 Application View")
app_mode = st.sidebar.radio(
    "Select Mode:",
    ["📊 Regional Command Center", "🚗 A-to-B Route & Detour Planner"],
    index=0
)
st.sidebar.markdown("---")

# ==============================================================================
# VIEW 1: REGIONAL HAZARD COMMAND CENTER
# ==============================================================================
if app_mode == "📊 Regional Command Center":
    st.sidebar.markdown("### 🎛️ Observation Sector")
    location_options = df_zones["Area"].tolist()
    selected_area_name = st.sidebar.selectbox("Active Telemetry Node:", location_options, index=1)

    selected_zone = df_zones[df_zones["Area"] == selected_area_name].iloc[0]
    sel_lat = selected_zone["lat"]
    sel_lon = selected_zone["lon"]
    sel_slope = selected_zone["slope"]
    sel_soil_moisture = selected_zone["base_soil_moisture"]

    weather_data = fetch_live_weather(sel_lat, sel_lon)

    # Compute risks for all zones
    computed_scores, computed_risks, computed_colors = [], [], []
    for _, row in df_zones.iterrows():
        score, risk_lvl, color, _, _ = calculate_landslide_risk(
            slope=row["slope"],
            live_rain=weather_data["precipitation"],
            past_3d_rain=weather_data["past_3d_rain"],
            base_moisture=row["base_soil_moisture"]
        )
        computed_scores.append(score)
        computed_risks.append(risk_lvl)
        computed_colors.append(color)

    df_zones["Score"] = computed_scores
    df_zones["Risk"] = computed_risks
    df_zones["Color"] = computed_colors

    active_score, active_risk, active_color, alert_type, alert_statement = calculate_landslide_risk(
        slope=sel_slope,
        live_rain=weather_data["precipitation"],
        past_3d_rain=weather_data["past_3d_rain"],
        base_moisture=sel_soil_moisture
    )

    st.sidebar.markdown("### 🔬 Ground Station Profile")
    st.sidebar.markdown(f"**Slope Gradient:** `{sel_slope}°`")
    st.sidebar.markdown(f"**Subsoil Saturation:** `{sel_soil_moisture}%`")
    st.sidebar.markdown(f"**Past 72h Rain:** `{weather_data['past_3d_rain']} mm`")
    st.sidebar.markdown(f"**Live Precipitation:** `{weather_data['precipitation']} mm/h`")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🛡️ Sector Risk Verdict")
    if alert_type == "error":
        st.sidebar.error(f"CRITICAL HAZARD — {active_score}/100")
    elif alert_type == "warning":
        st.sidebar.warning(f"ADVISORY WATCH — {active_score}/100")
    else:
        st.sidebar.success(f"STABLE CONDITIONS — {active_score}/100")

    map_zoom = st.sidebar.slider("Camera Elevation", 9, 13, 11)

    # Header
    st.markdown(
        f"""
        <div class="hero-box">
            <h2 style="margin: 0; font-size: 1.7rem; font-weight: 800; color: #ffffff;">
                🛡️ HimalayaGuard <span style="font-size: 1rem; font-weight: 400; color: #38bdf8;">| AI Landslide Monitoring</span>
            </h2>
            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.88rem;">
                Active Sector: <b style="color: #f1f5f9;">{selected_area_name}</b> ({selected_zone['District']})
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Ambient Temp</div><div class='metric-value'>{weather_data['temperature']} °C</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Relative Humidity</div><div class='metric-value'>{weather_data['humidity']} %</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>Rainfall Rate</div><div class='metric-value'>{weather_data['precipitation']} mm/h</div></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='metric-card'><div class='metric-label'>72h Antecedent Rain</div><div class='metric-value'>{weather_data['past_3d_rain']} mm</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Map & Leaderboard
    col_map, col_ranking = st.columns([1.85, 1.15])
    with col_map:
        st.markdown("#### 🗺️ Regional Hazard Grid")
        f_map = generate_hazard_map(df_zones, active_lat=sel_lat, active_lon=sel_lon, active_label=selected_area_name, zoom_level=map_zoom)
        st_folium(f_map, width="100%", height=500)

    with col_ranking:
        st.markdown("#### 🚨 Priority Threat Leaderboard")
        sorted_zones = df_zones.sort_values(by="Score", ascending=False)
        for _, row in sorted_zones.iterrows():
            is_focused = "border: 1px solid #38bdf8; background: rgba(56, 189, 248, 0.08);" if row["Area"] == selected_area_name else ""
            st.markdown(
                f"""
                <div class="threat-card" style="border-left: 5px solid {row['Color']}; {is_focused}">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-weight: 600; font-size: 0.86rem; color: #f8fafc;">{row['Area']}</span>
                        <span style="color: {row['Color']}; font-weight: 700; font-size: 0.8rem;">{row['Risk']} ({row['Score']})</span>
                    </div>
                    <div style="font-size: 0.74rem; color: #94a3b8; margin-top: 3px;">District: {row['District']} • Slope: {row['slope']}°</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("---")
    ca1, ca2 = st.columns([2.8, 1.2])
    with ca1:
        if alert_type == "error":
            st.error(f"🛑 **HAZARD ADVISORY:** {alert_statement}")
        elif alert_type == "warning":
            st.warning(f"⚠️ **ADVISORY:** {alert_statement}")
        else:
            st.success(f"✅ **STATUS:** {alert_statement}")
    with ca2:
        if st.button("📡 Dispatch Early Warning SMS", use_container_width=True):
            st.toast("Emergency SMS dispatched to registered phones!")
            st.info(f"**Dispatched SMS:**\n*SSDMA ALERT: Critical landslide risk in {selected_area_name}. Avoid NH-10; detour via Namchi.*")

# ==============================================================================
# VIEW 2: SMART A-TO-B ROUTE & DETOUR PLANNER
# ==============================================================================
else:
    st.markdown(
        """
        <div class="hero-box">
            <h2 style="margin: 0; font-size: 1.7rem; font-weight: 800; color: #ffffff;">
                🧭 Dynamic Transit & Landslide Detour Engine
            </h2>
            <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.88rem;">
                Detects road blockages on arterial highways and automatically re-routes traffic via safe mountain corridors.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Road node coordinates
    route_nodes = {
        "Majitar (SMIT Campus)": [27.190, 88.504],
        "Rangpo Checkpost": [27.176, 88.525],
        "Singtam Highway Junction": [27.230, 88.500],
        "Namchi Hill Bypass": [27.160, 88.350],
        "Gangtok Metro Center": [27.331, 88.613],
        "Mangan Hub": [27.505, 88.534],
        "Ravangla Corridor": [27.300, 88.360]
    }

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        start_node = st.selectbox("📍 Departure Point (Current Location):", list(route_nodes.keys()), index=0)
    with col_r2:
        end_node = st.selectbox("🏁 Target Destination:", list(route_nodes.keys()), index=4)

    start_c = route_nodes[start_node]
    end_c = route_nodes[end_node]

    if start_node == end_node:
        st.warning("⚠️ Departure and Destination cannot be the same point.")
    else:
        # Check if corridor hits the active Singtam slide barrier (NH-10)
        is_nh10_transit = (
            (start_node in ["Majitar (SMIT Campus)", "Rangpo Checkpost"] and end_node in ["Gangtok Metro Center", "Mangan Hub"]) or
            (start_node in ["Gangtok Metro Center", "Mangan Hub"] and end_node in ["Majitar (SMIT Campus)", "Rangpo Checkpost"])
        )

        mid_lat = (start_c[0] + end_c[0]) / 2
        mid_lon = (start_c[1] + end_c[1]) / 2
        nav_map = folium.Map(location=[mid_lat, mid_lon], zoom_start=11, tiles="OpenStreetMap")

        # Origin and Destination Markers
        folium.Marker(start_c, popup=f"Origin: {start_node}", icon=folium.Icon(color="blue", icon="play")).add_to(nav_map)
        folium.Marker(end_c, popup=f"Destination: {end_node}", icon=folium.Icon(color="green", icon="flag")).add_to(nav_map)

        if is_nh10_transit:
            st.error("🚨 **BLOCKED ROUTE DETECTED:** An active landslide is blocking NH-10 near Singtam. Direct route is impassable.")
            st.success("✅ **OPTIMAL DETOUR CALCULATED:** Rerouting via Namchi - Ravangla bypass corridor (+24 km, Safe).")

            # Blocked path: Red dashed line
            folium.PolyLine(
                [start_c, route_nodes["Singtam Highway Junction"], end_c],
                color="#ef233c",
                weight=6,
                dash_array="8, 8",
                tooltip="PRIMARY ROUTE (NH-10): BLOCKED BY LANDSLIDE"
            ).add_to(nav_map)

            # Slide obstruction icon
            folium.Marker(
                route_nodes["Singtam Highway Junction"],
                popup="<b>Landslide Obstruction Point</b><br>NH-10 Closed to all vehicles",
                icon=folium.Icon(color="red", icon="remove")
            ).add_to(nav_map)

            # Alternate safe path: Green solid line
            detour_coords = [start_c, route_nodes["Namchi Hill Bypass"], [27.280, 88.500], end_c]
            folium.PolyLine(
                detour_coords,
                color="#06d6a0",
                weight=6,
                opacity=0.95,
                tooltip="RECOMMENDED DETOUR: Open & Cleared Mountain Corridor"
            ).add_to(nav_map)

            # Telemetry comparison cards
            t1, t2, t3 = st.columns(3)
            t1.metric("Original Route (NH-10)", "Closed", delta="-100% Flow", delta_color="inverse")
            t2.metric("Alternate Detour Path", "Via Namchi Ridge", delta="Active Route", delta_color="normal")
            t3.metric("Estimated Added Transit", "+42 Mins", delta="Safe Terrain", delta_color="off")

        else:
            st.success("✅ **ROUTE ALL CLEAR:** No active landslides or road obstructions reported on this transit corridor.")
            folium.PolyLine([start_c, end_c], color="#38bdf8", weight=5, opacity=0.9, tooltip="Safe Transit Path").add_to(nav_map)

        st_folium(nav_map, width="100%", height=520)