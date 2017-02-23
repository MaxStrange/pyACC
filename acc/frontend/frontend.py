"""
This is the front end's API.

This module exposes all of the functions that should be used from the
frontend by the acc module.
"""
from acc.ir.intrep import Code
from acc.frontend.loop.loop import loop
import asttokens
import os
import re


def parse_pragmas(meta_data, *args, **kwargs):
    """
    Generator that yields pragmas one at a time from the function
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
        return loop(clause_list, meta_data, backend, code, *args, **kwargs)
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

