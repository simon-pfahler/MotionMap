import os

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from source.read_gpx import read_gpx
from source.track import Track

name = "Simon"

files = os.listdir(f"mapped_activities_{name}")

network = nx.Graph()

max_count = 0

for file in files:
    activity_id = file.split("_")[1].split(".")[0]
    track = Track(
        read_gpx(f"mapped_activities_{name}/activity_{activity_id}.gpx")
    )

    for segment in range(track.segments()):
        for node in track.graphs[segment].nodes:
            node_id = track.graphs[segment].nodes[node]["node_id"]
            pos = track.graphs[segment].nodes[node]["pos"]
            network.add_node(node_id, pos=pos)
        for edge in track.graphs[segment].edges:
            node_id_start = track.graphs[segment].nodes[edge[0]]["node_id"]
            node_id_end = track.graphs[segment].nodes[edge[1]]["node_id"]
            new_edge = tuple(sorted((node_id_start, node_id_end)))
            if new_edge not in network.edges:
                network.add_edge(*new_edge, count=0)
            network.edges[new_edge]["count"] += 1
            count = network.edges[new_edge]["count"]
            if count > max_count:
                max_count += 1

print(
    f"Processed {len(files)} files, "
    f"found {len(network.edges)} edges, "
    f"most run edge is run {max_count} times."
)

fig, ax = plt.subplots(1, 1)
fig.set_facecolor((51 / 255, 51 / 255, 51 / 255))
ax.set_facecolor((51 / 255, 51 / 255, 51 / 255))

# >>> plot edges
for edge in network.edges:
    xs = [network.nodes[edge[0]]["pos"][0], network.nodes[edge[1]]["pos"][0]]
    ys = [network.nodes[edge[0]]["pos"][1], network.nodes[edge[1]]["pos"][1]]
    ax.plot(
        xs,
        ys,
        color="#DDDDDD",
        alpha=0.1 + 0.9 * (network.edges[edge]["count"] / max_count),
        # alpha=0.9 * (1 - 1 / network.edges[edge]["count"]) + 0.1,
        zorder=1,
    )
# <<< plot edges

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
ax.set_aspect("equal")
ax.set_xlim(xmid - xrange / 2, xmid + xrange / 2)
ax.set_ylim(ymid - yrange / 2, ymid + yrange / 2)
plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
ax.axis("off")

plt.show()
