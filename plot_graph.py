import osmnx as ox
import shapely as shp

def plot_graph(G_orig, nodes_act, coords=list(), node_size=0):
    G = G_orig.copy()

    # node and edge color dicts
    node_colors = {node: 'w' for node in G.nodes}
    edge_colors = {edge: '#999999' for edge in G.edges}

    k = 0
    while k < len(nodes_act) and nodes_act[k] != 0:
        
        node_colors[nodes_act[k]] = 'green'
        
        if len(coords) == len(nodes_act):
            G.add_node(f"act_{k}", y=coords[k]["y"], x=coords[k]["x"])
            ls = shp.LineString([[G.nodes[nodes_act[k]]["y"], G.nodes[nodes_act[k]]["x"]],
                                 [coords[k]["y"], coords[k]["x"]]])
            G.add_edge(f"act_{k}", nodes_act[k])
            node_colors[f"act_{k}"] = 'orange'
            edge_colors[(f"act_{k}", nodes_act[k])] = 'orange'
        
        if k == 0:
            k += 1
            continue
        from_node = nodes_act[k-1]
        to_node = nodes_act[k]
        if from_node == to_node:
            k += 1
            continue
        edge_colors[(from_node, to_node, 0)] = 'green'
        edge_colors[(to_node, from_node, 0)] = 'green'

        k += 1

    if 0 < k < len(nodes_act):
        node_colors[f"act_{k-1}"] = 'red'
        edge_colors[(f"act_{k-1}", nodes_act[k-1])] = 'red'
        edge_colors[(nodes_act[k-1], f"act_{k-1}")] = 'red'
        for e in G.out_edges(nodes_act[k-1]):
            edge_colors[(e[0], e[1], 0)] = 'blue'
        for e in G.in_edges(nodes_act[k-1]):
            edge_colors[(e[0], e[1], 0)] = 'blue'

    ox.plot_graph(G, node_size=node_size, node_color=list(node_colors.values()), edge_color=list(edge_colors.values()))

