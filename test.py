from source.plot import *
from source.read_gpx import *
from source.street_network import *
from source.track import *

test_track = Track(read_gpx("test_activity.gpx"))

print("test access:", test_track.graphs[0].nodes[0])

print("test utm:", test_track.utm(0, 0))

print("test access:", test_track.graphs[0].nodes[0])

print("test distance:", test_track.distance(0))

dresden = Street_network(test_track.bbox)

print("test street network:", dresden.graph)

test_key = list(dresden.graph.nodes.keys())[0]

print(
    "test street network node:",
    test_key,
    dresden.graph.nodes[test_key],
)

print("test street network utm:", dresden.utm(test_key))

fig, ax = plot_street_network(dresden)

plot_track(test_track, figax=(fig, ax))

plt.show()
