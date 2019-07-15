"""
This module contains the 'collapse' clause's AST visitor for the 'loop' construct.
"""
import ast
import acc.frontend.util.errors as errors
import acc.frontend.util.util as util

class Loop:
    """
    Collection of data for loops, including source code and variables of interest.
    """
    def __init__(self, src: str, variables: []):
        self.src = src
        self.variables = list(variables)

class CollapseVisitor(ast.NodeVisitor):
    """
    This class gets all the loops in a batch of source code.
    """
    def __init__(self, atok):
        self.loops = []
        self.atok = atok

    def generic_visit(self, node):
        type_name = type(node).__name__

        if type_name == "comprehension":
            # TODO: We currently do not support parallelization of comprehensions
            pass
        elif type_name == "For":
            for_src = self.atok.get_text(node)
            ls_for_src = util.left_strip_src(for_src)
            loop_vars = list(set(util.get_variables_from_source(ls_for_src)))
            self.loops.append(Loop(ls_for_src, loop_vars))

        ast.NodeVisitor.generic_visit(self, node)

class CollapseClause:
    """
    All the information needed by the back-end for a loop's collapse clause.

    Items
    -----

    - loops : The list (in order of source from top to bottom) of for-loops to collapse. Type is collapse.Loop.

    From the docs
    -------------
    The collapse clause is used to specify how many tightly nested loops are associated with the
    loop construct. The argument to the collapse clause must be a constant positive integer expression.
    If no collapse clause appears, only the immediately following loop is associated with the
    loop construct.

    If more than one loop is associated with the loop construct, the iterations of all the associated loops
    are all scheduled according to the rest of the clauses. The trip count for all loops associated with the
    collapse clause must be computable and invariant in all the loops.
    It is implementation-defined whether a gang, worker or vector clause on the construct is
    applied to each loop, or to the linearized iteration space.
    """
    def __init__(self, v: CollapseVisitor, n: int, dbg: errors.Debug):
        """
        Args
        ----
        v : The CollapseVisitor that has walked the src tree.
        n : The number of loops to collapse.
        """
        # First check if there are the required number of loops
        if len(v.loops) != n:
            plural = "loop" if n == 1 else "loops"
            raise SyntaxError(dbg.build_message("Clause specifies {} {}, but {} found.").format(n, plural, len(v.loops)))

        assert n > 0, "n is {}, but must be > 0".format(n)
        self.loops = list(v.loops)[0:n]

    def __str__(self):
        return "{}".format(len(self.loops))
