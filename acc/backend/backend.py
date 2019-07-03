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
MUST contain a function called 'execute' which takes the same arguments
as what was provided to the original function.
"""
import os

def compile(intermediate_rep):
    """
    """
    return intermediate_rep.src

#TODO: this module is currently just a bare-minimum proof of concept and will
# eventually be changed completely. Don't worry about the backend so much right
# now.
def for_loop(code_object, meta_data):
    """
    POC function for parallelizing a for-loop into multiple on-host processes.
    Returns source code.
    """
    src = meta_data.src
    region_src = meta_data.region_source
    region_vars = meta_data.region_vars
    arg_vars = meta_data.signature.parameters
    imports = meta_data.funcs_mods + meta_data.callers_mods
    functions_srcs = meta_data.funcs_funcs + meta_data.callers_funcs
    print("==============================")
    print("Func: ", os.linesep + src)
    print("Task: ", os.linesep + region_src)
    print("Task variables: ", os.linesep + str(region_vars))
    print("Args: ", os.linesep + str(arg_vars))
    print("Modules: ", os.linesep + str(imports))
    print("Functions: ", str(functions_srcs))
    print("==============================")

    # -----------This is all you need to figure out---------------------
    modules = "" # You can get a module object's name by module.__name__
    region_signature = "x"
    new_region_src = " " * 4 + "return x * x" + os.linesep
    execute_signature = "ls"
    execute_src = " " * 4 + "p = Pool(5)" + os.linesep
    execute_src += " " * 4 + "return p.map(task, " + execute_signature + ")" + os.linesep
    #-------------------------------------------------------------------

    new_src = "from multiprocessing import Pool" + os.linesep
    new_src += modules + os.linesep
    new_src += os.linesep.join(functions_srcs) + os.linesep
    new_src += "def task(" + region_signature + "):" + os.linesep
    new_src += new_region_src + os.linesep
    new_src += "def execute(" + execute_signature + "):" + os.linesep
    new_src += execute_src + os.linesep

    print("This is the source we are going to import: " + os.linesep + new_src)

    return new_src
