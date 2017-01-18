"""
The main accelerator decorator.
"""
import dill
import acc.frontend.frontend as frontend
from functools import wraps
import inspect

back = None

def acc():
    """
    The main accelerator decorator.
    This is the only API function for the whole framework from
    an end-user's perspective.
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
            # Route to different functions based on the pragma
            # TODO: add pragma args to decorator
            # For now, just handle for loops
            return frontend.parallelize_for_loop(fname, source, stackframe,
                    signature, back, *args, **kwargs)
        return wrapper
    return decorate

def load_back_end(back_end="default"):
    """
    Call this function and pass in a module name as a string.
    This will load the given back end. If "default" is passed in,
    it will use the default back end.
    """
    if back_end == "default":
        back_end = "defaultbackend"

    global back
    back = __import__(back_end)
