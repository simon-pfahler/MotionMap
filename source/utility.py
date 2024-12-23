import numpy as np


def min_distance_point_edge(point, edge_start, edge_end):
    """
    Get the minimal distance between a point and an edge

    :param point: UTM coordinates of the point
    :param edge_start: UTM coordinates of the edge start
    :param edge_end: UTM coordinates of the edge end
    """
    point_np = np.array(point)
    edge_start_np = np.array(edge_start)
    edge_end_np = np.array(edge_end)

    edge_start_closest = (point_np[0] - edge_start_np[0]) * (
        edge_end_np[0] - edge_start_np[0]
    ) + (point_np[1] - edge_start_np[1]) * (
        edge_end_np[1] - edge_start_np[1]
    ) < 0
    if edge_start_closest:
        return np.linalg.norm(point_np - edge_start_np)

    edge_end_closest = (point_np[0] - edge_end_np[0]) * (
        edge_start_np[0] - edge_end_np[0]
    ) + (point_np[1] - edge_end_np[1]) * (edge_start_np[1] - edge_end_np[1])
    if edge_end_closest:
        return np.linalg.norm(point_np - edge_end_np)

    return (
        (edge_end_np[1] - edge_start_np[1]) * point_np[0]
        - (edge_end_np[0] - edge_start_np[0]) * point_np[1]
        + edge_end_np[0] * edge_start_np[1]
        - edge_start_np[1] * edge_end_np[0]
    ) / np.linalg.norm(edge_start_np - edge_end_np)


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
