import sympy
import base64
import json
from fractions import Fraction
import os 
import networkx as nx
from networkx.readwrite import json_graph
from dataclasses import dataclass
import re 
import pandas as pd
import itertools
from InquirerPy import inquirer
from InquirerPy.base import Choice
from html import escape

import mermaid as md
from mermaid.graph import Graph

from jinja2 import Environment, FileSystemLoader

# Set up the environment
# The FileSystemLoader tells Jinja where to look for template files
temp_env = Environment(loader=FileSystemLoader('Assets'))


@dataclass
class RegexEqual(str):
    string: str
    match: re.Match = None

    def __eq__(self, pattern):
        self.match = re.search(pattern, self.string)
        return self.match is not None
    
    def __getitem__(self, group):
        return self.match[group]





def incLast(l):
        if len(l) > 0:
            l[-1] = l[-1]+1
        return l

def addNumberToCollatzGraph(G, n,sideInfos=None, determineColor=None):
    
    sideInfos = sideInfos or {}

    def getFractionForm(n):
        
        next_num = 0
        fraction_form =  [0]
        distance_from_one = 0
        already_in_graph = n in G.nodes

        if n!=1:
            if n %2==1:
                next_num = 3*n+1
                distance_from_one, fraction_form = getFractionForm(next_num)
                fraction_form = fraction_form + [0]
            
            else:
                next_num = n//2
                distance_from_one, fraction_form = getFractionForm(next_num)
                fraction_form = incLast(fraction_form)
        
        # print(f'{n}: {fraction_form}')
        
            G.add_edge(n, next_num)
        
        if (not already_in_graph) or (n==1):
            for title, f in sideInfos.items():
                G.nodes[n][title] = f(n, G)
            
            G.nodes[n]["color"] = determineColor(n,G)
            G.nodes[n]["distanceFromOne"] = distance_from_one
            
        # if "MapFromOne" not in G.nodes[n]:
            G.nodes[n]["MapFromOne"] = fraction_form.copy() #Prevents the adding one to same list in memory as the privous one

        return distance_from_one + 1, fraction_form

    getFractionForm(n)
    #G.nodes[1]["MapFromOne"] =[]
    return G #, getFractionForm(n)

# Example usage


def generate_collatz(itr,sideInfos=None, determineColor=None):
    G = nx.DiGraph()
    G.add_node(1)

    for n in itr:
        addNumberToCollatzGraph(G,n,sideInfos=sideInfos, determineColor=determineColor)

    return G

def generate_mermaid_link(graph_code):
    # Define the state object
    state = {
        "code": graph_code,
        "mermaid": {"theme": "default"},
        "updateEditor": True
    }
    
    # Convert to JSON string
    json_str = json.dumps(state)
    
    # Encode to Base64
    # Note: Use urlsafe_b64encode if you find padding issues, 
    # but standard b64 is usually fine for mermaid.live
    encoded = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
    
    l = f"https://mermaid.live/view#base64:{encoded}"
    print("\n link to graph")
    print(l)
    print()

    return l

2

def generate_mermaid_code(g,sideInfos=None, determineColor=None):
    
    
    getNodeID = lambda nodeNum: f'n{str(nodeNum)}'


    def getNodeDetails(n):
        
        s = f'["`**{n}**'
        
        if sideInfos:
            s = s + f'\n**MapToOne**: {g.nodes[n].get("MapFromOne","")}'+ '\n'
            for title in sideInfos.keys():
                r =  g.nodes[n][title]
                if str(r):
                    s = s + f'\n**{title}**: {r}'



        s = s +'`"]'

        if determineColor:
           c = g.nodes[n]["color"]
           if c:
               s = s + f':::{c}'

        g.nodes[n]["detailedInCode"]=True
        return s

    getNodeText = lambda n: getNodeID(n)+ ("" if g.nodes[node].get("detailedInCode",False) else getNodeDetails(n))


    mermaid_code = """---
config:
   flowchart:
    nodeSpacing: 100
    rankSpacing: 120
---
flowchart TD
classDef red stroke:red,stroke-width: 3px;
classDef green stroke:green,stroke-width: 3px;
classDef blue stroke:blue,stroke-width: 3px;
"""
    mermaid_code =mermaid_code + f'\n{getNodeID(1)+getNodeDetails(1)}'


    for node in g: 
        print(f'{node}->{list(g.neighbors(node))}')
        for niehgbour in g.neighbors(node):
            mermaid_code += f'\n{getNodeText(node)}-->{getNodeText(niehgbour)}'

    return mermaid_code
        
    


