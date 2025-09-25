import requests, json, os

URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"

def fetch_data(cache_file="data/earthquakes.json"):
    # 如果已经有缓存文件，就直接读
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            return json.load(f)

    # 否则去 USGS 抓数据
    data = requests.get(URL).json()
    os.makedirs("data", exist_ok=True)   # 确保 data 文件夹存在
    with open(cache_file, "w") as f:
        json.dump(data, f)
    return data

if __name__ == "__main__":
    data = fetch_data()
    print(f"✅ 数据加载成功，共获取 {len(data['features'])} 条地震记录。")
    print("已保存到 data/earthquakes.json")
