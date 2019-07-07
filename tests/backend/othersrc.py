"""
Another source code module for testing.
"""
import math as mat
import os
import sys

mydir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(mydir, "../..")))
import acc.api as openacc

def modules_local_function(nothing):
    pass

@openacc.acc()
def square(ls):
    """
    This is the test function's doc string. This function's got lots going on
    for testing parsing.
    """
    for i in [0, 1, 2]:
        mat.sqrt(i)

    modules_local_function(None)

    # This is a comment in the test function
    y = str(mat.sqrt(5)).join(["a", "b"])

    sqrs = []
    # pragma acc parallel loop collapse(1) worker, vector(16)
    for x in ls:
        sqrs.append(x * x)

    a = [d for d in ls]
    b = [c * c for c in a if c % 5 == 0]

    return sqrs