def export_to_mermaid_graph(g,fileName,sideInfos=None, determineColor=None):
    
    
    mermaid_code = generate_mermaid_code(g,sideInfos, determineColor)
    
    os.makedirs('./mermaid_graphs', exist_ok=True)
    
    file_path = f'./mermaid_graphs/{fileName}.mmd'
    
    if not os.path.isfile(file_path): #If a graph file was created already, a link was appened too
        with open('./graphLinks.md', "a") as f:
            f.write(f"* [{fileName}]({generate_mermaid_link(mermaid_code)})\n") 

    with open(file_path, "w") as f:
        f.write(mermaid_code)


def interpret_input(s):
    itr = None
    match RegexEqual(s):
        case '^([0-9]*)$' as capture:
            print(f'number {capture[1]}')
            itr = [int(capture[1])]

        case '^([0-9]*)?-([0-9]*)$' as capture:
            print(f'range4-4 min:{capture[1] or 3} max:{capture[2]}')
            itr = range(int(capture[1] or 3), int(capture[2])+1)
        
        case r"^(\d+)(\s*\,\s*\d+)*$" as capture:
            print("list")
            
            itr = [int(n) for n in re.findall(r"\d+", capture[0])]
            
        case _:
            print('wrong, try again')
            raise SyntaxError("Wrong try again")
    
    return itr
    
def export_nodes_to_csv(g,fileName,sideInfos=None, determineColor=None):
    df = pd.DataFrame(index=g.nodes())
    
    df["MapFromOne"] = pd.Series(nx.get_node_attributes(g, "MapFromOne"))
    for info in sideInfos.keys():
        df[info] = pd.Series(nx.get_node_attributes(g, info))
    
    df["color"] = pd.Series(nx.get_node_attributes(g, "color"))
    df["distanceFromOne"] = pd.Series(nx.get_node_attributes(g, "distanceFromOne"))

    df= df.sort_index(ascending=True)
    
    os.makedirs('./graph_csvs', exist_ok=True)

    
    file_path = f'./graph_csvs/{fileName}.csv'

    df.to_csv(file_path)


def export_mermaid_to_html(g,fileName,sideInfos=None, determineColor=None):
    
    
    mermaid_code = generate_mermaid_code(g,sideInfos, determineColor)
    
    g = Graph(title=fileName,script=mermaid_code)

    

    os.makedirs('./mermaid_graphs', exist_ok=True)
    


    file_path = f'./mermaid_graphs/{fileName}.svg'

    g.render(output_file="file_path")
    # t = temp_env.get_template("graph_temp.html")
    # html_code = t.render({"mermaid_code":mermaid_code})

    # with open(file_path, "w") as f:
    #     f.write(html_code)


    print(os.path.abspath(file_path))

    
    

EXPORT_OPTIONS = {
   
    "Mermaid Graph": export_to_mermaid_graph,
      "Nodes CSV": export_nodes_to_csv,
      "ToHTML": export_mermaid_to_html
    #  "Text File": None
}


DEFAULT_EXPORT_OPTIONS = ["Mermaid Graph"]

def chooseExport(G, graphName,sideInfos=None, determineColor=None):

    fileName = graphName + f'({", ".join(sideInfos.keys()) if isinstance(sideInfos, dict) else ""})'

    selected = inquirer.checkbox(
        message="Choose methods to export the graph:",
        choices = [ Choice(k, enabled= (k in DEFAULT_EXPORT_OPTIONS)) for k in EXPORT_OPTIONS.keys()],
        validate=lambda result: len(result) >= 1,
        invalid_message="should be at least 1 selection",
        instruction="(select at least 1)",
    ).execute()

    for choise in selected:
        EXPORT_OPTIONS[choise](G, fileName, sideInfos, determineColor)


def r(user_numbers,graphName,sideInfos=None, determineColor=None):
    
    G = generate_collatz(user_numbers,sideInfos=sideInfos, determineColor=determineColor)
    chooseExport(G, graphName,sideInfos=sideInfos, determineColor=determineColor)



def main(): 
    try:
        
        prompt = input("Enter number/s: \n")
        user_numbers = interpret_input(prompt)
        #G = generate_collatz(user_numbers)
        r(user_numbers,prompt,{ "Mod6": lambda n, g: n%6},lambda n,g: 'green' if n%2 else '')
        # export_nodes_to_csv(G,prompt,{"MapFromOne": lambda n, g: g.nodes[n].get("MapFromOne","")},lambda n,g: 'green' if n%2 else '')
    except SyntaxError:
        main()



if __name__ == "__main__":
#   while True:
    main()