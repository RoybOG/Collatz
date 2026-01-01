import sympy as s


s.init_printing()

def calcMap(m_list):
    """Build an unevaluated SymPy expression and show it before evaluating.
    Print its LaTeX representation and then the evaluated result (also in LaTeX).
    """
    base = s.Integer(2)
    exp = s.Integer(4)
    # use evaluate=False so the expression stays symbolic (printed as 2**4)
    exr = s.Pow(base, exp, evaluate=False)

    # symbolic expression
    print("Expression:", exr)
    print("LaTeX:", f"${s.latex(exr)}$")

    # evaluated (exact integer) and its LaTeX
    evaluated = exr.doit()
    print("Evaluated:", evaluated)
    print("Evaluated LaTeX:", f"${s.latex(evaluated)}$")


calcMap([])