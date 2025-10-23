"""
Interactive Bokeh app for earthquake map visualization.

Run with:
  bokeh serve --show interactive_map.py

This app is pure Python and uses the processed DataFrame from process_data.geojson_to_df.
"""
import os
import json
from datetime import datetime

import pandas as pd

from bokeh.io import curdoc
from bokeh.models import (
    GeoJSONDataSource,
    ColumnDataSource,
    LinearColorMapper,
    ColorBar,
    HoverTool,
    Slider,
    Button,
)
from bokeh.plotting import figure
from bokeh.layouts import column, row
from bokeh.palettes import magma

import fetch_usgs
import process_data


def load_countries_geojson():
    path = os.path.join('data', 'countries.geojson')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    # try download
    try:
        import requests

        url = 'https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson'
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            geo = r.json()
            os.makedirs('data', exist_ok=True)
            with open(path, 'w', encoding='utf-8') as fh:
                json.dump(geo, fh)
            return geo
    except Exception:
        return None


def make_app(doc):
    # load data (uses cached file if available)
    data = fetch_usgs.fetch_usgs()
    df = process_data.geojson_to_df(data)

    # prepare country geojson source
    countries = load_countries_geojson()
    geo_source = None
    if countries is not None:
        geo_source = GeoJSONDataSource(geojson=json.dumps(countries))

    # prepare quake data source
    # ensure we have date_str column
    if 'date_str' not in df.columns:
        df['date_str'] = df['time'].dt.date.astype(str)

    df['marker_size'] = df['mag'].apply(lambda x: max(float(x) + 1.0, 0.2) * 4.0)

    dates = sorted(df['date_str'].unique())
    if not dates:
        dates = [str(datetime.utcnow().date())]

    # initial filter: latest date
    current_date = dates[-1]
    view_df = df[df['date_str'] == current_date]

    source = ColumnDataSource(view_df)

    p = figure(title="Interactive Earthquake Map", match_aspect=True,
               tools="pan,wheel_zoom,box_zoom,reset,save", background_fill_color="#06121a",
               x_axis_label='Longitude', y_axis_label='Latitude')

    # draw countries as patches if available
    if geo_source is not None:
        p.patches('xs', 'ys', source=geo_source,
                  fill_color="#0f1720", line_color="#1f2a36", line_width=0.3, fill_alpha=0.9)

    # color mapper
    mag_min = float(df['mag'].min()) if len(df) else 0.0
    mag_max = float(df['mag'].max()) if len(df) else 5.0
    mapper = LinearColorMapper(palette=magma(256), low=mag_min, high=mag_max)

    # quake circles
    quake_renderer = p.circle('lon', 'lat', source=source, size='marker_size',
                              fill_color={'field': 'mag', 'transform': mapper}, fill_alpha=0.9,
                              line_color='black', line_width=0.2)

    hover = HoverTool(renderers=[quake_renderer], tooltips=[
        ("Place", "@place"),
        ("Mag", "@mag"),
        ("Time", "@time"),
    ])
    p.add_tools(hover)

    color_bar = ColorBar(color_mapper=mapper, label_standoff=12, location=(0, 0))
    p.add_layout(color_bar, 'right')

    # slider
    slider = Slider(start=0, end=len(dates) - 1, value=len(dates) - 1, step=1, title="Date Index")

    playing = {'value': False}


    def update_source(attr, old, new):
        idx = slider.value
        ds = dates[idx]
        new_df = df[df['date_str'] == ds]
        if new_df.empty:
            source.data = {k: [] for k in source.data}
        else:
            # ColumnDataSource expects columns named used by glyphs
            new_src = {
                'lon': new_df['lon'].values,
                'lat': new_df['lat'].values,
                'mag': new_df['mag'].values,
                'place': new_df['place'].values,
                'time': new_df['time'].astype(str).values,
                'marker_size': new_df['marker_size'].values,
            }
            source.data = new_src


    slider.on_change('value', update_source)

    def animate_update():
        if slider.value < slider.end:
            slider.value = slider.value + 1
        else:
            slider.value = slider.start

    def play_pause():
        if not playing['value']:
            playing['value'] = True
            play_button.label = 'Pause'
            doc.add_periodic_callback(animate_update, 800)
        else:
            playing['value'] = False
            play_button.label = 'Play'
            # remove all periodic callbacks: simpler to clear all and re-add if needed
            doc.remove_periodic_callback(animate_update)

    play_button = Button(label='Play', width=60)
    play_button.on_click(play_pause)

    # layout
    layout = column(p, row(slider, play_button))
    doc.add_root(layout)


make_app(curdoc())
