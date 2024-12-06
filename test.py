from source.plot_track import *
from source.read_gpx import *
from source.street_network import *
from source.track import *

test_track = track(read_gpx("test_activity.gpx"))

print("test access:", test_track.graphs[0].nodes[0])

print("test utm:", test_track.utm(0, 0))

print("test access:", test_track.graphs[0].nodes[0])

print("test distance:", test_track.distance(0))

dresden = street_network(test_track.bbox)

print("test street network:", dresden.graph)

test_key = list(dresden.graph.nodes.keys())[0]

print(
    "test street network node:",
    test_key,
    dresden.graph.nodes[test_key],
)

print("test street network utm:", dresden.utm(test_key))

plot_track(test_track)

plt.show()
