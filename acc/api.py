"""
The main accelerator decorator and load_back_end function.

These two functions are the only API functions from an end-user's perspective.
"""
import acc.frontend.frontend as frontend
from acc.frontend.util.metavars import MetaVars
import dill
from functools import wraps
import inspect
import sys

# The back end
back = None

def acc(*, con_or_dir, clauses=[]):
    """
    The main accelerator decorator.
    NOTE: You cannot use global variables in the function that is decorated.
          The results are undefined if you do that, but it will likely result
          in a NameError. If you need to use a global, just pass it in to the
          function. Python passes objects by reference anyway, so don't worry
          about the overhead.
    """
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            global back
            if not back:
                raise ImportError("No back end loaded. First call " +
                        "load_back_end")
            source = dill.source.getsource(func)
            signature = inspect.signature(func)
            stackframe = inspect.stack()[1]
            fname = func.__name__
            module = sys.modules[func.__module__]
            meta_data = MetaVars(src=source, stackframe=stackframe,
                    signature=signature, funcs_name=fname, funcs_module=module)

            if con_or_dir == "parallel":
                pass
            elif con_or_dir == "kernels":
                pass
            elif con_or_dir == "data":
                pass
            elif con_or_dir == "host_data":
                pass
            elif con_or_dir == "loop":
                return frontend.parallelize_for_loop(meta_data,
                                                     back,
                                                     *args,
                                                     **kwargs)
            elif con_or_dir == "atomic":
                pass
            elif con_or_dir == "cache":
                pass
            elif con_or_dir == "declare":
                pass
            elif con_or_dir == "init":
                pass
            elif con_or_dir == "shutdown":
                pass
            elif con_or_dir == "set":
                pass
            elif con_or_dir == "update":
                pass
            elif con_or_dir == "wait":
                pass
            elif con_or_dir == "enter data":
                pass
            elif con_or_dir == "exit_data":
                pass
            else:
                raise ValueError("Unrecognized construct or directive: ",
                        con_or_dir)
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






