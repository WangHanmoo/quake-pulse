# visualize_map.py
import os
import math
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
import json
try:
    import requests
except Exception:
    requests = None
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection
import matplotlib.patheffects as patheffects

try:
    # Basemap may be installed in the user's environment (requirements.txt lists basemap)
    from mpl_toolkits.basemap import Basemap
except Exception:
    Basemap = None
    # We'll use requests/json to draw a simple base map fallback if Basemap missing
    import json
    try:
        import requests
    except Exception:
        requests = None
    from matplotlib.patches import Polygon as MplPolygon
    from matplotlib.collections import PatchCollection


def visualize(df: pd.DataFrame, out_path: str = "earthquake_map.png", annotate_top: int = 5, show_legend: bool = True):
    """
    使用 matplotlib + Basemap 将地震分布绘制为静态 PNG（纯 Python，无 HTML）。

    参数:
      df: 包含 latitude/longitude 或 lat/lon, mag, place 的 DataFrame
      out_path: 输出 PNG 文件路径（默认 earthquake_map.png）
    """

    # determine latitude/longitude column names (support aliases)
    lat_col = 'latitude' if 'latitude' in df.columns else ('lat' if 'lat' in df.columns else None)
    lon_col = 'longitude' if 'longitude' in df.columns else ('lon' if 'lon' in df.columns else None)

    required = []
    if lat_col is None or lon_col is None:
        required.append("latitude/longitude (or lat/lon)")
    if 'mag' not in df.columns:
        required.append('mag')
    if 'place' not in df.columns:
        required.append('place')

    if required:
        raise ValueError(f"DataFrame must contain the following columns: {', '.join(required)}")

    print("Generating static map (PNG) visualization...")

    # normalize column names
    df2 = df.copy()
    df2['latitude'] = df2[lat_col]
    df2['longitude'] = df2[lon_col]
    df2 = df2.dropna(subset=["latitude", "longitude", "mag"])  # drop invalid rows

    # map mag to a visible, non-negative marker size
    def _size_from_mag(x):
        try:
            val = float(x)
        except Exception:
            val = 0.0
        # shift and scale so small/negative mags still show as small dots
        return max(val + 1.0, 0.2) * 3.0

    df2['marker_size'] = df2['mag'].apply(_size_from_mag)

    # prepare figure
    fig = plt.figure(figsize=(14, 8), facecolor='black')
    ax = fig.add_subplot(111)
    ax.set_facecolor('black')

    # Use Basemap if available, otherwise fallback to scatter of lon/lat with coastlines using cartopy is not available
    if Basemap is not None:
        m = Basemap(projection='robin', lon_0=0, resolution='c', ax=ax)
        # draw subtle ocean and land base
        m.drawmapboundary(fill_color='#06121a')
        m.fillcontinents(color='#0f1720', lake_color='#06121a', zorder=0)
        m.drawcoastlines(color='#91a3b0', linewidth=0.6)

        # Try to load GeoJSON country shapes (same cache used in fallback) and draw them
        geojson_path = os.path.join('data', 'countries.geojson')
        geojson = None
        if os.path.exists(geojson_path):
            try:
                with open(geojson_path, 'r', encoding='utf-8') as fh:
                    geojson = json.load(fh)
            except Exception:
                geojson = None

        if geojson is None and requests is not None:
            url = 'https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson'
            try:
                resp = requests.get(url, timeout=15)
                if resp.status_code == 200:
                    geojson = resp.json()
                    os.makedirs('data', exist_ok=True)
                    with open(geojson_path, 'w', encoding='utf-8') as fh:
                        json.dump(geojson, fh)
            except Exception:
                geojson = None

        country_patches = []
        if geojson is not None:
            features = geojson.get('features', [])
            # create colored patches per country using a colormap
            cmap_countries = cm.get_cmap('tab20')
            for i, feat in enumerate(features):
                geom = feat.get('geometry', {})
                typ = geom.get('type')
                coords = geom.get('coordinates', [])
                try:
                    if typ == 'Polygon':
                        for poly in coords:
                            proj = [m(lon, lat) for lon, lat in poly]
                            p = MplPolygon(proj, True)
                            country_patches.append((p, i))
                    elif typ == 'MultiPolygon':
                        for part in coords:
                            for poly in part:
                                proj = [m(lon, lat) for lon, lat in poly]
                                p = MplPolygon(proj, True)
                                country_patches.append((p, i))
                except Exception:
                    continue

            # add patches with color cycling and a soft shadow effect
            for p, idx in country_patches:
                color = cmap_countries(idx % cmap_countries.N)
                # add shadow via path effects
                p.set_facecolor(color)
                p.set_edgecolor('#0b1220')
                p.set_linewidth(0.25)
                p.set_alpha(0.9)
                p.set_zorder(0)
                p.set_path_effects([patheffects.SimplePatchShadow(offset=(4, -4), shadow_rgbFace=(0, 0, 0), alpha=0.25), patheffects.Normal()])
                ax.add_patch(p)

        # Convert lon/lat to map coordinates for scatter
        x, y = m(df2['longitude'].values, df2['latitude'].values)
    else:
        # simple lon/lat plot (no projection). Draw a low-res world base map using GeoJSON polygons
        print("Warning: Basemap not available. Drawing a simple lon/lat base map from GeoJSON.")

        # try to load cached countries geojson in data/, else download a copy
        geojson_path = os.path.join('data', 'countries.geojson')
        geojson = None
        if os.path.exists(geojson_path):
            try:
                with open(geojson_path, 'r', encoding='utf-8') as fh:
                    geojson = json.load(fh)
            except Exception:
                geojson = None

        if geojson is None and requests is not None:
            # download from a small, maintained repository (low-res countries)
            url = 'https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson'
            try:
                resp = requests.get(url, timeout=15)
                if resp.status_code == 200:
                    geojson = resp.json()
                    # cache it
                    os.makedirs('data', exist_ok=True)
                    with open(geojson_path, 'w', encoding='utf-8') as fh:
                        json.dump(geojson, fh)
            except Exception:
                geojson = None

        patches = []
        if geojson is not None:
            features = geojson.get('features', [])
            for feat in features:
                geom = feat.get('geometry', {})
                typ = geom.get('type')
                coords = geom.get('coordinates', [])
                try:
                    if typ == 'Polygon':
                        for poly in coords:
                            # poly is list of [lon, lat]
                            pts = [(lon, lat) for lon, lat in poly]
                            patches.append(MplPolygon(pts, True))
                    elif typ == 'MultiPolygon':
                        for part in coords:
                            for poly in part:
                                pts = [(lon, lat) for lon, lat in poly]
                                patches.append(MplPolygon(pts, True))
                except Exception:
                    continue

        if patches:
            pc = PatchCollection(patches, facecolor='#101020', edgecolor='white', linewidths=0.2, alpha=1.0)
            ax.add_collection(pc)

        # set axis limits to world extents and aspect
        ax.set_xlim(-180, 180)
        ax.set_ylim(-90, 90)
        ax.set_aspect('auto')

        x = df2['longitude'].values
        y = df2['latitude'].values

    # color by magnitude (improved aesthetics)
    mags = df2['mag'].values
    vmin = min(mags) if len(mags) else 0
    vmax = max(mags) if len(mags) else 1
    norm = plt.Normalize(vmin=vmin, vmax=vmax)
    cmap = cm.get_cmap('magma')
    colors = cmap(norm(mags))

    # scatter with subtle halo: plot slightly larger semi-transparent white markers underneath
    sizes = df2['marker_size'].values
    # halo
    ax.scatter(x, y, s=sizes * 1.6, c='white', alpha=0.12, linewidths=0)
    # main points
    sc = ax.scatter(x, y, s=sizes, c=colors, edgecolors='k', linewidth=0.25, alpha=0.95)

    # add colorbar legend for magnitude (with nicer ticks)
    if show_legend:
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array(mags)
        cbar = fig.colorbar(sm, ax=ax, orientation='vertical', fraction=0.03, pad=0.02)
        cbar.set_label('Magnitude', color='white')
        cbar.ax.yaxis.set_tick_params(color='white')
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')

    # title with basic stats
    mean_mag = float(df2['mag'].mean()) if len(df2) else 0.0
    max_mag = float(vmax)
    title = '🌍 Global Earthquake Visualization'
    subtitle = f'Total events: {len(df2)}    Mean mag: {mean_mag:.2f}    Max mag: {max_mag:.1f}'
    ax.set_title(title + '\n' + subtitle, color='orange', fontsize=18)
    ax.tick_params(colors='white')

    # annotate top N events by magnitude
    if annotate_top and annotate_top > 0 and len(df2):
        top = df2.nlargest(annotate_top, 'mag')
        for _, row in top.iterrows():
            try:
                rx, ry = (m(row['longitude'], row['latitude']) if Basemap is not None else (row['longitude'], row['latitude']))
            except Exception:
                rx, ry = (row['longitude'], row['latitude'])
            ax.text(rx, ry, f" {row['place'][:40]} ({row['mag']:.1f})", color='white', fontsize=8, weight='bold')

    # save the figure
    plt.tight_layout()
    fig.savefig(out_path, facecolor=fig.get_facecolor(), dpi=180)
    plt.close(fig)

    print(f"Saved map to {out_path}")

    # Open the image using Python (Windows: os.startfile)
    try:
        if os.name == 'nt':
            os.startfile(os.path.abspath(out_path))
        else:
            # POSIX fallback: try xdg-open or open
            import subprocess

            opener = 'xdg-open' if os.name == 'posix' else None
            if opener:
                subprocess.run([opener, out_path], check=False)
    except Exception as e:
        print(f"Could not open image automatically: {e}")

