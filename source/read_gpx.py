import gpxpy
import networkx as nx
from shapely.geometry import Point


def read_gpx(filename, tracknr=0):
    """
    Read the coordinates and times from a gpx file

    :param filename: Path to the gpx file
    :param tracknr: Number of the considered track in the gpx file.
        Defaults to `0`.

    :return: A `Graph` of all segments, and a list of times of all segments.
    """
    with open(filename, "r") as f:
        gpx = gpxpy.parse(f)
    track = gpx.tracks[tracknr]

    graphs = [nx.Graph() for _ in range(len(track.segments))]
    for i, segment in enumerate(track.segments):
        for j, point in enumerate(segment.points):
            graphs[i].add_node(
                j,
                pos=(point.longitude, point.latitude),
                time=point.time_difference(segment.points[0]),
            )
            if j > 0:
                graphs[i].add_edge(j - 1, j, color="blue")

    return graphs
