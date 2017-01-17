"""
This module provides a bunch of functions that are useful
for the front end
"""
import ast
import asttokens
import os
import types



def compile_kernel_module(src):
    """
    Writes the given source code into a file that can then be loaded
    into the running Python program with a call to load_kernel_module.
    Returns the name of the module.
    """
    fname = "para_region_name_mangle.py"
    with open(fname, 'w') as f:
        f.write(src)
    return fname


def load_kernel_module(fname):
    """
    Loads the given Python file into the running program as a module
    and returns it.
    """
    mod = __import__(fname[:-3])
    os.remove(fname)
    return mod


def get_modules_from_stackframe(frame):
    """
    Takes a frame object and returns a list of aliases and
    the modules that they correspond to as tuples.
    """
    items = []
    for name, val in frame.f_globals.items():
        if isinstance(val, types.ModuleType):
            items.append((name, val.__name__))
    return items


def get_variables_from_source(src):
    """
    Gets all the variables found in the given batch of source code (which
    must be a string of valid source code - so its outermost scope should
    have no indentation, etc.).
    The variables might be local, arguments, or modules.
    The variables will contain repeats.
    """
    atk = asttokens.ASTTokens(src, parse=True)
    tree = atk.tree
    v = _name_visitor()
    v.visit(tree)
    return v.ids


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


def _num_spaces(line):
    num = 0
    for c in line:
        if c == " ":
            num += 1
        else:
            break
    return num


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

