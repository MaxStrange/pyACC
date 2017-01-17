"""
This is the back end's API.
The back end is responsible for taking the OpenACC-compliant information
from the front end and actually parallelizing the given code.
It does this by providing an API that takes the information (such as
func's source code, func's args, func's context's modules with aliases,
and the variables present in the source code) and handing back source
code that is a parallelized version of func.

The parallelized source code that each of these functions returns
should contain whatever is reasonable to get the job done, but they
MUST contain a function called 'execute' with takes the same arguments
as what was provided to the original function.
"""
import os

def for_loop(src, task_src, arg_vars, imports):
    """
    POC function for parallelizing a for-loop into multiple on-host processes.
    Returns source code.
    """
    print("==============================")
    print("Func: ", os.linesep + src)
    print("Task: ", os.linesep + task_src)
    print("Args: ", os.linesep + str(arg_vars))
    print("Modules: ", os.linesep + str(imports))
    print("==============================")

    # TODO: This is just a proof of concept right now - need to actually do this

    new_src =  "from multiprocessing import Pool" + os.linesep
    new_src += "def f(x):" + os.linesep
    new_src += " " * 4 + "return x * x" + os.linesep
    new_src += "def execute(ls):" + os.linesep
    new_src += " " * 4 + "p = Pool(5)" + os.linesep
    new_src += " " * 4 + "return p.map(f, ls)" + os.linesep

    return new_src
