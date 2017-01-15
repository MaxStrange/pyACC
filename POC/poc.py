"""
POC for the idea
"""
import dill
from functools import wraps
import math

def acc(msg=""):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(msg)
            source = dill.source.getsource(func)
            print("This is the function to call:")
            print(source)
            return func(*args, **kwargs)
        return wrapper
    return decorate


@acc(msg="Hello!")
def add(x, y):
    """
    A function that adds two values.
    """
    _  = math.sqrt(x + y)
    return x + y

x = 5
y = 10
val = add(x, y)
print("And here is the result:", str(val))
