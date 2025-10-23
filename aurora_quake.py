# aurora_quake.py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
import fetch_usgs
import process_data

def aurora_visualization(df):
    # 归一化处理
    mags = df["mag"].fillna(0).values
    depths = df["depth"].fillna(0).values
    mags = np.clip(mags, 0, 8)
    depths = np.clip(depths, 0, 700)

    # 创建极坐标图
    fig = plt.figure(figsize=(8, 8), facecolor="black")
    ax = plt.subplot(111, polar=True, facecolor="black")
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_rticks([])
    ax.set_xticks([])
    ax.spines['polar'].set_visible(False)
    ax.set_title("AURORA QUAKE ✦", fontsize=20, color="white", pad=20, fontweight="bold")

    # 自定义渐变色（粉紫到暖橙）
    aurora_cmap = LinearSegmentedColormap.from_list(
        "aurora",
        ["#FF6FD8", "#FFB86C", "#FFE56E", "#C68EFF", "#8BE9FD"],
        N=512
    )

    # 初始化散点
    theta = np.linspace(0, 2*np.pi, len(mags))
    r = depths / np.max(depths)
    colors = mags / np.max(mags)
    scat = ax.scatter(theta, r, c=colors, cmap=aurora_cmap, s=mags**3, alpha=0.7)

    # 动画更新函数
    def update(frame):
        # 旋转+脉动效果
        offset = (frame / 50) % (2*np.pi)
        pulse = 1 + 0.3 * np.sin(frame / 10)
        new_theta = (theta + offset) % (2*np.pi)
        scat.set_offsets(np.c_[new_theta, r])
        scat.set_sizes((mags**3) * pulse)
        scat.set_alpha(0.6 + 0.3*np.sin(frame / 20))
        return scat,

    # 制作动画
    ani = animation.FuncAnimation(
        fig,
        update,
        frames=400,
        interval=40,
        blit=True,
        repeat=True
    )

    plt.show()

if __name__ == "__main__":
    data = fetch_usgs.fetch_usgs()
    df = process_data.geojson_to_df(data)
    aurora_visualization(df)
