import networkx as nx

from source.plot import *
from source.track import *
from source.utility import (
    cosine_similarity,
    get_neighboring_edges,
    log_likelihood_edge,
    log_likelihoods_first_edge,
)


def map_track_to_street_network(track, street_network):
    """
    Map a track to a street_network

    :param track: `Track` object
    :param street_network: `Street_network` object
    """

    paths = list()

    debug = False
    if debug:
        plt.ion()
        fig, ax = plt.subplots(1, 1)

    for segment in range(track.segments()):
        # list that contains the calculated quality values
        # of the possible (edge, previous_edge) pairs at all timepoints
        # for index 0, the keys are only edges, not tuples of edges, as there
        # is no previous edge
        Q = [dict() for _ in range(track.len(segment))]

        # current most probable edge list
        edges = [(None, None) for _ in range(track.len(segment))]
        # index of the next edge for the currently most probable path
        # (i.e. the first index i for which edges[i] == (None, None)
        at_index = 0

        # get quality values for starting nodes of the track
        Q[0] = log_likelihoods_first_edge(track.utm(segment, 0), street_network)

        # loop until we got the most probable complete path
        while at_index < track.len(segment):

            # special case if at_index == 0
            if at_index == 0:
                next_edge = max(Q[0], key=Q[0].get)
                # go one step forward
                edges[at_index] = next_edge
                at_index += 1
                continue

            # >>> get new Q values
            # proposal for next edge
            next_edge = (None, None)

            # shorthand for current and previous edge
            curr_edge = edges[at_index - 1]
            prev_edge = edges[at_index - 2]

            relevant_edges = get_neighboring_edges(street_network, curr_edge)

            # add their quality values to Q[at_index]
            max_log_likelihood = -np.inf
            for edge in relevant_edges:
                if (edge, curr_edge) not in Q[at_index].keys():
                    track_edge_start = track.utm(segment, at_index - 1)
                    track_edge_end = track.utm(segment, at_index)
                    track_vec = np.array(track_edge_end) - np.array(
                        track_edge_start
                    )
                    if edge[0] in curr_edge:
                        street_edge_start = street_network.utm(edge[0])
                        street_edge_end = street_network.utm(edge[1])
                    else:
                        street_edge_start = street_network.utm(edge[1])
                        street_edge_end = street_network.utm(edge[0])
                    street_vec = np.array(street_edge_end) - np.array(
                        street_edge_start
                    )
                    Q[at_index][(edge, curr_edge)] = log_likelihood_edge(
                        track_edge_end,
                        street_edge_start,
                        street_edge_end,
                    )
                if Q[at_index][(edge, curr_edge)] > max_log_likelihood:
                    next_edge = edge
                    max_log_likelihood = Q[at_index][(edge, curr_edge)]

            # add next edge to edges list
            edges[at_index] = next_edge

            # update Q values
            for index in reversed(range(0, at_index)):
                maxQ = -np.inf
                relevant_edges = get_neighboring_edges(
                    street_network, edges[index]
                )
                for edge in relevant_edges:
                    if Q[index + 1][(edge, edges[index])] > maxQ:
                        maxQ = Q[index + 1][(edge, edges[index])]
                # print(maxQ)
                for edge in relevant_edges:
                    Q[index + 1][(edge, edges[index])] -= maxQ
                    # print(
                    #    f"{edge}: {Q[index + 1][(edge, edges[index])]+maxQ} -> {Q[index+1][(edge,edges[index])]}"
                    # )
                if index == 0:
                    Q[index][edges[index]] += maxQ
                else:
                    Q[index][(edges[index], edges[index - 1])] += maxQ

            # build new edges list
            # print(f"Building current path (previously at {at_index})")
            edges = [(None, None) for _ in range(track.len(segment))]
            edges[0] = max(Q[0], key=Q[0].get)
            at_index = 1
            while True:
                relevant_edges = get_neighboring_edges(
                    street_network, edges[at_index - 1]
                )
                if (edges[at_index - 1], edges[at_index - 1]) not in Q[
                    at_index
                ].keys():
                    break
                next_edge = (None, None)
                max_ll = -np.inf
                for edge in relevant_edges:
                    if Q[at_index][(edge, edges[at_index - 1])] > max_ll:
                        max_ll = Q[at_index][(edge, edges[at_index - 1])]
                        next_edge = edge
                # if max_ll != 0 and at_index != 1:
                #    print(f"Problem at {at_index}: max_ll={max_ll}")
                #    input()
                edges[at_index] = next_edge
                at_index += 1
                # print(f"{at_index}: {next_edge} (Q={max_ll})")
                if at_index == track.len(segment):
                    break

            print(f"Now at index {at_index}, edge={edges[at_index-1]}")

        # build the graph from the edges
        graph = nx.Graph()
        graph.add_node(0, **street_network.graph.nodes[edges[0][0]])
        for i, edge in enumerate(edges):
            graph.add_node(i + 1, **street_network.graph.nodes[edge[1]])
            graph.add_edge(i, i + 1)

        # append final path to all paths
        paths.append(graph)

    return Track(paths)
