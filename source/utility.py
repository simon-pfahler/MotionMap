import numpy as np


def min_distance_point_edge(point, edge_start, edge_end):
    """
    Get the minimal distance between a point and an edge

    :param point: UTM coordinates of the point
    :param edge_start: UTM coordinates of the edge start
    :param edge_end: UTM coordinates of the edge end
    """

    x, y = point
    x0, y0 = edge_start
    x1, y1 = edge_end

    if x0 == x1 and y0 == y1:
        return np.sqrt((x - x0) ** 2 + (y - y0) ** 2)

    edge_start_closest = (x - x0) * (x1 - x0) + (y - y0) * (y1 - y0) < 0

    if edge_start_closest:
        return np.sqrt((y - y0) ** 2 + (x - x0) ** 2)

    edge_end_closest = (x - x1) * (x0 - x1) + (y - y1) * (y0 - y1) < 0

    if edge_end_closest:
        return np.sqrt((y - y1) ** 2 + (x - x1) ** 2)

    return np.abs((y1 - y0) * x - (x1 - x0) * y + x1 * y0 - x0 * y1) / np.sqrt(
        (y1 - y0) ** 2 + (x1 - x0) ** 2
    )


def likelihood_edge(point, edge_start, edge_end):
    """
    Get the likelihood of a given edge to be associated to a point

    :param point: UTM coordinates of the point
    :param edge_start: UTM coordinates of the edge start
    :param edge_end: UTM coordinates of the edge end
    """

    return np.exp(-min_distance_point_edge(point, edge_start, edge_end) / 5)


def likelihoods_first_edge(point, street_network):
    """
    Get the likelihoods of all edges being the first edge

    :param point: UTM coordinates of the point
    :param street_network: `Street_network` object
    """

    likelihoods = dict()

    for edge in street_network.graph.edges():
        edge_start = street_network.utm(edge[0])
        edge_end = street_network.utm(edge[1])
        likelihoods[edge] = likelihood_edge(point, edge_start, edge_end)

    return likelihoods


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
