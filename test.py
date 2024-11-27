from source.read_gpx import *
from source.track import *

test_track = track(*read_gpx("test_activity.gpx"))

print(test_track.point_at_time(0, 6477))
print(test_track.points[0][-2])

print(test_track.distance(segment=0, start_index=-2, end_index=-1))
