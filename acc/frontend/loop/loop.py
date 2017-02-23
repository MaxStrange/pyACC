"""
Module for the loop directive.

Provides one API function: loop
"""
import acc.frontend.util.util as util
from acc.frontend.loop.visitor import loop_visitor
import asttokens

def loop(clauses, meta_data, back_end, code_object, *args, **kwargs):
    """
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
    - reduction( operator:var-list )

        Where gang-arg is one of:
        - [num:]int-expr
        - static:size-expr
        and gang-arg-list may have at most one num and one static argument,
        and where size-expr is one of:
        - *
        - int-expr

    Restrictions:
    - Only the collapse, gang, worker, vector, seq, auto and tile clauses may
      follow a device_type clause.
    - The int-expr argument to the worker and vector clauses must be
      invariant in the kernels region.
    - A loop associated with a loop construct that does not have a seq
      clause must be written such that the loop iteration count is
      computable when entering the loop construct.
    """
    # TODO: first parse the clauses list (see the docs for the clauses'
    #       descriptions associated with each directive or construct)

    # TODO: parse the source into the intermediate representation used
    #       by the backend
    # --->  The backend will need the following:
    #       - meta variables (which it is NOT allowed to change)
    #       - original source code of the decorated function
    #           ---> packaged into a Code object which contains the
    #                source and the context in which that source is running.
    #                This context information should be appropriately updated
    #                by the backend to match which lines are under which
    #                context. That is, what region of the original source code
    #                is under parallel context or kernels context?
    #                It also needs the line number of the pragma the backend is
    #                supposed to be working on.
    #       - the function so far accumulated
    #           ---> This function is a Code object that contains the so-far
    #                modified function and the context in which different
    #                regions of the code are being run. TODO not sure if we
    #                need both this code and the above code to have the context
    #                information.
    #                It may also need some way of being easy for the backend to
    #                figure out where it left off.
    #       The backend will give back a Code object that is the so-far
    #       accumulated function plus changes made due to the latest directive.

    atok = asttokens.ASTTokens(meta_data.src, parse=True)
    tree = atok.tree
    v = loop_visitor(atok)
    v.visit(tree)

    meta_data.region_source = v.loop_code
    meta_data.region_vars = set(v.loop_vars)
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

    new_source = back_end.for_loop(code_object, meta_data)
    return new_source
