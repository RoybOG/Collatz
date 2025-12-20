from ete3 import Tree, TextFace, TreeStyle, add_face_to_node
import networkx as nx
from collatz import collatz_sequence,build_graph,interpret_input
import os

def nx_to_newick(G):
    """
    Converts a NetworkX tree/DAG (DiGraph) to a Newick string.

    Args:
        G (nx.DiGraph): The NetworkX graph (must be a tree or a DAG).
        root_node: The starting node (root) of the tree.
        
    Returns:
        str: The Newick formatted string.
    """
    root=1

    eteTree = Tree(name=1)

    def recur_to_ete(current_node_num, current_new_node):
        
        for child_num in G.predecessors(current_node_num):
            c = current_new_node.add_child(name=child_num) 
            recur_to_ete(child_num,c)

    recur_to_ete(1,eteTree)

    return eteTree


    
    # 1. Initialize the root node for the ETE tree

def dual_label_layout(node):
    """
    Layout function that adds the node's name (in blue) and a custom 
    property (mod6, in red) next to the node.
    """
    
    # --- Part 1: Display the Main Node Name ---
    
    # 1. Check if the node has a name to display
    if node.name:
        # Create a face for the node's main identifier
        name_face = TextFace(str(node.name), fsize=10, fgcolor="blue")
        
        # Add the main name face to the node (left-aligned)
        add_face_to_node(name_face, node, column=0, position="branch-right")

    # --- Part 2: Display the Custom Number (e.g., mod 6) ---
    
    # 2. Check if the node has the custom property (replace 'mod6' with your actual attribute)
    if hasattr(node, "mod6"):
        # Get the custom value
        mod_value = str(node.mod6)
        
        # Create a face for the custom number
        mod_face = TextFace(f' ({mod_value})', fsize=8, fgcolor="red")
        
        # Add the custom face immediately to the right of the name (column=1)
        add_face_to_node(mod_face, node, column=1, position="branch-right")

def get_tree_style_for_labels(ete_tree):
    # 1. Define the TreeStyle
    ts = TreeStyle()
    
    # Use the custom layout function
    ts.layout_fn = dual_label_layout 
    ts.branch_vertical_margin = 10
    # Set display options
    ts.show_branch_length = False
    ts.show_leaf_name = False # Disable default names so we control their placement
    ts.mode = "r" 

    return ts
    # 2. Show the tree
    


def drawGraph(G,prompt="t"):  
# --- Setup Example Data ---
# Create a tree (the names are the numbers)
    t = nx_to_newick(G)
    os.makedirs('./collatz_graph', exist_ok=True)
    filename=f'./collatz_graph/{prompt}.nw' #.svg'
    # Traverse and assign the custom 'mod6' property to each node
    for node in t.traverse("levelorder"):
        try:
            # Assume node names are convertible to integers for the Collatz graph
            num = int(node.name)
            node.add_features(mod6=num % 6)
        except ValueError:
            # Handle cases where internal node names aren't numbers (e.g., empty or "I1")
            node.add_features(mod6='-') 

    ts = get_tree_style_for_labels(t)
    # t.render(filename,tree_style=ts)
    t.write(format=8, outfile=filename)
    t.show(tree_style=ts)
    

def generate_mermaid_code(g,prompt,sideInfos=None):
    
    
    getNodeID = lambda nodeNum: f'n{str(nodeNum)}'
    
    def getNodeDetails(n):
        
        s = f'["`###{n}'
        
        if sideInfos:
            for title, f in sideInfos.items():
                s = s + f'\n**{title}**: {f(n)}'
        
        s = s +'`"]'
        g.nodes[n]["detailedInCode"]=True
        return s

    getNodeText = lambda n: getNodeID(n)+ ("" if g.nodes[node].get("detailedInCode",False) else getNodeDetails(n))


    mermaid_code = """https://mermaidviewer.com/editor
    
    ---
config:
   flowchart:
    nodeSpacing: 100
    rankSpacing: 120
---
flowchart TD
"""
    mermaid_code =mermaid_code + f'\n{getNodeID(1)+getNodeDetails(1)}'


    for node in g: 
        print(f'{node}->{list(g.neighbors(node))}')
        for niehgbour in g.neighbors(node):
            mermaid_code += f'\n{getNodeText(node)}-->{getNodeText(niehgbour)}'

    os.makedirs('./collatz_graph', exist_ok=True)
    filename=f'./collatz_graph/{prompt}.mmd' #.svg'
    with open(filename, "w") as f:
        f.write(mermaid_code)
        
        

if __name__ == "__main__":
    prompt = '3-26'  #'3,9,15,21,33,39,27'#input("Enter number: \n")
    #
    generate_mermaid_code(interpret_input(prompt),prompt, {"mod 6":lambda n: n%6})
    drawGraph(interpret_input(prompt),prompt)
    
    #nx_to_newick(G)


