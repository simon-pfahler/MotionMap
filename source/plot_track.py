import matplotlib.pyplot as plt
import numpy as np


def plot_track(track):
    """
    Plot a track using matplotlib

    :param track: track to plot
    :param fig: Figure object to write plot to
    :param ax: Axes object to write plot to
    """
    fig, ax = plt.subplots(1, 1)
    for segment in range(track.segments()):
        x, y = zip(*[track.utm(segment, i) for i in range(track.len(0))])

        ax.plot(
            x,
            y,
            marker="o",
            markersize=4,
            markerfacecolor="C3",
            markeredgecolor="C3",
        )
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    xmid = np.mean(xlim)
    ymid = np.mean(ylim)
    xrange = xlim[1] - xlim[0]
    yrange = ylim[1] - ylim[0]
    if 3 * xrange > 4 * yrange:
        yrange = 3 * xrange / 4
    else:
        xrange = 4 * yrange / 3
    ax.set_xlim(xmid - xrange / 2, xmid + xrange / 2)
    ax.set_ylim(ymid - yrange / 2, ymid + yrange / 2)
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_aspect("equal")
    ax.axis("off")

    return fig, ax
