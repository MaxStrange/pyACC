"""
The main accelerator decorator and load_back_end function.

These two functions are the only API functions from an end-user's perspective.
"""
import acc.frontend.util.util as util
import acc.frontend.frontend as frontend
from acc.ir.metavars import MetaVars
from acc.ir.intrep import IntermediateRepresentation
import dill
from functools import wraps
import inspect
import sys

# The back end
back = None

def acc():
    """
    The main accelerator decorator.

    Usage:

    @acc()
    def function_to_list_pragmas_in(data, ret):
        #pragma acc parallel loop copyout=ret[0:len(data)]
        for d in data:
            ret.append(d ** 2)

    NOTE: You cannot use global variables in the function that is decorated.
          The results are undefined if you do that, but it will likely result
          in a NameError. If you need to use a global, just pass it in to the
          function. Python passes objects by reference anyway, so don't worry
          about the overhead.

    The decorator will scan the decorated function, parse any pragmas it sees,
    rewrite the function into a module, load the module, and then
    run the re-written function on the fly, rather than running the decorated
    function as is.
    """
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            global back
            if not back:
                raise ImportError("No back end loaded. First call load_back_end")
            else:
                try:
                    getattr(back, "compile")
                except AttributeError:
                    raise ImportError("Back end does not have a 'compile' function.")

            # Grab the source code from the decorated function
            source = dill.source.getsource(func)

            # Grab the decorated function's signature
            signature = inspect.signature(func)

            # Grab the top of the stack
            stackframe = inspect.stack()[1]

            # Put together all the stuff we need in order to rewrite the function
            funcname = func.__name__
            module = sys.modules[func.__module__]
            meta_data = MetaVars(src=source, stackframe=stackframe, signature=signature, funcs_name=funcname, funcs_module=module)

            intermediate_rep = IntermediateRepresentation(meta_data)
            for pragma in frontend.parse_pragmas(intermediate_rep.src, *args, **kwargs):
                # Side-effect-y: this function modifies intermediate_rep each time
                frontend.accumulate_pragma(intermediate_rep, pragma, *args, **kwargs)

            # Pass the intermediate representation into the backend to get the new source code
            new_source = back.compile(intermediate_rep)

            # Dump the source code that we created into a file
            oldmodulesource = dill.source.getsource(module)
            newmodulesource = oldmodulesource.replace(source, new_source.strip("@acc()"))
            fname = util.compile_kernel_module(newmodulesource)

            # Import the new module.
            mod = util.load_kernel_module(fname)

            # Return the result of executing the newly written function.
            func_to_execute = getattr(mod, funcname)
            return func_to_execute(*args, **kwargs)
        return wrapper
    return decorate

def load_back_end(back_end="default"):
    """
    Call this function and pass in a module name as a string.
    This will load the given back end. If "default" is passed in,
    it will use the default back end.
    """
    if back_end == "default":
        back_end = "acc.backend.backend"

    # Set the back end to whatever is the last item in a string of x.y.z...
    global back
    back = __import__(back_end)
    components = back_end.split('.')
    for comp in components[1:]:
        back = getattr(back, comp)
