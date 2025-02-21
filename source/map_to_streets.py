import networkx as nx

from source.plot import *
from source.track import *
from source.utility import likelihood_edge, likelihoods_first_edge


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
        # list that contains the calculated likelihoods
        # of different edges at different time points
        L = [dict() for _ in range(track.len(segment))]
        # list that contains the maximum likelihood in every step

        # current most probable edge list
        edges = [(None, None) for _ in range(track.len(segment))]
        # index of the next edge for the currently most probable path
        next_index = 0

        # get likelihoods for starting nodes
        L[0] = likelihoods_first_edge(track.utm(segment, 0), street_network)

        # loop until we got the most probable complete path
        while next_index < track.len(segment):
            # DEBUG
            if next_index > 0:
                if next_index > 1:
                    print(
                        next_index,
                        L[next_index - 1][
                            (edges[next_index - 1], edges[next_index - 2])
                        ],
                        L[0][(518671757, 1752315539)],
                    )
                else:
                    print(
                        next_index,
                        L[next_index - 1][edges[next_index - 1]],
                        L[0][(518671757, 1752315539)],
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
            # DEBUG

            # get relevant likelihoods for the next step and proposed edge
            next_edge = (None, None)
            if next_index == 0:
                next_edge = max(L[0], key=L[0].get)
                # go one step forward
                edges[next_index] = next_edge
                next_index += 1
                continue

            # shorthand for current and previous edge
            curr_edge = edges[next_index - 1]
            prev_edge = edges[next_index - 2]

            # get relevant edges
            relevant_edges = (
                [edges[next_index - 1]]
                + list(street_network.graph.edges(edges[next_index - 1][0]))
                + list(street_network.graph.edges(edges[next_index - 1][1]))
            )
            # store their likelihoods in L
            max_likelihood = 0
            for edge in relevant_edges:
                if (edge, curr_edge) not in L[next_index].keys():
                    L[next_index][(edge, curr_edge)] = likelihood_edge(
                        track.utm(segment, next_index),
                        street_network.utm(edge[0]),
                        street_network.utm(edge[1]),
                    )
                if L[next_index][(edge, curr_edge)] > max_likelihood:
                    next_edge = edge
                    max_likelihood = L[next_index][(edge, curr_edge)]

            if next_edge == (None, None):
                L[next_index - 1][(curr_edge, edges[next_index - 2])] = 0
                edges[next_index - 1] = (None, None)
                next_index -= 1
                continue

            if next_index > 1:
                L[next_index - 1][(curr_edge, edges[next_index - 2])] *= L[
                    next_index
                ][(next_edge, curr_edge)]
            else:
                L[next_index - 1][curr_edge] *= L[next_index][
                    (next_edge, curr_edge)
                ]
            L[next_index][(next_edge, curr_edge)] = 1

            # go back one step if last step is now non-optimal
            go_back = False
            relevant_prev_edges = list()
            if next_index > 1:
                relevant_prev_edges = (
                    [edges[next_index - 2]]
                    + list(street_network.graph.edges(prev_edge[0]))
                    + list(street_network.graph.edges(prev_edge[1]))
                )
                for edge in relevant_prev_edges:
                    if (
                        L[next_index - 1][(edge, prev_edge)]
                        > L[next_index - 1][(curr_edge, prev_edge)]
                    ):
                        go_back = True
                        break
            else:
                relevant_prev_edges = list(L[0].keys())
                for edge in relevant_prev_edges:
                    if L[next_index - 1][edge] > L[next_index - 1][curr_edge]:
                        go_back = True
                        break
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
