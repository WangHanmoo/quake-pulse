import os
import json
import requests
import plotly.express as px
import streamlit as st
from openai import OpenAI

# ----------- 配置区 -----------
USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"
CACHE_FILE = "data/earthquakes.json"
# 需要在系统环境变量或 .env 文件里设置 OPENAI_API_KEY
# PowerShell 临时设置示例： $env:OPENAI_API_KEY="sk-xxxx"
# --------------------------------

# ---------- 数据获取 ----------
def fetch_data():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)

    os.makedirs("data", exist_ok=True)
    data = requests.get(USGS_URL).json()
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f)
    return data


# ---------- 可视化 ----------
def plot_map(data, mag_min=0.0):
    features = data["features"]

    lats, lons, mags, places, times = [], [], [], [], []
    for f in features:
        coords = f["geometry"]["coordinates"]
        mag = f["properties"]["mag"]
        if mag is None or mag < mag_min:
            continue
        lons.append(coords[0])
        lats.append(coords[1])
        mags.append(mag)
        places.append(f["properties"]["place"])
        times.append(f["properties"]["time"])

    fig = px.scatter_geo(
        lat=lats,
        lon=lons,
        size=[max(m, 0.1) for m in mags],
        color=mags,
        hover_name=places,
        projection="natural earth",
        title=f"Earthquakes (M ≥ {mag_min}, Past 30 Days)"
    )
    return fig


# ---------- AI 自动解说 ----------
def generate_summary(mag_min=0.0):
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        prompt = f"Summarize recent global earthquakes with magnitude >= {mag_min}. \
                  Highlight patterns and significant regions in plain English."
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a seismologist who explains earthquake data clearly."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ AI summary unavailable: {e}"


# ---------- Streamlit 界面 ----------
st.set_page_config(page_title="🌋 Quake Pulse", layout="wide")

st.title("🌋 Quake Pulse: Global Earthquakes Visualization")

# 控件
mag_min = st.slider("Minimum Magnitude", 0.0, 8.0, 4.5, 0.1)

# 加载数据
with st.spinner("Fetching earthquake data..."):
    data = fetch_data()

# 可视化
fig = plot_map(data, mag_min)
st.plotly_chart(fig, use_container_width=True)

# AI 解说
st.subheader("AI Summary")
summary = generate_summary(mag_min)
st.write(summary)
