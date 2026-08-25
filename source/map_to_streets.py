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
    edge_to_index = {tuple(sorted(e)): i for i, e in enumerate(edgelist)}
    edge_utms = [
        (street_network.utm(e[0]), street_network.utm(e[1])) for e in edgelist
    ]

    edge_neighbors_cache = {}

    def get_edge_neighbors(edge_index):
        if edge_index in edge_neighbors_cache:
            return edge_neighbors_cache[edge_index]
        edge = edgelist[edge_index]
        neighbors = set()
        for node in edge:
            for e in street_network.graph.edges(node):
                neighbors.add(edge_to_index[tuple(sorted(e))])
        edge_neighbors_cache[edge_index] = neighbors
        return neighbors

    for segment in range(track.segments()):
        # This is an implementation of the Viterbi algorithm
        P = -np.inf * np.ones((track.len(segment), street_network.nr_edges()))
        Q = np.zeros((track.len(segment), street_network.nr_edges()), dtype=int)

        # step 0
        utm_point = track.utm(segment, 0)
        for edge_index in range(P.shape[1]):
            utm_edge_start, utm_edge_end = edge_utms[edge_index]
            P[0, edge_index] = log_likelihood_edge(
                utm_point, utm_edge_start, utm_edge_end
            )
        P_dict = {
            (0, edge_index): P[0, edge_index]
            for edge_index in range(P.shape[1])
        }

        nr_calculated = P.shape[1]
        while True:
            track_index, edge_index = max(P_dict, key=P_dict.get)
            P_dict.pop((track_index, edge_index))
            print(
                f"At {track_index}\t{edge_index} ({P[track_index,edge_index]})"
            )
            if track_index == P.shape[0] - 1:
                break
            nr_calculated += 1

            utm_next_point = track.utm(segment, track_index + 1)
            next_edge_indices = get_edge_neighbors(edge_index)
            for next_edge_index in next_edge_indices:
                utm_edge_start, utm_edge_end = edge_utms[next_edge_index]
                new_ll = P[track_index, edge_index] + log_likelihood_edge(
                    utm_next_point, utm_edge_start, utm_edge_end
                )
                if new_ll > P[track_index + 1, next_edge_index]:
                    P[track_index + 1, next_edge_index] = new_ll
                    P_dict[(track_index + 1, next_edge_index)] = new_ll
                    Q[track_index + 1, next_edge_index] = edge_index

        print(f"Calculated {nr_calculated}/{P.shape[0]*P.shape[1]} points")

        plt.imshow(np.log(-P))
        plt.colorbar()
        plt.show()

        found_edges = list()
        found_edges.append(int(np.argmax(P[-1])))
        for track_index in reversed(range(P.shape[0] - 1)):
            if Q[track_index + 1][found_edges[-1]] == found_edges[-1]:
                continue
            found_edges.append(int(Q[track_index + 1][found_edges[-1]]))

        found_edges = found_edges[::-1]

        cleaned_found_edges = list()
        for index, edge_index in enumerate(found_edges):
            edge = edgelist[edge_index]
            if index == 0:
                if edge[1] in edgelist[found_edges[index + 1]]:
                    cleaned_found_edges.append((edge[0], edge[1]))
                else:
                    cleaned_found_edges.append((edge[1], edge[0]))
                continue
            if index == len(found_edges) - 1:
                if edge[0] == cleaned_found_edges[-1][1]:
                    cleaned_found_edges.append((edge[0], edge[1]))
                else:
                    cleaned_found_edges.append((edge[1], edge[0]))
                continue
            if (
                edge[0] == cleaned_found_edges[-1][1]
                and edge[1] in edgelist[found_edges[index + 1]]
            ):
                cleaned_found_edges.append((edge[0], edge[1]))
            elif (
                edge[1] == cleaned_found_edges[-1][1]
                and edge[0] in edgelist[found_edges[index + 1]]
            ):
                cleaned_found_edges.append((edge[1], edge[0]))

        graph = nx.Graph()
        first_edge = cleaned_found_edges[0]
        graph.add_node(0, **street_network.graph.nodes[first_edge[0]])
        graph.add_node(1, **street_network.graph.nodes[first_edge[1]])
        for edge_index_index in range(1, len(cleaned_found_edges)):
            edge = cleaned_found_edges[edge_index_index]
            graph.add_node(
                edge_index_index + 1,
                **street_network.graph.nodes[edge[1]],
            )
        for i in range(len(graph.nodes()) - 1):
            graph.add_edge(i, i + 1)

        paths.append(graph)

    return Track(paths)
