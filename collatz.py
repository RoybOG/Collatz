import sympy
from fractions import Fraction
import os 
import networkx as nx
from dataclasses import dataclass
import re 
import itertools

@dataclass
class RegexEqual(str):
    string: str
    match: re.Match = None

    def __eq__(self, pattern):
        self.match = re.search(pattern, self.string)
        return self.match is not None
    
    def __getitem__(self, group):
        return self.match[group]
    


def collatz_sequence(n, max_tries=None):
    """
    Generator that yields the Collatz sequence starting from n.
    If max_tries is provided, will stop after that many iterations.
    """
    tries = 0
    current = n
    
    while current != 1:
        yield current
        
        if max_tries and tries >= max_tries:
            break
            
        if current % 2 == 0:
            current = current // 2
        else:
            current = 3 * current + 1
            
        tries += 1
    
    yield current  # Yield the final 1



# Example usage

def log_sequence(n, max_tries=None, ):
    os.makedirs('./collatz_calcs', exist_ok=True)
    filename=f'./collatz_calcs/collatz_log_for_{n}.csv'
    with open(filename, 'w') as f:
        # f.write(f"\nTesting {n} (max tries: {max_tries}):\n")
        
        formulaCalc = lambda i: (n+1)*((Fraction(3,2))**(i-1))-1
        n_path = list(collatz_sequence(n, max_tries=max_tries))
        
        # Log each number and its prime factorization
        last_four_multiple_index=0
        f.write(', '.join(['index','number','factorization','distance from power of 2','reminder mod 4', 'is peak'])+ '\n')
        for i,num in enumerate(n_path):
            factors = sympy.ntheory.factorint(num)
            fstr = ' * '.join([f'{k}^{v}' for k,v in factors.items()])
            #f.write(f'{num} = {factors}\n')
            factors.pop(2, None)
            distFromPowerOfTwo = sum(factors.values())
            f.write(', '.join([str(v) for v in [i,num, fstr, distFromPowerOfTwo, num%4, " peak" if num%4==0 else '']]) + '\n')
                    

        


def build_graph(itr):
    G = nx.DiGraph()
    def add_to_graph(num):
        for pair in itertools.pairwise(collatz_sequence(num)):
            G.add_edge(*pair)
            # Store both mod4 and mod6 values
            G.nodes[pair[0]]['mod6'] = pair[0] % 6


    for i in itr:
        if G.has_node(i):
            continue
        add_to_graph(i)
        log_sequence(i)
    
    return G




def interpret_input(s):
    itr = None
    match RegexEqual(s):
        case '^([0-9]*)$' as capture:
            print(f'number {capture[1]}')
            itr = [int(capture[1])]

        case '^([0-9]*)?\-([0-9]*)$' as capture:
            print(f'range4-4 min:{capture[1] or 3} max:{capture[2]}')
            itr = range(int(capture[1] or 3), int(capture[2])+1)
        
        case r"^(\d+)(\s*\,\s*\d+)*$" as capture:
            print("list")
            
            itr = [int(n) for n in re.findall(r"\d+", capture[0])]
            
        case _:
            print('wrong, try again')
            raise TypeError("Wrong try again")
    
    return build_graph(itr)
    


def main(): 
    try:

        G = interpret_input(input("Enter number: \n"))
    except TypeError:
        main()



if __name__ == "__main__":
    log_sequence(int(input("Enter number: \n")))

