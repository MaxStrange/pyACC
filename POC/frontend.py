"""
This is the front end's API.
"""
import ast
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
    print("Was given this source code:", os.linesep + source)
    # Compile the src code into a syntax tree so we can get all the vars
    v = visitor()
    tree = ast.parse(source)
    v.visit(tree)
    variables = set(v.ids)
    print("Its variables are:")
    print(variables)

    # Scan for a for loop
    src = source.split(os.linesep)
    para_region = []
    found = False
    for line in src:
        if found and num_tabs(line) <= start_tabs:
            found = False
        elif found and num_tabs(line) > start_tabs:
            para_region.append(line)
        if line.lstrip().startswith("for"):
            para_region.append(line)
            start_tabs = num_tabs(line)
            found = True
    print("Found this loop: ", str(para_region))
    print("As source code: " + os.linesep + os.linesep.join(para_region))
    print("Just the task part: " +
            os.linesep + os.linesep.join(para_region[1:]))
    vis = visitor()
    tree = ast.parse(os.linesep.join(para_region[1:]).lstrip())
    vis.visit(tree)
    task_vars = set(vis.ids)
    print("Variables from the task:", task_vars)
    print("Signature of decorated function: ", signature)
    signature_vars = signature.parameters
    print("Variables found in the decorated function's signature: ",
            signature_vars)
    module_vars = list(imports())
    print("Modules and aliases in the scope of the function: ",
            module_vars)
    # We now have all of the variables, and we know what region
    # needs to be parallelized. But this is just a proof of concept,
    # so we will just hard code a module that we import on the fly
    # to show that that part of the process can be done.
    new_src =  "from multiprocessing import Pool" + os.linesep
    new_src += "def f(x):" + os.linesep
    new_src += " " * 4 + "return x * x" + os.linesep
    new_src += "def paraloop(ls):" + os.linesep
    new_src += " " * 4 + "p = Pool(5)" + os.linesep
    new_src += " " * 4 + "return p.map(f, ls)" + os.linesep
    with open("para_region_name_mangle.py", 'w') as f:
        f.write(new_src)
    mod = __import__("para_region_name_mangle")

    #v = visitor()
    #tree = ast.parse(source)
    ## Collect everything we need from the source code
    #v.visit(tree)

    #task_source = v.loop_code
    #task_vars = v.loop_vars
    #signature_vars = signature.parameters
    #module_vars = list(imports())
    #print("Modules and aliases in scope: MAKE SURE THIS WORKS" +\
    #        os.linesep + str(module_vars))
    #new_source = backend.for_loop(src=source, task_src=task_source,
    #        arg_vars=signature_vars, imports=module_vars)
    #compile_kernel_module(new_source)
    #mod = load_kernel_module()
    #return mod.execute(*args, **kwargs)

    return mod.paraloop(*args, **kwargs)


def imports():
    for name, val in globals().items():
        if isinstance(val, types.ModuleType):
            yield name, val.__name__

class visitor(ast.NodeVisitor):
    def __init__(self):
        self.ids = []

    def generic_visit(self, node):
        type_name = type(node).__name__
        if type_name == "Name":
            self.ids.append(node.id)
        ast.NodeVisitor.generic_visit(self, node)

def num_tabs(line):
    num = 0
    for c in line:
        if c == " ":
            num += 1
        else:
            break
    return num
