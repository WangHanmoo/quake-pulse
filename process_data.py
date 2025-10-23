# process_data.py
import pandas as pd
from datetime import datetime
import numpy as np

def geojson_to_df(geojson):
    features = geojson.get("features", [])
    rows = []
    for f in features:
        props = f.get("properties", {})
        geom = f.get("geometry", {})
        coords = geom.get("coordinates", [None, None, None])
        lon, lat, depth = coords[0], coords[1], coords[2] if len(coords)>2 else None
        time_ms = props.get("time")
        time = datetime.utcfromtimestamp(time_ms/1000) if time_ms else None
        mag = props.get("mag") if props.get("mag") is not None else np.nan
        place = props.get("place", "")
        rows.append({
            "time": time,
            "time_ms": time_ms,
            "place": place,
            "mag": mag,
            "lon": lon,
            "lat": lat,
            "depth": depth,
            "id": f.get("id")
        })
    df = pd.DataFrame(rows)
    # drop rows missing lat/lon
    df = df.dropna(subset=["lat","lon"])
    # sort by time ascending
    df = df.sort_values("time").reset_index(drop=True)
    # add day index for animation frames if needed
    df["date"] = df["time"].dt.date
    df["date_str"] = df["date"].astype(str)
    return df

if __name__ == "__main__":
    import fetch_usgs
    data = fetch_usgs.fetch_usgs()
    df = geojson_to_df(data)
    print("Total quakes:", len(df))
    print(df.head())
