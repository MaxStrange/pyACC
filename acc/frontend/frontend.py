"""
This is the front end's API.
"""
from acc.frontend.util.util import get_modules_from_stackframe
from acc.frontend.loop.visitor import loop_visitor
import ast
import asttokens
import os


def parallelize_for_loop(source, stackframe, signature, *args, **kwargs):
    """
    Parallelizes a for loop.
    This is just a proof of concept function to show the idea.
    This will only parallelize the first for loop in the
    given function.
    """
    atok = asttokens.ASTTokens(source, parse=True)
    tree = atok.tree
    v = loop_visitor(source, atok)
    v.visit(tree)

    task_source = v.loop_code
    task_vars = v.loop_vars
    signature_vars = signature.parameters
    module_vars = get_modules_from_stackframe(stackframe.frame)

    print("======================================")
    print("Task source: ", os.linesep + task_source)
    print("Task vars: ", os.linesep + str(task_vars))
    print("Signature vars: ", os.linesep + str(signature_vars))
    print("Module vars: ", os.linesep + str(module_vars))
    print("======================================")

    new_source = backend.for_loop(src=source, task_src=task_source,
            arg_vars=signature_vars, imports=module_vars)
    compile_kernel_module(new_source)
    mod = load_kernel_module()
    return mod.execute(*args, **kwargs)



