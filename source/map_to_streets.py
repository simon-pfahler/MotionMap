import networkx as nx

from source.plot import *
from source.track import *
from source.utility import (
    cosine_similarity,
    likelihood_edge,
    likelihoods_first_edge,
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
        # TODO: Would it be sufficient to always use the current edge as key?
        Q = [dict() for _ in range(track.len(segment))]

        # current most probable edge list
        edges = [(None, None) for _ in range(track.len(segment))]
        # index of the next edge for the currently most probable path
        # (i.e. the first index i for which edges[i] == (None, None)
        next_index = 0

        # get quality values for starting nodes of the track
        Q[0] = likelihoods_first_edge(track.utm(segment, 0), street_network)

        # loop until we got the most probable complete path
        while next_index < track.len(segment):

            # >>> DEBUG
            if next_index > 0:
                if next_index > 1:
                    print(
                        next_index,
                        Q[next_index - 1][
                            (edges[next_index - 1], edges[next_index - 2])
                        ],
                        Q[0][(518671757, 1752315539)],
                    )
                else:
                    print(
                        next_index,
                        Q[next_index - 1][edges[next_index - 1]],
                        Q[0][(518671757, 1752315539)],
                    )
                # build the graph from the edges
                if debug:
                    plt.cla()
                    graph = nx.Graph()
                    graph.add_node(0, **street_network.graph.nodes[edges[0][0]])
                    for i in range(next_index):
                        graph.add_node(
                            i + 1, **street_network.graph.nodes[edges[i][1]]
                        )
                        graph.add_edge(i, i + 1)
                    # fig, ax = plot_street_network(street_network)
                    fig, ax = plot_track(track, figax=(fig, ax))
                    fig, ax = plot_track(
                        Track([graph]), figax=(fig, ax), color="C2"
                    )
                    utm1 = street_network.utm(edges[next_index - 1][0])
                    utm2 = street_network.utm(edges[next_index - 1][1])
                    ax.scatter(
                        [utm1[0], utm2[0]],
                        [utm1[1], utm2[1]],
                        s=16,
                        color="C2",
                    )
                    x0, y0 = street_network.utm(edges[0][0])
                    x1, y1 = street_network.utm(edges[next_index - 1][0])
                    ax.set_xlim(min(x0, x1) - 100, max(x0, x1) + 100)
                    ax.set_ylim(min(y0, y1) - 100, max(y0, y1) + 100)
                    plt.show()
                    plt.pause(0.05)
            # <<< DEBUG

            # special case if next_index == 0
            if next_index == 0:
                next_edge = max(Q[0], key=Q[0].get)
                # go one step forward
                edges[next_index] = next_edge
                next_index += 1
                continue

            # TODO: Check here if we should take a step backwards

            # proposal for next edge
            next_edge = (None, None)

            # shorthand for current and previous edge
            curr_edge = edges[next_index - 1]
            prev_edge = edges[next_index - 2]

            # the possible next edges are the current edge and the neighboring
            # edges at both ends of the current edge
            relevant_edges = (
                [curr_edge]
                + list(street_network.graph.edges(curr_edge[0]))
                + list(street_network.graph.edges(curr_edge[1]))
            )

            # add their quality values to Q[next_index]
            max_likelihood = -np.inf
            for edge in relevant_edges:
                if (edge, curr_edge) not in Q[next_index].keys():
                    track_edge_start = track.utm(segment, next_index - 1)
                    track_edge_end = track.utm(segment, next_index)
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
                    Q[next_index][(edge, curr_edge)] = likelihood_edge(
                        track_edge_end,
                        street_edge_start,
                        street_edge_end,
                    )
                if Q[next_index][(edge, curr_edge)] > max_likelihood:
                    next_edge = edge
                    max_likelihood = Q[next_index][(edge, curr_edge)]

            # if no possible edge could be found, go back one step
            # TODO: Is this even possible?
            if next_edge == (None, None):
                Q[next_index - 1][(curr_edge, edges[next_index - 2])] = 0
                edges[next_index - 1] = (None, None)
                next_index -= 1
                continue

            # update the Q values of the previous step
            Q_change = Q[next_index][(next_edge, curr_edge)]
            if next_index == 1:
                Q[0][curr_edge] += Q_change
            else:
                Q[next_index - 1][
                    (curr_edge, edges[next_index - 2])
                ] += Q_change
            for edge in relevant_edges:
                Q[next_index][(edge, curr_edge)] -= Q_change

            # check if there is now an edge at time next_index-1 that has a
            # higher Q value
            go_back = False
            if next_index == 1:
                relevant_prev_edges = list(Q[0].keys())
                for edge in list(Q[0].keys()):
                    if Q[0][edge] > Q[0][curr_edge]:
                        go_back = True
                        break
            else:
                # relevant_prev_edges are defined analogously to relevant_edges
                relevant_prev_edges = (
                    [prev_edge]
                    + list(street_network.graph.edges(prev_edge[0]))
                    + list(street_network.graph.edges(prev_edge[1]))
                )
                for edge in relevant_prev_edges:
                    if (
                        Q[next_index - 1][(edge, prev_edge)]
                        > Q[next_index - 1][(curr_edge, prev_edge)]
                    ):
                        go_back = True

            # go back one step if last step is now non-optimal
            if go_back:
                edges[next_index - 1] = (None, None)
                next_index -= 1
                continue

            # go one step forward
            edges[next_index] = next_edge
            next_index += 1

        # build the graph from the edges
        graph = nx.Graph()
        graph.add_node(0, **street_network.graph.nodes[edges[0][0]])
        for i, edge in enumerate(edges):
            graph.add_node(i + 1, **street_network.graph.nodes[edge[1]])
            graph.add_edge(i, i + 1)

        # append final path to all paths
        paths.append(graph)

    return paths
