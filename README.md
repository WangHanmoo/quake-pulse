# quake-pulse
An interactive web-based visualization of global earthquake activity, combining data from USGS with AI-generated summaries. This project demonstrates data fetching, visualization, interactivity via Streamlit, and optional AI explanation.
It collects global earthquake data from the past 30 days and creates an animated, artistic world map using Plotly to visualize the distribution and magnitude of seismic events over time.Generates a natural language summary of recent earthquake patterns using OpenAI API or LMStudio. Streamlit App Provides a web-based interface for interactive exploration.

With API key → AI summary enabled.
Without API key → App still runs, summary disabled.

# Data Source
- [USGS Earthquake Hazards Program — GeoJSON Feeds](https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php)  
- Specific dataset used in this project:  
  [All earthquakes, past 30 days (GeoJSON)](https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson)

