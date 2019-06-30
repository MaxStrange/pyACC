"""
This module provides a bunch of functions that are useful
for the front end
"""
import ast
import asttokens
import inspect
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

def get_function_names_from_source(src, ignore):
    """
    Gets the function names of all the function calls in the source code.
    Does not include "acc" or the name of the acc-decorated function.
    """
    atk = asttokens.ASTTokens(src, parse=True)
    tree = atk.tree
    v = _func_visitor(atk)
    v.visit(tree)
    func_names = set(v.func_names)
    if "acc" in func_names:
        func_names.remove("acc")
    if ignore in func_names:
        func_names.remove(ignore)
    return list(func_names)

def get_functions_from_module(module, func_names):
    """
    Gets all the functions from the module that are in func_names.
    See @get_functions_from_stackframe.
    """
    names_in_module_and_func_names = set([name for name in dir(module) if name in func_names])
    funcs = [getattr(module, name) for name in names_in_module_and_func_names]
    func_sources = []
    for f in funcs:
        try:
            src = inspect.getsource(f)
            func_sources.append(src)
        except OSError:
            # Source code not available, this must be a builtin or defined
            # in another module, which will be taken care of by knowing which
            # modules the new source file will need
            pass
        except TypeError:
            # Seems that on previous Python versions, this is the error,
            # rather than OSError
            pass
    return func_sources

def get_functions_from_stackframe(frame, func_names):
    """
    Gets all the functions from the the stackframe that are in func_names.
    That is, gets the source code of the functions that exist in the stack
    frame corresponding to the function names in func_names.
    So if there is a function in func_names called 'square' and there is
    a function defined in the frame as 'def square(x): return x * x',
    this will return ['def square(x): return x * x'] (but with appropriate
    indenting and new lines).
    """
    items = []
    for name, val in frame.f_globals.items():
        if isinstance(val, types.FunctionType) and name in func_names:
            items.append((name, val))
    for name, val in frame.f_locals.items():
        if isinstance(val, types.FunctionType) and name in func_names:
            items.append((name, val))
    items = set(items)

    funcs = [tup[1] for tup in items]
    func_sources = [inspect.getsource(f) for f in funcs]
    return func_sources

def get_modules_from_module(module):
    """
    Gets all the modules that the given one imports in the form:
    [('alias', 'module_object')...].
    """
    global_var_names = set(dir(module))
    items = [(name, getattr(module, name)) for name in global_var_names]
    items = [tup for tup in items if inspect.ismodule(tup[1])]
    return items

def get_modules_from_stackframe(frame):
    """
    Takes a frame object and returns a list of aliases and
    the modules that they correspond to as tuples.
    """
    items = []
    for name, val in frame.f_globals.items():
        if isinstance(val, types.ModuleType):
            items.append((name, val))
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
    """
    How many spaces are there on the left of this line?
    """
    num = 0
    for c in line:
        if c == " ":
            num += 1
        else:
            break
    return num

class _func_visitor(ast.NodeVisitor):
    """
    This class gets all the function names for the functions
    that are called in a given batch of source code.
    """
    def __init__(self, atok):
        self.atok = atok
        self.func_names = []
        self._found_call = False

    def generic_visit(self, node):
        type_name = type(node).__name__
        if type_name == "Call":
            self._found_call = True
            #name = self.atok.get_text(node)
            #self.func_names.append(name)
        elif type_name == "Name" and self._found_call:
            self._found_call = False
            self.func_names.append(node.id)

        ast.NodeVisitor.generic_visit(self, node)

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
