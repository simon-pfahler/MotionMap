from source.map_to_streets import *
from source.plot import *
from source.read_gpx import *
from source.street_network import *
from source.track import *
from source.utility import *

test_track = Track(read_gpx("test_activity_long.gpx"))

print("test access:", test_track.graphs[0].nodes[0])

print("test utm:", test_track.utm(0, 0))

print("test access:", test_track.graphs[0].nodes[0])

print("test distance:", test_track.distance(0))

street_network = Street_network(test_track.bbox)

print("test street network:", street_network.graph)

test_key = list(street_network.graph.nodes.keys())[0]

print(
    "test street network node:",
    test_key,
    street_network.graph.nodes[test_key],
)

print("test street network utm:", street_network.utm(test_key))

cleaned_track = map_track_to_street_network(test_track, street_network)

fig, ax = plot_street_network(street_network)

# fig, ax = plt.subplots(1, 1)

fig, ax = plot_track(test_track, figax=(fig, ax))

fig, ax = plot_track(cleaned_track, figax=(fig, ax), color="C2")

plt.show()
