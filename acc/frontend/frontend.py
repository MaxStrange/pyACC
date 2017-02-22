"""
This is the front end's API.

This module exposes all of the functions that should be used from the
frontend by the acc module.
"""
import acc.frontend.util.util as util
from acc.frontend.loop.visitor import loop_visitor
import ast
import asttokens
import os


def parse_pragmas(meta_data, *args, **kwargs):
    """
    Generator that yields pragmas one ata time from the function
    given in meta_data.
    """
    # TODO
    pass


def apply_pragma(code, pragma, meta_data, *args, **kwargs):
    """
    Returns modified 'code' after applying any pragmas.
    'code' is a Code object.
    """
    # TODO
    pass


def parallelize_for_loop(clauses, meta_data, back_end, *args, **kwargs):
    """
    Parallelizes a for loop.
    ###################################################################
    This is just a proof of concept function to show the idea.
    This will only parallelize the first for loop in the
    given function.
    ###################################################################
    From the docs:
    The loop construct can describe what type of parallelism to use to
    execute the loop and declare private variables and arrays and reduction
    operations.

    Allowable clauses are:
    - collapse( n )
    - gang [( gang-arg-list )]
    - worker [( [num:]int-expr )]
    - vector [( [length:]int-expr )]
    - seq
    - auto
    - tile( size-expr-list )
    - device_type( device-type-list )
    - independent
    - private( var-list )
    - reduction( operator:var-list)

        Where gang-arg is one of:
        - [num:]int-expr
        - static:size-expr
        and gang-arg-list may have at most one num and one static argument,
        and where size-expr is one of:
        - *
        - int-expr

    Restrictions:
    - Only the collapse, gange, worker, vector, seq, auto and tile clauses may
      follow a device_type clause.
    - The int-expr argument to the worker and vector clauses must be
      invariant in the kernels region.
    - A loop associated with a loop construct that does not have a seq
      clause must be written such that the loop iteration count is
      computable when entering the loop construct.
    """
    # TODO: first parse the clauses list (see the docs for the clauses'
    #       descriptions associated with each directive or construct)

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

    funcs = meta_data.funcs_funcs + meta_data.callers_funcs
    module_vars = meta_data.funcs_mods + meta_data.callers_mods

    new_source = back_end.for_loop(src=meta_data.src, task_src=task_source,
            task_vars=task_vars, arg_vars=meta_data.signature.parameters,
            imports=module_vars, functions_srcs=funcs)
    fname = util.compile_kernel_module(new_source)
    mod = util.load_kernel_module(fname)
    return mod.execute(*args, **kwargs)




