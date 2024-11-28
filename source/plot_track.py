import matplotlib.pyplot as plt
from shapely.geometry import LineString


def plot_track(track):
    """
    Plot a track using matplotlib

    :param track: track to plot
    """
    fig, ax = plt.subplots(1, 1)
    for segment in range(track.segments()):
        proj_points = LineString(
            [track.proj(segment, i) for i in range(track.len(segment))]
        )
        x, y = proj_points.xy

        ax.plot(
            x,
            y,
            marker="o",
            markersize=4,
            markerfacecolor="C3",
            markeredgecolor="C3",
        )
    ax.set_aspect("equal")
    ax.axis("off")
    plt.show()
