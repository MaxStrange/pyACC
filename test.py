from acc.api import acc
import math as mat
import tensorflow as tf
import os
from tqdm import tqdm

@acc()
def square(ls):
    y = mat.sqrt(5)
    sqrs = []
    for x in ls:
        sqrs.append(x * x)
    a = [d for d in ls]
    b = [c * c for c in a if a % 5 == 0]
    return sqrs

ls = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
squares = square(ls)
print("Squared: ", str(squares))
