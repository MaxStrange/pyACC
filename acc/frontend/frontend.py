"""
This is the front end's API.

This module exposes all of the functions that should be used from the
frontend by the acc module.
"""
from acc.frontend.loop.loop import loop
import asttokens
import re

def parse_pragmas(meta_data, *args, **kwargs):
    """
    Generator that yields pragmas one at a time from the function
    given in meta_data.
    """
    regexp = re.compile("^((\s)*#(\s)*(pragma)(\s)*(acc))")
    for line in meta_data.src.splitlines():
        if regexp.match(line):
            yield line

def accumulate_pragma(intermediate_rep, pragma, meta_data, backend, *args, **kwargs):
    """
    Modifies `intermediate_rep` according to `pragma`.
    """
    directive_and_clauses = pragma.partition("acc")[-1].split(' ')
    directive_and_clauses = [word for word in directive_and_clauses if word != '']
    directive = directive_and_clauses[0]
    clause_list = directive_and_clauses[1:]
    _apply_pragma_helper(directive, clause_list, intermediate_rep, meta_data, backend, *args, **kwargs)

def _apply_pragma_helper(directive, clause_list, intermediate_rep, meta_data, backend, *args, **kwargs):
    """
    Applies the given directive and its associated clause list
    to the given intermediate_rep (with the help of the meta_data).
    Modifies intermediate_rep in place.
    """
    # TODO: This is the main batch of work that needs to get done to make this compliant with the OpenACC standard
    if directive == "parallel":
        pass
    elif directive == "kernels":
        pass
    elif directive == "data":
        pass
    elif directive == "host_data":
        pass
    elif directive == "loop":
        loop(clause_list, meta_data, backend, intermediate_rep, *args, **kwargs)
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
