import osmnx as ox
import numpy as np
from tqdm import tqdm

from MotionMap.plot_graph import plot_graph

def snap_path(coords, G, start_index, dist_threshold, debug = False):
    # store the path of the activity in a list
    nodes_act = [0 for _ in range(len(coords))]
    dists = [np.inf for _ in range(len(coords))]
    
    # list containing forbidden nodes
    forbidden_nodes = [set() for _ in range(len(coords))]

    # start node is the closest node to the start coords
    start_node, start_dist = ox.distance.nearest_nodes(G, coords[start_index]["x"],
                                                       coords[start_index]["y"],
                                                       return_dist=True)
    # set appropriate first entry in resulting path
    nodes_act[start_index] = start_node
    dists[start_index] = start_dist
    
    # index for going through the coords
    i = start_index + 1
    highscore = start_index
    while i < len(coords):
        if i <= start_index:
            print("Did not find a path")
            break
        # previous node in nodes_act
        from_node = nodes_act[i-1]
        # calculate distance from from node
        from_coord_dist = ox.distance.great_circle(G.nodes[from_node]["y"],
                                                       G.nodes[from_node]["x"],
                                                       coords[i]["y"], coords[i]["x"])
        # get neighbors
        out_neighbors = [e[1] for e in G.out_edges(from_node)]
        in_neighbors = [e[0] for e in G.in_edges(from_node)]
        neighbors = list(set(out_neighbors + in_neighbors))

        # get non-forbidden neighbors
        candidates = [node for node in neighbors if node not in forbidden_nodes[i]]

        # check if any node is possible
        if len(candidates) == 0 and from_node in forbidden_nodes[i]:
            # go back one steps so the previous node gets set again
            forbidden_nodes[i-1].add(to_node)
            dists[i-1] = np.inf
            nodes_act[i-1] = 0
            i -= 1
            continue


        to_node = from_node
        to_coord_dist = from_coord_dist
        
        if len(candidates) != 0:
            # calculate bearing from from_node for coord
            from_coord_bearing = ox.bearing.calculate_bearing(G.nodes[from_node]["y"],
                                                              G.nodes[from_node]["x"],
                                                              coords[i]["y"], coords[i]["x"])

            # calculate bearings from from_node for all candidates
            from_candidate_bearings = {node: ox.bearing.calculate_bearing(G.nodes[from_node]["y"],
                                                                          G.nodes[from_node]["x"],
                                                                          G.nodes[node]["y"],
                                                                          G.nodes[node]["x"])
                                       for node in candidates}
            # calculate bearing_diffs
            bearing_diffs = {node: np.abs(from_coord_bearing - from_candidate_bearings[node])
                             for node in candidates}
            for node in candidates:
                if bearing_diffs[node] > 180:
                    bearing_diffs[node] = 360 - bearing_diffs[node]

            # get node with minimal bearing_diff
            to_node = min(bearing_diffs, key=bearing_diffs.get)
            
            # get distance between coord and to_node
            to_coord_dist = ox.distance.great_circle(G.nodes[to_node]["y"],
                                                     G.nodes[to_node]["x"],
                                                     coords[i]["y"], coords[i]["x"])
            
            # get distance between from_node and to_node
            from_to_dist = ox.distance.great_circle(G.nodes[to_node]["y"],
                                                        G.nodes[to_node]["x"],
                                                        G.nodes[from_node]["y"],
                                                        G.nodes[from_node]["x"])

            # take no step if coord is closer to from_node than to to_node
            if from_node not in forbidden_nodes[i] and from_coord_dist < to_coord_dist:
                to_node = from_node
                to_coord_dist = from_coord_dist

        # update list
        dists[i] = to_coord_dist
        nodes_act[i] = to_node

        forbidden = to_node in forbidden_nodes[i]

        # check if we should skip a node of G because they are too close together
        if not forbidden and from_to_dist < from_coord_dist and from_coord_dist > to_coord_dist:
            coords.insert(i+1, coords[i])
            nodes_act.append(0)
            dists.append(np.inf)
            forbidden_nodes.append(set())

            # do not check for pathological path in this case
            i += 1
            continue

        if debug:
            print(f"{i}:\tnode: {nodes_act[i]}")
            print(f"\tfrom_node: {from_node}")
            print(f"\tdistance: {dists[i]}")
            print(f"\tforbidden: {forbidden_nodes[i]}")
            print(f"\tcandidates: {candidates}")

        # check for pathological path
        if forbidden or (to_coord_dist > from_to_dist and to_coord_dist > dist_threshold):
            if debug and i > highscore:
                highscore = i
                plot_graph(G, nodes_act, coords=coords, node_size=15)

            # add to_node to forbidden nodes and try to place it again
            forbidden_nodes[i].add(to_node)
            dists[i] = np.inf
            nodes_act[i] = 0
            i -= 1
        i += 1

    return nodes_act, dists
