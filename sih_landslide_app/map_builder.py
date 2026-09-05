import folium
from folium.plugins import LocateControl

def generate_hazard_map(df_zones, active_lat=27.23, active_lon=88.50, active_label="Active Location", zoom_level=10):
    """
    Renders an interactive map centered on the selected target coordinate
    with styled visual markers for high-risk zones and detour corridors.
    """
    sikkim_map = folium.Map(
        location=[active_lat, active_lon],
        zoom_start=zoom_level,
        tiles="OpenStreetMap",
        zoom_control=True
    )

    # In-map GPS device tracker button
    LocateControl(
        auto_start=False,
        flyTo=True,
        keepCurrentZoomLevel=False,
        strings={"title": "Track Device GPS Coordinates"}
    ).add_to(sikkim_map)

    # Active Monitored Pinpoint
    folium.Marker(
        location=[active_lat, active_lon],
        popup=f"<b>📍 Active Node: {active_label}</b><br>Lat: {active_lat:.4f}, Lon: {active_lon:.4f}",
        tooltip=f"Monitored Sector: {active_label}",
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(sikkim_map)

    # Regional Hazard Circular Buffers
    for _, row in df_zones.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=15 if row["Risk"] == "Critical" else (11 if row["Risk"] == "Moderate" else 8),
            color=row["Color"],
            weight=2,
            fill=True,
            fill_color=row["Color"],
            fill_opacity=0.6,
            popup=f"<b>{row['Area']}</b><br>District: {row['District']}<br>Risk Score: {row['Score']}/100 ({row['Risk']})<br>Slope: {row['slope']}°",
            tooltip=f"{row['Area']} | {row['Risk']} Threat ({row['Score']}/100)"
        ).add_to(sikkim_map)

    # Primary Corridor (NH-10 Suspended Stretch near Singtam)
    blocked_route = [
        [27.176, 88.525],  # Rangpo
        [27.230, 88.500],  # Singtam Slide Point
        [27.331, 88.613]   # Gangtok
    ]
    folium.PolyLine(
        blocked_route,
        color="#ef233c",
        weight=5,
        opacity=0.9,
        dash_array="7, 9",
        tooltip="NH-10: CLOSED DUE TO ACTIVE LANDSLIDE"
    ).add_to(sikkim_map)

    # Recommended Alternate Bypass Corridor via Namchi
    detour_route = [
        [27.176, 88.525],  # Rangpo
        [27.160, 88.350],  # Namchi
        [27.280, 88.500],  # Link Axis
        [27.331, 88.613]   # Gangtok
    ]
    folium.PolyLine(
        detour_route,
        color="#06d6a0",
        weight=5,
        opacity=0.95,
        tooltip="ACTIVE DETOUR: Open Bypass Corridor via Namchi"
    ).add_to(sikkim_map)

    # Obstruction Marker
    folium.Marker(
        location=[27.230, 88.500],
        popup="<b>Active Landslide Obstruction</b><br>NH-10 Closed",
        icon=folium.Icon(color="red", icon="remove")
    ).add_to(sikkim_map)

    return sikkim_map