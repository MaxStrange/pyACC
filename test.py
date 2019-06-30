"""
Test script.
"""
from acc.api import acc, load_back_end
import testmodule
import os
from tqdm import tqdm


def a_local_function(some_args):
    print("Does nothing")
    return None

if __name__ == "__main__":
    load_back_end("default")
    ls = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    squares = testmodule.square(ls)
    print("Squared: ", str(squares))
