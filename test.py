from acc.api import acc
import math as mat
from tensorflow.python.ops import rnn, rnn_cell
import tensorflow as tf
import os
from tqdm import tqdm

def a_local_function(some_args):
    print("Does nothing")
    return None

@acc()
def square(ls):
    y = str(mat.sqrt(5)).join(["a", "b"])
    n = a_local_function("")
    sqrs = []
    for x in ls:
        sqrs.append(x * x)
    a = [d for d in ls]
    b = [c * c for c in a if a % 5 == 0]
    return sqrs

ls = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
squares = square(ls)
print("Squared: ", str(squares))
