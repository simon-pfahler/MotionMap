from source.map_to_streets import *
from source.plot import *
from source.read_gpx import *
from source.street_network import *
from source.track import *
from source.utility import *

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

cleaned_track = map_track_to_street_network(test_track, dresden)


log_likelihoods = np.zeros(len(test_track.graphs[0].nodes))
for index in range(test_track.len(0)):
    log_likelihoods[index] = log_likelihood_edge(
        test_track.utm(0, index),
        cleaned_track.utm(0, index),
        cleaned_track.utm(0, index + 1),
    )

plt.plot(log_likelihoods)
plt.axhline(-4, c="r")
plt.xlabel("Node index")
plt.ylabel("distance/5m")
plt.show()

# fig, ax = plot_street_network(dresden)

fig, ax = plt.subplots(1, 1)

fig, ax = plot_track(test_track, figax=(fig, ax))

fig, ax = plot_track(cleaned_track, figax=(fig, ax), color="C2")

plt.show()
