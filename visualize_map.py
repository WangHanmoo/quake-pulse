# visualize_map.py
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import pandas as pd
import process_data
import fetch_usgs

def visualize_quakes_on_map(df: pd.DataFrame):
    plt.figure(figsize=(10, 6))
    m = Basemap(projection='robin', lon_0=0, resolution='c')
    m.drawcoastlines(linewidth=0.5)
    m.drawcountries(linewidth=0.3)
    m.drawmapboundary(fill_color='lightblue')
    m.fillcontinents(color='lightgray', lake_color='lightblue')

    x, y = m(df["lon"].values, df["lat"].values)
    sc = m.scatter(x, y, c=df["mag"], cmap="plasma", alpha=0.7, s=df["mag"]**3)
    plt.colorbar(sc, label="Magnitude")

    plt.title("Global Earthquakes Visualization", fontsize=14)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    data = fetch_usgs.fetch_usgs()
    df = process_data.geojson_to_df(data)
    visualize_quakes_on_map(df)
