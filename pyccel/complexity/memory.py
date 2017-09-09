# coding: utf-8

from sympy import sympify, simplify, Symbol, Add
from sympy import preorder_traversal
from sympy.core.expr import Expr
from sympy.core.singleton import S
from sympy.tensor.indexed import Idx

from pyccel.parser  import PyccelParser
from pyccel.syntax import ( \
                           # statements
                           AssignStmt, MultiAssignStmt, \
                           IfStmt, ForStmt,WhileStmt \
                           )

from pyccel.types.ast import (For, Assign, Declare, Variable, \
                              datatype, While, NativeFloat, \
                              EqualityStmt, NotequalStmt, \
                              Argument, InArgument, InOutArgument, \
                              MultiAssign, OutArgument, Result, \
                              FunctionDef, Import, Print, \
                              Comment, AnnotatedComment, \
                              IndexedVariable, Slice, If, \
                              ThreadID, ThreadsNumber, \
                              Rational, NumpyZeros, NumpyLinspace, \
                              Stencil,ceil, \
                              NumpyOnes, NumpyArray, LEN, Dot, Min, Max,IndexedElement)

from pyccel.complexity.basic     import Complexity
from pyccel.complexity.operation import count_ops

__all__ = ["count_access", "MemComplexity"]

# ...
def count_access(expr, visual=True, local_vars=[]):
    """
    returns the number of access to memory in terms of WRITE and READ.

    expr: sympy.Expr
        any sympy expression or pyccel.types.ast object
    visual: bool
        If ``visual`` is ``True`` then the number of each type of operation is shown
        with the core class types (or their virtual equivalent) multiplied by the
        number of times they occur.
    local_vars: list
        list of variables that are supposed to be in the fast memory. We will
        ignore their corresponding memory accesses.
    """
    if not isinstance(expr, (Assign, For)):
        expr = sympify(expr)

    ops   = []
    WRITE = Symbol('WRITE')
    READ  = Symbol('READ')

    local_vars = [str(a) for a in local_vars]

    if isinstance(expr, Expr):
        indices = []
        for arg in preorder_traversal(expr):
            if isinstance(arg, Idx):
                for a in arg.free_symbols:
                    indices.append(str(a))

        atoms = expr.atoms(Symbol)
        atoms = [str(i) for i in atoms]

        atoms      = set(atoms)
        indices    = set(indices)
        local_vars = set(local_vars)
        ignored = indices.union(local_vars)
        atoms = atoms - ignored
        ops = [READ]*len(atoms)
    elif isinstance(expr, Assign):
        if isinstance(expr.lhs, IndexedElement):
            name = str(expr.lhs.base)
        else:
            name = str(expr.lhs)
        ops  = [count_access(expr.rhs, visual=visual, local_vars=local_vars)]
        if not name in local_vars:
            ops += [WRITE]
    elif isinstance(expr, For):
        b = expr.iterable.args[0]
        e = expr.iterable.args[1]
        if isinstance(b, Symbol):
            local_vars.append(b)
        if isinstance(e, Symbol):
            local_vars.append(e)
        ops = [count_access(i, visual=visual, local_vars=local_vars) for i in expr.body]
        ops = [i * (e-b) for i in ops]
    elif isinstance(expr, (NumpyZeros, NumpyOnes)):
        ops = []

    if not ops:
        return S.Zero

    ops = simplify(Add(*ops))

    return ops
# ...

# ...
def free_parameters(expr):
    """
    Returns the free parameters of a given expression. In general, this
    corresponds to length of a For loop.

    expr: sympy.Expr
        any sympy expression or pyccel.types.ast object
    """
    args = []
    if isinstance(expr, For):
        b = expr.iterable.args[0]
        e = expr.iterable.args[1]
        if isinstance(b, Symbol):
            args.append(str(b))
        if isinstance(e, Symbol):
            args.append(str(e))
        for i in expr.body:
            args += free_parameters(i)
        args = set(args)
        args = list(args)

    return args
# ...

# ...
from sympy import Poly, LT
def leading_term(expr, *args):
    """
    Returns the leading term in a sympy Polynomial.

    expr: sympy.Expr
        any sympy expression

    args: list
        list of input symbols for univariate/multivariate polynomials
    """
    expr = sympify(str(expr))
    P = Poly(expr, *args)
    return LT(P)
# ...

# ...
class MemComplexity(Complexity):
    """
    Class for memory complexity computation.
    This class implements a simple two level memory model
    """

    @property
    def free_parameters(self):
        """
        Returns the free parameters. In general, this
        corresponds to length of a For loop.
        """
        # ...
        args = []
        for stmt in self.ast.statements:
            if isinstance(stmt, ForStmt):
                args += free_parameters(stmt.expr)
        # ...
        args = [Symbol(i) for i in args]
        return args

    def cost(self, local_vars=[]):
        """
        Computes the complexity of the given code.

        local_vars: list
            list of variables that are supposed to be in the fast memory. We will
            ignore their corresponding memory accesses.
        """
        # ...
        m = S.Zero
        f = S.Zero
        # ...

        # ...
        for stmt in self.ast.statements:
            if isinstance(stmt, (AssignStmt, ForStmt)):
                m += count_access(stmt.expr, visual=True, local_vars=local_vars)
                f += count_ops(stmt.expr, visual=True)
        # ...

        # ...
        m = simplify(m)
        f = simplify(f)
        # ...

        # ...
        d = {}
        d['m'] = m
        d['f'] = f
        # ...

        return d

    def intensity(self, d=None, args=None):
        """
        Returns the computational intensity for the two level memory model.

        d: dict
            dictionary containing the floating and memory costs. if not given,
            we will compute them.
        args: list
            list of free parameters, i.e. degrees of freedom.
        """
        # ...
        if d is None:
            d = self.cost(local_vars=['r', 'u', 'v'])
        # ...

        # ...
        if args is None:
            args = self.free_parameters
        # ...

        # ...
        f = d['f']
        m = d['m']
        lt_f = leading_term(f, *args)
        lt_m = leading_term(m, *args)
        # ...

        return lt_f/lt_m
# ...

##############################################
if __name__ == "__main__":
    import sys
    filename = sys.argv[1]

    M = MemComplexity(filename)
    d = M.cost(local_vars=['r', 'u', 'v'])

    f = d['f']
    m = d['m']
    print "f = ", f
    print "m = ", m

    q = M.intensity()
    print ">>> computational intensity ~", q

#    # ... computational intensity
#    q = f / m
#    q = simplify(q)
#    t_f = Symbol('t_f')
#    t_m = Symbol('t_m')
#    c = f * t_f + m * t_m
#    # ...

