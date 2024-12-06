from source.plot_track import *
from source.read_gpx import *
from source.track import *

test_track = track(read_gpx("test_activity.gpx"))

print("test access:", test_track.graphs[0].nodes[0])

print("test utm:", test_track.utm(0, 0))

print("test distance:", test_track.distance(0))

plot_track(test_track)

plt.show()
