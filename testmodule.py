"""
This is a module.
"""

from acc.api import acc
import tensorflow as tf
import math as mat

def modules_local_function(nothing):
    print("This module is a hoax!")

@acc(construct_or_directive="loop", clauses=[])
def square(ls):
    modules_local_function(None)
    y = str(mat.sqrt(5)).join(["a", "b"])
    sqrs = []
    for x in ls:
        sqrs.append(x * x)
    a = [d for d in ls]
    b = [c * c for c in a if c % 5 == 0]
    return sqrs
