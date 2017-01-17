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

def for_loop(src, task_src, arg_vars, imports, functions_srcs):
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

    # -----------This is all you need to figure out---------------------
    modules = ""
    task_signature = "x"
    new_task_src = " " * 4 + "return x * x" + os.linesep
    execute_signature = "ls"
    execute_src = " " * 4 + "p = Pool(5)" + os.linesep
    execute_src += " " * 4 + "return p.map(task, " + execute_signature + ")" +\
            os.linesep
    #-------------------------------------------------------------------

    new_src = "from multiprocessing import Pool" + os.linesep
    new_src += modules + os.linesep
    new_src += os.linesep.join(functions_srcs) + os.linesep
    new_src += "def task(" + task_signature + "):" + os.linesep
    new_src += new_task_src + os.linesep
    new_src += "def execute(" + execute_signature + "):" + os.linesep
    new_src += execute_src + os.linesep

    return new_src

