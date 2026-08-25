import networkx as nx
from tqdm import tqdm

from source.plot import *
from source.track import *
from source.utility import log_likelihood_edge


def map_track_to_street_network(track, street_network):
    """
    Map a track to a street_network

    :param track: `Track` object
    :param street_network: `Street_network` object
    """

    paths = list()

    edgelist = [sorted(e) for e in street_network.graph.edges]

    for segment in range(track.segments()):
        # This is an implementation of the Viterbi algorithm
        P = -np.inf * np.ones((track.len(segment), street_network.nr_edges()))
        Q = np.zeros((track.len(segment), street_network.nr_edges()), dtype=int)

        # step 0
        utm_point = track.utm(0, 0)
        for edge_index in range(P.shape[1]):
            utm_edge_start = street_network.utm(edgelist[edge_index][0])
            utm_edge_end = street_network.utm(edgelist[edge_index][1])
            P[0, edge_index] = log_likelihood_edge(
                utm_point, utm_edge_start, utm_edge_end
            )

        for track_index in tqdm(range(1, P.shape[0])):
            utm_point = track.utm(0, track_index)
            for edge_index in range(P.shape[1]):
                utm_edge_start = street_network.utm(edgelist[edge_index][0])
                utm_edge_end = street_network.utm(edgelist[edge_index][1])
                transition_ll = log_likelihood_edge(
                    utm_point, utm_edge_start, utm_edge_end
                )
                prev_edge_indices = set(
                    edgelist.index(sorted(e))
                    for i in range(2)
                    for e in street_network.graph.edges(edgelist[edge_index][i])
                )
                for prev_edge_index in prev_edge_indices:
                    new_ll = P[track_index - 1, prev_edge_index] + transition_ll
                    if new_ll > P[track_index, edge_index]:
                        P[track_index, edge_index] = new_ll
                        Q[track_index, edge_index] = prev_edge_index

        found_edges = np.zeros(P.shape[0], dtype=int)
        found_edges[-1] = np.argmax(P[-1])
        for track_index in reversed(range(P.shape[0] - 1)):
            found_edges[track_index] = Q[track_index + 1][
                found_edges[track_index + 1]
            ]

        graph = nx.Graph()
        for edge_index in found_edges:
            edge = edgelist[edge_index]
            graph.add_node(edge[0], **street_network.graph.nodes[edge[0]])
            graph.add_node(edge[1], **street_network.graph.nodes[edge[1]])
            graph.add_edge(edge[0], edge[1])

        paths.append(graph)

    return Track(paths)
