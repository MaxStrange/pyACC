"""
This module provides a class that will hold all of the metadata that
the front end collects and which might be useful to all the back end
functions.
"""
import os

class MetaVars:
    """
    Just a storage class for all the useful variables that might get
    passed around.
    """
    def __init__(self, *, src=None, stackframe=None, signature=None,
                    signature_vars=None, callers_mods=None, callers_funcs=None,
                    funcs_mods=None, funcs_funcs=None, funcs_name=None,
                    funcs_module=None):
        """
        @param src:             The source code of the acc-decorated-function,
                                including the `def whatever(args):` line, but NOT
                                including the acc decorator.

        @param stackframe:      The callstack frame at the point of calling
                                the acc-decorated-function

        @param signature:       The acc-decorated-function's signature

        @param callers_mods:    The modules (and aliases of those modules)
                                which are known to the caller of the
                                acc-decorated-function

        @param callers_funcs:   The source code for the functions that
                                the caller of the acc-decorated-function has
                                access to and which are called from the
                                acc-decorated-function

        @param funcs_mods:      The modules (and aliases of those modules)
                                which are known to the function (in the form
                                [(alias: str, module object), etc.])

        @param funcs_funcs:     The source code for the functions that
                                the acc-decorated-function has access to and
                                calls

        @param funcs_name:      The name of the acc-decorated function

        @param funcs_module:    The module in which the function is defined
        """
        self.src = src
        self.stackframe = stackframe
        self.signature = signature
        self.callers_mods = callers_mods
        self.callers_funcs = callers_funcs
        self.funcs_mods = funcs_mods
        self.funcs_funcs = funcs_funcs
        self.funcs_name = funcs_name
        self.funcs_module = funcs_module

    def __str__(self):
        s = ""
        s += "(" + os.linesep
        s += "src: " + os.linesep + str(self.src) + os.linesep
        s += "stackframe: " + os.linesep + str(self.stackframe) + os.linesep
        s += "signature: " + os.linesep + str(self.signature) + os.linesep
        s += "callers_mods: " + os.linesep + str(self.callers_mods) + os.linesep
        s += "callers_funcs: " + os.linesep + str(self.callers_funcs) + os.linesep
        s += "funcs_mods: " + os.linesep + str(self.funcs_mods) + os.linesep
        s += "funcs_funcs: " + os.linesep + str(self.funcs_funcs) + os.linesep
        s += "funcs_name: " + os.linesep + str(self.funcs_name) + os.linesep
        s += "funcs_module: " + os.linesep + str(self.funcs_module) + os.linesep
        s += ")"

        return s
