"""
This is the front end's API.
"""
import acc.frontend.util.util as util
from acc.frontend.loop.visitor import loop_visitor
import ast
import asttokens
import os


def parallelize_for_loop(meta_data, back_end, *args, **kwargs):
    """
    Parallelizes a for loop.
    This is just a proof of concept function to show the idea.
    This will only parallelize the first for loop in the
    given function.
    """
    atok = asttokens.ASTTokens(meta_data.src, parse=True)
    tree = atok.tree
    v = loop_visitor(atok)
    v.visit(tree)

    task_source = v.loop_code
    task_vars = set(v.loop_vars)
    frame = meta_data.stackframe[0] # In 3.5, this can be stackframe.frame
    func_names = util.get_function_names_from_source(meta_data.src,
            meta_data.funcs_name)

    meta_data.callers_mods = util.get_modules_from_stackframe(frame)
    meta_data.callers_funcs = util.get_functions_from_stackframe(frame, func_names)
    meta_data.funcs_funcs = util.get_functions_from_module(meta_data.funcs_module,
            func_names)
    meta_data.funcs_mods = util.get_modules_from_module(meta_data.funcs_module)

    print(str(meta_data))

    funcs = meta_data.funcs_funcs.extend(meta_data.callers_funcs)
    funcs = [] if not funcs else funcs
    module_vars = meta_data.callers_mods.extend(meta_data.funcs_mods)
    module_vars = [] if not module_vars else module_vars

    new_source = back_end.for_loop(src=meta_data.src, task_src=task_source,
            task_vars=task_vars, arg_vars=meta_data.signature.parameters,
            imports=module_vars, functions_srcs=funcs)
    fname = util.compile_kernel_module(new_source)
    mod = util.load_kernel_module(fname)
    return mod.execute(*args, **kwargs)




