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
import re


def parse_pragmas(meta_data, *args, **kwargs):
    """
    Generator that yields pragmas one ata time from the function
    given in meta_data.
    """
    regexp = re.compile("^((\s)*#(\s)*(pragma)(\s)*(acc))")
    for line in meta_data.src.split(os.linesep):
        if regexp.match(line):
            yield line.strip()


def apply_pragma(code, pragma, meta_data, backend, *args, **kwargs):
    """
    Returns modified 'code' after applying any pragmas.
    'code' is a Code object.
    """
    directive_and_clauses = pragma.partition("acc")[-1].split(' ')
    directive_and_clauses = [word for word in directive_and_clauses if\
                             word != '']
    directive = directive_and_clauses[0]
    clause_list = directive_and_clauses[1:]
    return _apply_pragma_helper(directive,
                                clause_list,
                                code,
                                meta_data,
                                backend,
                                *args,
                                **kwargs)

def _apply_pragma_helper(directive,
                         clause_list,
                         code,
                         meta_data,
                         backend,
                         *args,
                         **kwargs):
    """
    Applies the given directive and its associated clause list
    to the given code (with the help of the meta_data).
    Returns the code after modifiying it.
    """
    # TODO: This is the main batch of work that needs to get done
    if directive == "parallel":
        pass
    elif directive == "kernels":
        pass
    elif directive == "data":
        pass
    elif directive == "host_data":
        pass
    elif directive == "loop":
        # TODO this is just a proof of concept way of doing this
        return _loop(clause_list, meta_data, backend, *args, **kwargs)
    elif directive == "atomic":
        pass
    elif directive == "cache":
        pass
    elif directive == "declare":
        pass
    elif directive == "init":
        pass
    elif directive == "shutdown":
        pass
    elif directive == "set":
        pass
    elif directive == "update":
        pass
    elif directive == "wait":
        pass
    elif directive == "enter_data":
        pass
    elif directive == "exit_data":
        pass
    else:
        raise ValueError("Unrecognized construct or directive:", directive)

def _loop(clauses, meta_data, back_end, *args, **kwargs):
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
    return new_source

