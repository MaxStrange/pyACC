"""
The main accelerator decorator.
"""
import dill
import acc.frontend.frontend as frontend
from functools import wraps
import inspect

def acc():
    """
    The main accelerator decorator.
    This is the only API function for the whole framework from
    an end-user's perspective.
    """
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            source = dill.source.getsource(func)
            signature = inspect.signature(func)
            stackframe = inspect.stack()[1]
            fname = func.__name__
            # Route to different functions based on the pragma
            # TODO: add pragma args to decorator
            # For now, just handle for loops
            return frontend.parallelize_for_loop(fname, source, stackframe,
                                            signature, *args, **kwargs)
        return wrapper
    return decorate


