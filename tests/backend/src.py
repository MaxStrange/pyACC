"""
This is source code for the tests in this module.
"""
import os
import sys
import othersrc

def _a_local_function(some_args):
    print("Does nothing")
    return None

def test_function():
    ls = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    squares = othersrc.square(ls)
    return squares
