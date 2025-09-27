import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from fetch_data import fetch_data
import os

st.set_page_config(page_title="Quake Pulse", layout="wide")

# ---------- 标题 ----------
st.title("🌋 Quake Pulse - Dual Earthquake Visualizations")

# ---------- 获取数据 ----------
data = fetch_data()
features = data["features"]

# 只保留有震级的事件，确保长度一致
valid = [f for f in features if f["properties"]["mag"] is not None]

lats = [f["geometry"]["coordinates"][1] for f in valid]
lons = [f["geometry"]["coordinates"][0] for f in valid]
mags = [f["properties"]["mag"] for f in valid]

# 清理后的震级（用于极坐标）
mags_clean = [m for m in mags if m > 0]

# ---------- 两列布局 ----------
col1, col2 = st.columns(2)

# ---------- 左边：地图可视化 ----------
with col1:
    st.subheader("🌍 Interactive Map")
    fig_map = px.scatter_geo(
        lat=lats,
        lon=lons,
        size=[max(m, 0.3) for m in mags],  # 确保不会报错
        color=mags,
        color_continuous_scale="Plasma",   # 粉紫-暖色渐变
        projection="natural earth",
        title="Global Earthquakes (Past 30 Days)"
    )
    fig_map.update_layout(
        geo=dict(showland=True, landcolor="white", showocean=True, oceancolor="lavender"),
    )
    st.plotly_chart(fig_map, use_container_width=True)

# ---------- 右边：艺术极坐标花瓣 ----------
with col2:
    st.subheader("🌸 Artistic Polar Flower (Animated)")

    # 生成动态帧（旋转 + 呼吸）
    frames = []
    steps = 30  # 帧数
    for t in range(steps):
        angle_shift = t * 12   # 每一帧整体旋转角度
        pulse_factor = 1 + 0.3 * ( (t % 10) / 10.0 )  # 呼吸效果 (0.7x ~ 1.3x)
        
        frames.append(go.Frame(
            data=[go.Scatterpolar(
                r=[m * pulse_factor for m in mags_clean],
                theta=[i * 10 + angle_shift for i in range(len(mags_clean))],
                mode="markers",
                marker=dict(
                    size=[m * 2 for m in mags_clean],
                    color=mags_clean,
                    colorscale="Plasma",   # 粉紫色调
                    showscale=False,
                    opacity=0.9
                ),
            )],
            name=str(t)
        ))

    # 初始画面
    fig_polar = go.Figure(
        data=[go.Scatterpolar(
            r=mags_clean,
            theta=[i * 10 for i in range(len(mags_clean))],
            mode="markers",
            marker=dict(
                size=[m * 2 for m in mags_clean],
                color=mags_clean,
                colorscale="Plasma",
                showscale=False,
                opacity=0.9
            ),
        )],
        frames=frames
    )

    # 设置动画
    fig_polar.update_layout(
        template="plotly_dark",  # 黑色背景
        polar=dict(bgcolor="black"),
        title="Earthquake Polar Flower 🌸 (Breathing & Rotating)",
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            buttons=[dict(label="▶ Play",
                          method="animate",
                          args=[None, {"frame": {"duration": 200, "redraw": True},
                                       "fromcurrent": True,
                                       "transition": {"duration": 0}}]),
                     dict(label="⏸ Pause",
                          method="animate",
                          args=[[None], {"frame": {"duration": 0, "redraw": False},
                                         "mode": "immediate",
                                         "transition": {"duration": 0}}])]
        )]
    )

    st.plotly_chart(fig_polar, use_container_width=True)

# ---------- AI Summary ----------
st.subheader("🤖 AI Summary")
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.warning("⚠️ AI Summary disabled (no API key set).")
else:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        prompt = "Summarize recent global earthquakes. Highlight regions with higher magnitudes."
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a seismologist who explains earthquake data clearly."},
                {"role": "user", "content": prompt}
            ]
        )
        st.info(response.choices[0].message.content)
    except Exception as e:
        st.error(f"⚠️ AI summary unavailable: {e}")

