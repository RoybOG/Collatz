import networkx as nx

import matplotlib.pyplot as plt
from collatz import collatz_sequence,build_graph
import re 
import EoN
import numpy as np
import ete3 


def zoom_factory(event, base_scale=1.2):
    """
    Implement zoom functionality for the graph
    """
    ax = event.inaxes
    if ax is None:
        return
    
    cur_xlim = ax.get_xlim()
    cur_ylim = ax.get_ylim()
    
    xdata = event.xdata
    ydata = event.ydata
    
    if event.button == 'up':
        scale_factor = 1/base_scale
    elif event.button == 'down':
        scale_factor = base_scale
    else:
        scale_factor = 1
    
    new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
    new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
    
    ax.set_xlim([xdata - new_width/2, xdata + new_width/2])
    ax.set_ylim([ydata - new_height/2, ydata + new_height/2])
    
    plt.draw()


    

def old_draw_graph(G):
    plt.figure(figsize=(12, 10))
    
    pos = nx.spring_layout(G, k=0.15) #nx.kamada_kawai_layout(G)
    
    pos_inverted = {node: (x, -y) for node, (x, y) in pos.items()}
    
    min_y = min(y for x, y in pos_inverted.values())
    max_y = max(y for x, y in pos_inverted.values())
    
    for node in pos_inverted:
        x, y = pos_inverted[node]
        if node == 1:
            pos_inverted[node] = (x, min_y)
        else:
            pos_inverted[node] = (x, y)
    
    # Draw edges and nodes first
    nx.draw(G, pos=pos_inverted,
            with_labels=True,
            font_weight='bold',
            node_color='lightblue',
            node_size=800,
            width=1.5,
            edge_color='gray',
            arrows=False)
        
    
    # Add mod 6 labels
    for node, (x, y) in pos_inverted.items():
        mod6 = node % 6
        plt.text(x + 0.05, y, f'({mod6})', 
                color='red',
                fontsize=8,
                verticalalignment='center')
    
    plt.title("Collatz Graph")
    plt.gcf().canvas.mpl_connect('scroll_event', lambda event: zoom_factory(event, base_scale=1.2))
    plt.show()



    


def draw_graph(G):
    
    # Create a layered (top-to-bottom) layout that covers all nodes.
    # Compute a level (distance) for each node per connected component so branches are separated.
    levels = {}
    undirected = G.to_undirected()
    for comp in nx.connected_components(undirected):
        # pick a root for the component; prefer 1 if present, else smallest node
        root = 1 if 1 in comp else min(comp)
        dist = nx.single_source_shortest_path_length(undirected, root)
        for n, d in dist.items():
            levels[n] = d

    # Group nodes by level
    level_nodes = {}
    for n, lvl in levels.items():
        level_nodes.setdefault(lvl, []).append(n)

    # Assign positions: x spread depends on number of nodes in that level; y decreases with level
    pos = {}
    max_width = max((len(nodes) for nodes in level_nodes.values()), default=1)
    # Increase horizontal spacing for wider trees and use a larger multiplier so branches don't overlap
    horiz_scale = max(12, max_width * 2.0)
    vgap = 2.0  # vertical gap between levels
    for lvl, nodes in sorted(level_nodes.items()):
        count = len(nodes)
        # sort nodes for more stable ordering (by value)
        nodes = sorted(nodes)
        if count == 1:
            xs = [0.0]
        else:
            xs = np.linspace(-horiz_scale/2, horiz_scale/2, count)
        y = -lvl * vgap  # top (0) to bottom (increasing lvl)
        for x, n in zip(xs, nodes):
            pos[n] = (float(x), float(y))
        

    # If there are isolated nodes not reached above (rare), place them on a new lower level
    missing = set(G.nodes()) - set(pos)
    if missing:
        start_lvl = max(level_nodes.keys(), default=0) + 1
        for i, n in enumerate(sorted(missing)):
            pos[n] = ((i - len(missing)/2) * 1.5, -start_lvl)

   
        
    plt.figure(figsize=(14, 10))
    nx.draw_networkx_edges(G, pos, arrows=True, arrowstyle='->', arrowsize=12, edge_color='gray', width=1.2)
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=700)
    nx.draw_networkx_labels(G, pos, labels={n: str(n) for n in G.nodes()}, font_weight='bold')

    # add small red "(mod6)" label next to each node using offset in points (keeps spacing stable when zooming)
    ax = plt.gca()
    for n, (x, y) in pos.items():
        mod6 = G.nodes[n].get('mod6', n % 6)
        ax.annotate(f'({mod6})',
                    xy=(x, y),
                    xytext=(8, 0),               # offset in points to the right
                    textcoords='offset points',
                    color='red',
                    fontsize=8,
                    va='center',
                    ha='left')

    plt.title("Collatz Graph")
    # re-enable scroll-to-zoom (centers on cursor)
    plt.gcf().canvas.mpl_connect('scroll_event', lambda event: zoom_factory(event, base_scale=1.2))
    plt.show()
    
    # plt.figure(figsize=(14, 10))
    # nx.draw(G, pos, with_labels=True)
    # plt.show()
    # Try multipartite layout for tree-like separation

    

    """
    pos_inverted = {node: (x, -y) for node, (x, y) in pos.items()}
    
    min_y = min(y for x, y in pos_inverted.values())
    max_y = max(y for x, y in pos_inverted.values())
    
    for node in pos_inverted:
        x, y = pos_inverted[node]
        if node == 1:
            pos_inverted[node] = (x, min_y)
        else:
            pos_inverted[node] = (x, y)

    # Draw the base graph first (directed)
    nx.draw(G, pos=pos_inverted,
        with_labels=True,
        font_weight='bold',
        node_color='lightblue',
        node_size=800,
        width=1.5,
        edge_color='gray',
        arrows=True,
        arrowstyle='-|>',
        arrowsize=18)
    
    # Add mod6 values from stored node attributes
    for node, (x, y) in pos_inverted.items():
        mod6 = G.nodes[node].get('mod6', node % 6)  # Fallback to calculation if not stored
        plt.text(x + 0.05, y, f'({mod6})', 
                color='red',
                fontsize=8,
                verticalalignment='center')
    
    plt.title("Collatz Graph")
    plt.gcf().canvas.mpl_connect('scroll_event', lambda event: zoom_factory(event, base_scale=1.2))
    plt.show()
    """



if __name__ == "__main__":
    main()
    
    


    # G = build_graph(20) #10)
    # draw_graph(G)


