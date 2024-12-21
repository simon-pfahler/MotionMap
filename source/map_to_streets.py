import networkx as nx

from source.utility import get_closest_node


def map_track_to_street_network(track, street_network):
    """
    Map a track to a street_network

    :param track: `Track` object
    :param street_network: `Street_network` objectn
    """

    paths = [nx.Graph() for _ in range(track.segments())]

    for segment in range(track.segments()):
        # start with closest node
        curr_node_index = get_closest_node(track.utm(0, 0), street_network)
        paths[segment].add_node(
            0,
            pos=street_network.graph.nodes[curr_node_index]["pos"],
            time=track.graphs[segment].nodes[0]["time"],
        )

    return paths
