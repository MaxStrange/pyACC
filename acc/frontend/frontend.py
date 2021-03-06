"""
This is the front end's API.

This module exposes all of the functions that should be used from the
frontend by the acc module.
"""
import acc.frontend.loop.loop as loop
import acc.frontend.parallel.parallel as parallel
import acc.frontend.util.util as util
import asttokens
import re

def parse_pragmas(src, *args, **kwargs):
    """
    Generator that yields pragmas one at a time from the function
    given in `src`.
    """
    regexp = re.compile(r"^((\s)*#(\s)*(pragma)(\s)*(acc))")
    for lineno, line in enumerate(src.splitlines()):
        if regexp.match(line):
            yield line, lineno

def accumulate_pragma(intermediate_rep, pragma, lineno, *args, **kwargs):
    """
    Modifies `intermediate_rep` according to `pragma`.
    """
    directive, clause_list = util.parse_pragma_to_directive_and_clauses(pragma)
    _accumulate_pragma_helper(directive, clause_list, intermediate_rep, lineno, *args, **kwargs)

def _accumulate_pragma_helper(directive, clause_list, intermediate_rep, lineno, dbg, *args, **kwargs):
    """
    Applies the given directive and its associated clause list
    to the given intermediate_rep.
    Modifies intermediate_rep in place.
    """
    if directive  == "parallel":
        parallel.parallel(clause_list, intermediate_rep, lineno, dbg, *args, **kwargs)
    elif directive == "kernels":
        pass
    elif directive == "serial":
        pass
    elif directive == "data":
        pass
    elif directive == "enter":  # enter data
        pass
    elif directive == "exit":   # exit data
        pass
    elif directive == "host_data":
        pass
    elif directive == "loop":
        loop.loop(clause_list, intermediate_rep, lineno, dbg, *args, **kwargs)
    elif directive == "cache":
        pass
    elif directive == "atomic":
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
    elif directive == "routine":
        pass
    else:
        raise ValueError("Unrecognized construct or directive:", directive)
