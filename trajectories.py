import sympy as sym
import re
import dataclasses

class trajectory:
    pass


def calculate_trajectory(l, ):

   

    raise_to_pow_2_latex = lambda e: f'2^{e}'


    raise_to_pow_2 = lambda e: 2**(e)
    
    exponent =next(l,0)
    
        
    num = raise_to_pow_2(exponent)

    latex = raise_to_pow_2_latex(exponent)

    for exponent in l:
        print( num )
        if num % 3 !=1:
            raise ValueError("The trajectory is leading to a non integer!")
        

        num = ((num -1) // 3) * raise_to_pow_2(exponent)

        latex = r"\frac{" +latex+ "-1}{3}*{"+raise_to_pow_2_latex(exponent)+"}"

    print(latex)
    return num


def main():

    user_str = input("Enter exponnents:\n")
    m =re.search(r"(\d+)(?:\s*\,\s*(\d+))+", user_str) 
    if m:
        user_str =  m.group()
        g = ",".split(user_str)
        itr = (int(n.group()) for n in re.finditer(r"\d+", user_str))
        print(sym.latex(calculate_trajectory(itr)))
    else:
        print('invalid input')
            
            # itr = [int(n) for n in re.findall(r"\d+", capture[0])]

if __name__ == "__main__":
    while True:
        main()

