import sys
from time import time

from source.map_to_streets import *
from source.plot import *
from source.read_gpx import *
from source.street_network import *
from source.track import *
from source.utility import *

test_track = Track(read_gpx(sys.argv[1])).filled(20)

street_network = Street_network(test_track.bbox)

print(
    f"Mapping a track with {test_track.len(0)} nodes onto a "
    f"street network with {street_network.nr_edges()} edges"
)

test_key = list(street_network.graph.nodes.keys())[0]

start_time = time()
mapped_track = map_track_to_street_network(test_track, street_network)
end_time = time()

print(f"Mapping took {end_time-start_time:.2f}s")

# fig, ax = plot_street_network(street_network)
fig, ax = plt.subplots(1, 1)
# fig, ax = plot_track(test_track, figax=(fig, ax))

fig, ax = plot_track(mapped_track, figax=(fig, ax), color="C2")

plt.show()
