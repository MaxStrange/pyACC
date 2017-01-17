"""
This is a class for visiting ASTs and collecting information on loops.
"""
import ast
from acc.frontend.util.util import get_variables_from_source
from acc.frontend.util.util import left_strip_src

class loop_visitor(ast.NodeVisitor):
    """
    This class gets all the loops in a batch of source code.
    """
    def __init__(self, source, atok):
        self.loop_code = ""
        self.loop_vars = ""
        self.funcs = []
        self.source = source
        self.atok = atok

    def generic_visit(self, node):
        type_name = type(node).__name__

        if type_name == "comprehension":
            pass

            # TODO: There is a bug in the asttokens library
            # it doesn't get the first part of the comprehension:
            # it gets: "for _ in list" rather than "_ for _ in list"
            #comp_src = self.atok.get_text(node)
            #self.loop_code = "[" + comp_src + "]"
            #ls_comp_src = "[" + left_strip_src(comp_src) + "]"
            #print("===============================")
            #print("comp_src: ", comp_src)
            #print("===============================")
            #self.loop_vars = get_variables_from_source(ls_comp_src)
            ## TODO: Only get the most outer comprehension or loop
            ## Do this by checking each one's atok.get_text_range
            ## and making sure that none overlap.

        elif type_name == "For":
            for_src = self.atok.get_text(node)
            ls_for_src = left_strip_src(for_src)
            self.loop_code = ls_for_src
            self.loop_vars = get_variables_from_source(ls_for_src)

        elif type_name == "Call":
            self.funcs.append(self.atok.get_text(node))

        ast.NodeVisitor.generic_visit(self, node)





