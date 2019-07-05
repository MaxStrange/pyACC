"""
This module contains the 'collapse' clause's AST visitor for the 'loop' construct.
"""
import ast
from acc.frontend.util.util import get_variables_from_source
from acc.frontend.util.util import left_strip_src

class CollapseVisitor(ast.NodeVisitor):
    """
    This class gets all the loops in a batch of source code.
    """
    def __init__(self, atok):
        self.loop_code = ""
        self.loop_vars = ""
        self.atok = atok

    def generic_visit(self, node):
        type_name = type(node).__name__

        if type_name == "comprehension":
            # TODO: We currently do not support parallelization of comprehensions
            pass
        elif type_name == "For":
            for_src = self.atok.get_text(node)
            ls_for_src = left_strip_src(for_src)
            self.loop_code = ls_for_src
            self.loop_vars = list(set(get_variables_from_source(ls_for_src)))

            print("Loop code:")
            print("-----------------------")
            print(self.loop_code)
            print("-----------------------")
            print("Loop vars:")
            print("-----------------------")
            print(self.loop_vars)
            print("-----------------------")

        ast.NodeVisitor.generic_visit(self, node)
