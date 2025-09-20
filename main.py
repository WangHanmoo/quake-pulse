# main.py — Artistic Earthquake Visualization with Trails & Pulse Effects
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timezone

# 1) Fetch earthquake data (past 30 days, USGS)
URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"
r = requests.get(URL, timeout=20)
data = r.json()

# 2) Parse GeoJSON into DataFrame
rows = []
for feat in data["features"]:
    props = feat["properties"]
    coords = feat["geometry"]["coordinates"]
    lon, lat, depth = coords[0], coords[1], coords[2]
    dt = datetime.fromtimestamp(props["time"] / 1000.0, tz=timezone.utc)
    rows.append({
        "time": dt,
        "longitude": lon,
        "latitude": lat,
        "depth": depth,
        "mag": props.get("mag", 0.0),
        "place": props.get("place"),
    })

df = pd.DataFrame(rows)

# 3) Frame by day
df["frame"] = df["time"].dt.strftime("%Y-%m-%d")

# 4) Size scaling (avoid negatives)
df["mag"] = pd.to_numeric(df["mag"], errors="coerce").fillna(0.0)
df["size"] = df["mag"].apply(lambda m: max(m, 0) * 5 + 3)

# 5) Add trailing effect (events stay visible for 3 days with fading)
frames = []
fade_days = 3
for offset in range(fade_days):
    temp = df.copy()
    temp["frame"] = temp["time"].dt.strftime("%Y-%m-%d")
    temp["opacity"] = 0.9 - offset * 0.3  # fade out
    temp["size"] = temp["size"] + offset * 3  # larger = fading ripple
    temp["frame_offset"] = temp["time"].dt.strftime("%Y-%m-%d")
    temp["frame"] = pd.to_datetime(temp["frame"]) + pd.to_timedelta(offset, unit="D")
    temp["frame"] = temp["frame"].dt.strftime("%Y-%m-%d")
    frames.append(temp)

df_fade = pd.concat(frames, ignore_index=True)

# 6) Build animated plot
fig = px.scatter_geo(
    df_fade,
    lon="longitude",
    lat="latitude",
    color="mag",
    size="size",
    hover_name="place",
    animation_frame="frame",
    projection="natural earth",
    color_continuous_scale="Turbo",  # Try "Plasma" / "Rainbow" too
    title="Quake-Pulse: Artistic Earthquake Visualization (30 Days)"
)

# 7) Styling: dark background + glowing points
fig.update_layout(
    geo=dict(
        showland=True, landcolor="rgb(15, 20, 30)",
        showocean=True, oceancolor="rgb(5,10,25)",
        bgcolor="black"
    ),
    paper_bgcolor="black",
    plot_bgcolor="black",
    font=dict(color="white"),
    coloraxis_colorbar=dict(title="Magnitude"),
)

fig.update_traces(
    marker=dict(opacity=0.7, line=dict(width=0.8, color="rgba(255,255,255,0.3)"))
)

# 8) Save & Show
fig.write_html("earthquakes_anim.html", include_plotlyjs="cdn")
print("✅ Done! Open earthquakes_anim.html in your browser for animation.")


