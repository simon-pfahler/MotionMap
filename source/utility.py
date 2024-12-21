import numpy as np


def get_closest_node(utm, street_network):
    """
    Find the closest node from a `Street_network` to some coordinates

    :param utm: UTM coordinates of the position
    :param street_network: `Street_network` that should be searched for
        closest node
    """

    utm_np = np.array(utm)

    min_dist = np.inf
    min_node_index = None
    for node_index in street_network.graph.nodes.keys():
        dist = np.linalg.norm(utm_np - np.array(street_network.utm(node_index)))
        if dist < min_dist:
            min_dist = dist
            min_node_index = node_index

    return min_node_index
