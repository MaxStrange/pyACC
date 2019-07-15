"""
This is source code for the tests in this module.
"""
import os
import sys
import othersrc

mydir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(mydir, "../..")))
import acc.api as openacc

def _a_local_function(some_args):
    print("Does nothing")
    return None

def test_function():
    ls = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    squares = othersrc.square(ls)
    return squares

def test_function_host():
    openacc.set_device_type('host')
    return test_function()

def test_function_cuda():
    openacc.set_device_type('nvidia')
    return test_function()

def test_function_opencl():
    openacc.set_device_type('radeon')
    return test_function()
