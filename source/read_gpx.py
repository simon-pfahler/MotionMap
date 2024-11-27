import gpxpy
from shapely.geometry import Point


def read_gpx(filename, tracknr=0):
    """
    Read the coordinates and times from a gpx file

    :param filename: Path to the gpx file
    :param tracknr: Number of the considered track in the gpx file.
        Defaults to `0`.

    :return: A list of `Point`s of all segments, and a list of times of all
        segments.
    """
    with open(filename, "r") as f:
        gpx = gpxpy.parse(f)
    track = gpx.tracks[tracknr]

    points = [list() for _ in range(len(track.segments))]
    times = [list() for _ in range(len(track.segments))]
    for i, segment in enumerate(track.segments):
        for point in segment.points:
            points[i].append(Point(point.latitude, point.longitude))
            times[i].append(point.time_difference(segment.points[0]))

    return points, times
