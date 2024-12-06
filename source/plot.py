import matplotlib.pyplot as plt
import numpy as np


def plot_street_network(
    street_network,
    edge_color=lambda edge: "grey",
    node_color=lambda n: "black",
    figax=None,
):
    """
    Plot a street network using matplotlib

    :param street_network: street network to plot
    :param edge_color: function that takes the `Edge` and returns its color
    :param node_color: function that takes the `Node` and returns its color
    """
    if figax == None:
        fig, ax = plt.subplots(1, 1)
    else:
        fig, ax = figax

    # >>> plot edges
    for edge in street_network.graph.edges:
        xs = [street_network.utm(edge[0])[0], street_network.utm(edge[1])[0]]
        ys = [street_network.utm(edge[0])[1], street_network.utm(edge[1])[1]]
        ax.plot(xs, ys, color=edge_color(edge), zorder=1)
    # <<< plot edges

    # >>> plot nodes
    node_xs = list()
    node_ys = list()
    node_cs = list()
    for node in street_network.graph.nodes.keys():
        node_xs.append(street_network.utm(node)[0])
        node_ys.append(street_network.utm(node)[1])
        node_cs.append(node_color(node))
    ax.scatter(node_xs, node_ys, color=node_cs, s=4, zorder=2)
    # <<< plot nodes

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


def plot_track(track, figax=None):
    """
    Plot a track using matplotlib

    :param track: track to plot
    """
    if figax == None:
        fig, ax = plt.subplots(1, 1)
    else:
        fig, ax = figax
    for segment in range(track.segments()):
        x, y = zip(*[track.utm(segment, i) for i in range(track.len(0))])

        ax.plot(
            x,
            y,
            marker="o",
            markersize=4,
            markerfacecolor="C3",
            markeredgecolor="C3",
            zorder=3,
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
