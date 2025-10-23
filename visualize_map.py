import json
import plotly.express as px

# 读取数据
with open("data/earthquakes.json", "r") as f:
    data = json.load(f)

features = data["features"]

# 提取需要的信息
lats = [f["geometry"]["coordinates"][1] for f in features]
lons = [f["geometry"]["coordinates"][0] for f in features]

# 如果 mag 是 None，就用 0.0 代替
mags = [f["properties"]["mag"] if f["properties"]["mag"] is not None else 0.0 for f in features]
places = [f["properties"]["place"] for f in features]


fig = px.scatter_geo(
    lat=lats,
    lon=lons,
    size=[max(m, 0.1) for m in mags],  # 保证点的大小至少是 0.1
    color=mags,
    hover_name=places,
    projection="natural earth",
    title="Earthquakes (Past 30 days)"
)

fig.show()
