"""
POC for parallelization
"""
import dill
from functools import wraps
from multiprocessing import Pool
import os

def num_tabs(line):
    num = 0
    for c in line:
        if c == " ":
            num += 1
        else:
            break
    return num

def parallelize_for_loop(src, *args, **kwargs):
    # Scan for a for loop
    print("Found this source code to parallelize:", src)
    src = src.split(os.linesep)
    para_region = []
    found = False
    for line in src:
        if found and num_tabs(line) <= start_tabs:
            found = False
        elif found and num_tabs(line) > start_tabs:
            para_region.append(line)
        if line.lstrip().startswith("for"):
            para_region.append(line)
            start_tabs = num_tabs(line)
            found = True
    print("Found this loop: ", str(para_region))
    # Now would come the hard part, where we scan the src
    # and the para_region and see what variables are needed and
    # how best to parallelize the region, etc.
    # But for the POC, I just want to hard-code stuff to see if it
    # is possible.
    new_src =  "from multiprocessing import Pool" + os.linesep
    new_src += "def f(x):" + os.linesep
    new_src += " " * 4 + "return x * x" + os.linesep
    new_src += "def paraloop(ls):" + os.linesep
    new_src += " " * 4 + "p = Pool(5)" + os.linesep
    new_src += " " * 4 + "return p.map(f, ls)" + os.linesep
    with open("para_region_name_mangle.py", 'w') as f:
        f.write(new_src)
    mod = __import__("para_region_name_mangle")
    return mod.paraloop(*args, **kwargs)

def acc():
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            source = dill.source.getsource(func)
            return parallelize_for_loop(source, *args, **kwargs)
        return wrapper
    return decorate


@acc()
def square(ls):
    sqrs = []
    for x in ls:
        sqrs.append(x * x)
    return sqrs


ls = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print("Squaring each item in:", str(ls))
squares = square(ls)
print("Squares:", str(squares))


