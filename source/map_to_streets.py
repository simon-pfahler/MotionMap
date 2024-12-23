import networkx as nx

from source.utility import min_distance_point_edge


def map_track_to_street_network(track, street_network):
    """
    Map a track to a street_network

    :param track: `Track` object
    :param street_network: `Street_network` objectn
    """

    paths = [nx.Graph() for _ in range(track.segments())]

    for segment in range(track.segments()):
        # start with closest node
        pass

    return paths
