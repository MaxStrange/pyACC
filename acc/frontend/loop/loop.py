"""
Module for the loop directive.

Provides one API function: loop
"""
from acc.ir.intrep import Code
from acc.frontend.loop.visitor import loop_visitor
from acc.frontend.util.errors import InvalidClauseError
import acc.frontend.util.util as util
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
    index = 0
    while index != -1:
        index, code_object = _apply_clause(index,
                                           clauses,
                                           code_object,
                                           meta_data,
                                           back_end)

    #atok = asttokens.ASTTokens(meta_data.src, parse=True)
    atok = asttokens.ASTTokens(code_object.src, parse=True)
    tree = atok.tree
    v = loop_visitor(atok)
    v.visit(tree)

    meta_data.region_source = v.loop_code
    meta_data.region_vars = set(v.loop_vars)
    frame = meta_data.stackframe[0] # In 3.5, this can be stackframe.frame
    #func_names = util.get_function_names_from_source(meta_data.src,
    func_names = util.get_function_names_from_source(code_object.src,
            meta_data.funcs_name)

    meta_data.callers_mods = util.get_modules_from_stackframe(frame)
    meta_data.callers_funcs = util.get_functions_from_stackframe(frame, func_names)
    meta_data.funcs_funcs = util.get_functions_from_module(meta_data.funcs_module,
            func_names)
    meta_data.funcs_mods = util.get_modules_from_module(meta_data.funcs_module)

    funcs = meta_data.funcs_funcs + meta_data.callers_funcs
    module_vars = meta_data.funcs_mods + meta_data.callers_mods

    new_source = back_end.for_loop(code_object, meta_data)
    return Code(new_source)


def _apply_clause(index, clause_list, code_object, meta_data, back_end):
    """
    Consumes however much of the clause list as necessary to apply the clause
    found at index in the clause_list.

    @param index:       The index into the clause_list of the clause we are
                        interested int.

    @param clause_list: The list of the clauses that this clause is indexed in.

    @return:            The new index and new Code. If there are no more
                        clauses after this one is done, index will be -1.
    """
    args = (index, clause_list, code_object, meta_data, back_end)
    clause = clause_list[index]
    if   clause.startswith("collapse"):
        return _collapse(*args)
    elif clause.startswith("gang"):
        return _gang(*args)
    elif clause.startswith("worker"):
        return _worker(*args)
    elif clause.startswith("vector"):
        return _vector(*args)
    elif clause.startswith("seq"):
        return _seq(*args)
    elif clause.startswith("auto"):
        return _auto(*args)
    elif clause.startswith("tile"):
        return _tile(*args)
    elif clause.startswith("device_type"):
        return _device_type(*args)
    elif clause.startswith("independent"):
        return _independent(*args)
    elif clause.startswith("private"):
        return _private(*args)
    elif clause.startswith("reduction"):
        return _reduction(*args)
    else:
        raise InvalidClauseError("Clause either not allowed for this " +\
                "directive, or else it may be spelled " +\
                "incorrectly. Clause given: " + clause)
#TODO do this crap
def _collapse(index, clause_list, code_object, meta_data, back_end):
    """
    """
    return -1, code_object

def _gang(index, clause_list, code_object, meta_data, back_end):
    """
    """
    return -1, code_object

def _worker(index, clause_list, code_object, meta_data, back_end):
    """
    """
    return -1, code_object

def _vector(index, clause_list, code_object, meta_data, back_end):
    """
    """
    return -1, code_object

def _seq(index, clause_list, code_object, meta_data, back_end):
    """
    """
    return -1, code_object

def _auto(index, clause_list, code_object, meta_data, back_end):
    """
    """
    return -1, code_object

def _tile(index, clause_list, code_object, meta_data, back_end):
    """
    """
    return -1, code_object

def _device_type(index, clause_list, code_object, meta_data, back_end):
    """
    """
    return -1, code_object

def _independent(index, clause_list, code_object, meta_data, back_end):
    """
    """
    return -1, code_object

def _private(index, clause_list, code_object, meta_data, back_end):
    """
    """
    return -1, code_object

def _reduction(index, clause_list, code_object, meta_data, back_end):
    """
    """
    return -1, code_object
