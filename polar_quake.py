# polar_quake.py — Artistic Polar Flower Animation of Earthquakes
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timezone
import numpy as np # 导入 numpy 用于处理 NaN

# 1) Fetch earthquake data (past 30 days, USGS)
print("Fetching data from USGS...")
URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"
try:
    r = requests.get(URL, timeout=30)
    r.raise_for_status() # 检查 HTTP 错误
    data = r.json()
except requests.exceptions.RequestException as e:
    print(f"Error fetching data: {e}")
    exit()

# 2) Parse data into DataFrame
rows = []
for feat in data.get("features", []):
    props = feat.get("properties", {})
    coords = feat.get("geometry", {}).get("coordinates", [])
    
    # 确保 coordinates 有足够的元素
    if len(coords) < 3:
        continue 
        
    lon, lat, depth = coords[0], coords[1], coords[2]
    
    # 确保时间戳存在且有效
    timestamp = props.get("time")
    if timestamp is None:
        continue
        
    dt = datetime.fromtimestamp(timestamp / 1000.0, tz=timezone.utc)
    
    # 使用 .get() 且提供 None 作为默认值，让缺失的震级和地点变为 NaN
    rows.append({
        "time": dt,
        "hour": dt.hour + dt.minute / 60.0,  # 精确到小时
        "magnitude": props.get("mag"), # 保持原始值，让 nan 存在
        "depth": depth,
        "place": props.get("place"),
    })

df = pd.DataFrame(rows)

# ----------------------------------------------------------------------
# 关键修正：清理用于绘图的关键列
# ----------------------------------------------------------------------
# 震级 (magnitude) 列是用于 'size' 和 'color' 映射的关键。
# 如果该列有 NaN，Plotly 会报错。最简单的处理方式是删除这些行。
print(f"Total events: {len(df)}")
df.dropna(subset=['magnitude'], inplace=True)
print(f"Events after dropping NaN magnitudes: {len(df)}")
# ----------------------------------------------------------------------

# 3) 转换为极坐标数据
# - 角度 θ = 一天中的小时（0~24 → 0~360°）
# - 半径 r = 地震震级 (确保大于等于0)
df["theta"] = df["hour"] * 15  # 24 小时 → 360 度
# 确保半径 r 不会是负值 (虽然USGS震级通常不会有，但防止意外)
df["r"] = df["magnitude"].apply(lambda m: max(m, 0.0))

# 4) 生成动画帧（按日期逐天播放）
df["frame"] = df["time"].dt.strftime("%Y-%m-%d")

# 5) 绘制极坐标动画
fig = px.scatter_polar(
    df,
    r="r",
    theta="theta",
    size="r", # 使用清理后的 'r' 作为大小
    color="magnitude",
    hover_name="place",
    animation_frame="frame",
    # 艺术化效果：用 alpha (不透明度) 来模拟衰减
    color_continuous_scale="Plasma", 
    title="Polar Quake Flower — Artistic Earthquake Visualization"
)

# 6) 美化样式
# 调整不透明度和描边，以增强艺术效果
fig.update_traces(
    opacity=0.6, 
    marker=dict(
        line=dict(width=0.5, color='rgba(255, 255, 255, 0.4)')
    )
)
fig.update_layout(
    polar=dict(
        bgcolor="black",
        # 隐藏径向轴的刻度和线，只留下网格线
        radialaxis=dict(showticklabels=False, showline=False, ticks='', gridcolor='rgba(255, 255, 255, 0.1)'),
        # 设置角轴为顺时针，并旋转90度
        angularaxis=dict(
            showticklabels=True, 
            rotation=90, 
            direction="clockwise",
            gridcolor='rgba(255, 255, 255, 0.2)'
        )
    ),
    paper_bgcolor="black", # 整个背景为黑色
    font=dict(color="white"),
    coloraxis_colorbar=dict(title="Magnitude", thickness=15, len=0.8), # 美化色条
)

# 7) 保存为 HTML
print("Generating HTML file...")
fig.write_html("polar_quake.html", include_plotlyjs="cdn")
print("✅ Done! Open polar_quake.html in your browser to see the flower animation.")