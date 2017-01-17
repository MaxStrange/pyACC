"""
This is the front end's API.
"""
import ast
import asttokens
from multiprocessing import Pool
import os
import types

def parallelize_for_loop(source, signature, *args, **kwargs):
    """
    Parallelizes a for loop.
    This is just a proof of concept function to show the idea.
    This will only parallelize the first for loop in the
    given function.
    """
    atok = asttokens.ASTTokens(source, parse=True)
    tree = atok.tree
    v = _loop_visitor(source, atok)
    v.visit(tree)

    task_source = v.loop_code
    task_vars = v.loop_vars
    signature_vars = signature.parameters
    module_vars = list(imports())
    new_source = backend.for_loop(src=source, task_src=task_source,
            arg_vars=signature_vars, imports=module_vars)
    compile_kernel_module(new_source)
    mod = load_kernel_module()
    return mod.execute(*args, **kwargs)

class _loop_visitor(ast.NodeVisitor):
    """
    This class gets all the loops in a batch of source code.
    """
    def __init__(self, source, atok):
        self.loop_code = ""
        self.loop_vars = ""
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
            #return

        elif type_name == "For":
            for_src = self.atok.get_text(node)
            self.loop_code = for_src
            ls_for_src = left_strip_src(for_src)
            print("===============================")
            print("ls_for_src: ", os.linesep + ls_for_src)
            print("===============================")
            self.loop_vars = get_variables_from_source(ls_for_src)
            return

        ast.NodeVisitor.generic_visit(self, node)


def _num_spaces(line):
    num = 0
    for c in line:
        if c == " ":
            num += 1
        else:
            break
    return num


def left_strip_src(src):
    """
    Left-justifies the given source code.
    """
    as_list = src.split(os.linesep)
    spaces = [_num_spaces(line) for line in as_list]
    justification = min(spaces)
    spaces = [x - justification for x in spaces]
    as_list = [line.lstrip() for line in as_list]
    as_list = [" " * space + line for line, space in zip(as_list, spaces)]
    return os.linesep.join(as_list)


def get_variables_from_source(src):
    atk = asttokens.ASTTokens(src, parse=True)
    tree = atk.tree
    v = _name_visitor()
    v.visit(tree)

class _name_visitor(ast.NodeVisitor):
    """
    This class gets all the variable names in a batch of python source
    code in order of appearance (may contain duplicates - call set()
    on the ids if you want only unique ones).
    """
    def __init__(self):
        self.ids = []

    def generic_visit(self, node):
        type_name = type(node).__name__
        if type_name == "Name":
            self.ids.append(node.id)

        ast.NodeVisitor.generic_visit(self, node)











