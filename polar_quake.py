# polar_quake.py
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import process_data
import fetch_usgs

def polar_visualization(df):
    fig = plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, polar=True)
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_title("Polar Quake Visualization", va='bottom', fontsize=14)

    points, = ax.plot([], [], 'o', alpha=0.6)

    mags = df["mag"].fillna(0).values
    depths = df["depth"].fillna(0).values
    times = np.linspace(0, 2*np.pi, len(mags))

    def init():
        points.set_data([], [])
        return points,

    def update(i):
        theta = times[:i]
        r = depths[:i] / np.max(depths)
        color = mags[:i]
        points.set_data(theta, r)
        points.set_color(plt.cm.plasma(color / np.max(color)))
        return points,

    ani = animation.FuncAnimation(fig, update, frames=len(df), init_func=init,
                                  interval=50, blit=True, repeat=True)
    plt.show()

if __name__ == "__main__":
    data = fetch_usgs.fetch_usgs()
    df = process_data.geojson_to_df(data)
    polar_visualization(df)
