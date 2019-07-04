"""
The main accelerator decorator and load_back_end function.

These two functions are the only API functions from an end-user's perspective.
"""
import acc.frontend.util.util as util
import acc.frontend.frontend as frontend
from acc.ir.metavars import MetaVars
from acc.ir.intrep import IntermediateRepresentation
import dill
from functools import wraps
import inspect
import sys

# The back end
back = None

def acc():
    """
    The main accelerator decorator.

    Usage:

    @acc()
    def function_to_list_pragmas_in(data, ret):
        #pragma acc parallel loop copyout=ret[0:len(data)]
        for d in data:
            ret.append(d ** 2)

    NOTE: You cannot use global variables in the function that is decorated.
          The results are undefined if you do that, but it will likely result
          in a NameError. If you need to use a global, just pass it in to the
          function. Python passes objects by reference anyway, so don't worry
          about the overhead.

    The decorator will scan the decorated function, parse any pragmas it sees,
    rewrite the function into a module, load the module, and then
    run the re-written function on the fly, rather than running the decorated
    function as is.
    """
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            global back
            if not back:
                raise ImportError("No back end loaded. First call load_back_end")
            else:
                try:
                    getattr(back, "compile")
                except AttributeError:
                    raise ImportError("Back end does not have a 'compile' function.")

            # Grab the source code from the decorated function
            source = dill.source.getsource(func)

            # Grab the decorated function's signature
            signature = inspect.signature(func)

            # Grab the top of the stack
            stackframe = inspect.stack()[1]

            # Put together all the stuff we need in order to rewrite the function
            funcname = func.__name__
            module = sys.modules[func.__module__]
            meta_data = MetaVars(src=source, stackframe=stackframe, signature=signature, funcs_name=funcname, funcs_module=module)

            intermediate_rep = IntermediateRepresentation(meta_data)
            for pragma, linenumber in frontend.parse_pragmas(intermediate_rep.src, *args, **kwargs):
                # Side-effect-y: this function modifies intermediate_rep each time
                frontend.accumulate_pragma(intermediate_rep, pragma, linenumber, *args, **kwargs)

            # Pass the intermediate representation into the backend to get the new source code
            new_source = back.compile(intermediate_rep)

            # Dump the source code that we created into a file
            oldmodulesource = dill.source.getsource(module)
            newmodulesource = oldmodulesource.replace(source, new_source.strip("@acc()"))
            fname = util.compile_kernel_module(newmodulesource)

            # Import the new module.
            mod = util.load_kernel_module(fname)

            # Return the result of executing the newly written function.
            func_to_execute = getattr(mod, funcname)
            return func_to_execute(*args, **kwargs)
        return wrapper
    return decorate

def load_back_end(back_end="default"):
    """
    Call this function and pass in a module name as a string.
    This will load the given back end. If "default" is passed in,
    it will use the default back end.
    """
    if back_end == "default":
        back_end = "acc.backend.backend"

    # Set the back end to whatever is the last item in a string of x.y.z...
    global back
    back = __import__(back_end)
    components = back_end.split('.')
    for comp in components[1:]:
        back = getattr(back, comp)

def get_num_devices(devtype: str) -> int:
    """
    Returns the number of devices of the given type.
    """
    pass

def set_device_type(devtype: str) -> None:
    """
    Description
    -----------
    The acc_set_device_type routine tells the runtime which type of device to
    use among those available and sets the value of acc-current-device-type-var for the current thread.

    A call to acc_set_device_type is functionally equivalent to a set device_type directive
    with the matching device type argument, as described in Section 2.14.3.

    Restrictions
    ------------
    • If the device type specified is not available, the behavior is implementation-defined; in
      particular, the program may abort.
    • If some compute regions are compiled to only use one device type, calling this routine with a
      different device type may produce undefined behavior.
    """
    pass

def get_device_type() -> str:
    """
    Description
    -----------
    The acc_get_device_type routine returns the value of acc-current-device-type-var
    for the current thread to tell the program what type of device will be used to run the next
    compute region, if one has been selected. The device type may have been selected by the program
    with an acc_set_device_type call, with an environment variable, or by the default behavior
    of the program.

    Restrictions
    ------------
    • If the device type has not yet been selected, the value acc_device_none may be returned.
    """
    pass

def set_device_num(n: int, devtype: str) -> None:
    """
    Description
    -----------
    The acc_set_device_num routine tells the runtime which device to use among
    those available of the given type for compute or data regions in the current thread and sets the value
    of acc-current-device-num-var. If the value of devicenum is negative, the runtime will revert to
    its default behavior, which is implementation-defined. If the value of the second argument is zero,
    the selected device number will be used for all device types. A call to acc_set_device_num
    is functionally equivalent to a set device_num directive with the matching device number
    argument, as described in Section 2.14.3.

    Restrictions
    ------------
    • If the value of devicenum is greater than or equal to the value returned by acc_get_num_devices
      for that device type, the behavior is implementation-defined.
    • Calling acc_set_device_num implies a call to acc_set_device_type with that
      device type argument.
    """
    pass

def get_device_num(devtype: str) -> int:
    """
    The acc_get_device_num routine returns the value of acc-current-device-num-var for the current thread.
    """
    pass

def get_device_property(devnum: int, devtype: str, property: str):
    """
    Description
    -----------
    The acc_get_property routine returns
    the value of the specified property. devicenum and devicetype specify the device being
    queried. If devicetype has the value acc_device_current, then devicenum is ignored
    and the value of the property for the current device is returned. property is an enumeration
    constant, defined in openacc.h, for C or C++, or an integer parameter, defined in the openacc
    module, for Fortran. Integer-valued properties are returned by acc_get_property, and
    string-valued properties are returned by acc_get_property_string. In Fortran, acc_get_property_string
    returns the result into the character variable passed as the last argument.

    The supported values of property are given in the following table.

    property                        return type                     return value
    "memory"                        int                             size of device memory in bytes
    "free_memory"                   int                             free device memory in bytes
    "shared_memory_support"         int                             nonzero if the specified device
                                                                    supports sharing memory with the local
                                                                    thread
    "name"                          str                             device name
    "vendor"                        str                             device vendor
    "driver"                        str                             device driver version

    An implementation may support additional properties for some devices.

    Restrictions
    ------------
    • These routines may not be called within an compute region.
    • If the value of property is not one of the known values for that query routine, or that
    property has no value for the specified device, acc_get_property will return 0 and
    acc_get_property_string will return NULL (in C or C++) or an blank string (in
    Fortran).
    """
    pass

def init(devtype: str) -> None:
    """
    Description
    -----------
    The acc_init routine also implicitly calls acc_set_device_type. A call to
    acc_init is functionally equivalent to a init directive with the matching device type argument,
    as described in Section 2.14.1.

    Restrictions
    ------------
    • This routine may not be called within a compute region.
    • If the device type specified is not available, the behavior is implementation-defined;
    in particular, the program may abort.
    • If the routine is called more than once without an intervening acc_shutdown call, with a
    different value for the device type argument, the behavior is implementation-defined.
    • If some accelerator regions are compiled to only use one device type, calling this routine with
    a different device type may produce undefined behavior.
    """
    pass

def shutdown(devtype: str) -> None:
    """
    Description
    -----------
    The acc_shutdown routine disconnects the program from any device of the
    specified device type. Any data that is present in the memory of any such device is immediately deallo2331 cated.

    Restrictions
    ------------
    • This routine may not be called during execution of a compute region.
    • If the program attempts to execute a compute region on a device or to access any data in
    the memory of a device after a call to acc_shutdown for that device type, the behavior is
    undefined.
    • If the program attempts to shut down the acc_device_host device type, the behavior is
    undefined.
    """
    pass

def async_test(i: int) -> int:
    """
    Description
    -----------
    The argument must be an async-argument as defined in Section 2.16.1 async clause.
    If that value did not appear in any async clauses, or if it did appear in one or more async clauses
    and all such asynchronous operations have completed on the current device, the acc_async_test
    routine will return with a nonzero value in C and C++, or .true. in Fortran.
    If some such asynchronous operations have not completed, the acc_async_test routine will return with a zero
    value in C and C++, or .false. in Fortran. If two or more threads share the same accelerator, the
    acc_async_test routine will return with a nonzero value or .true. only if all matching
    asynchronous operations initiated by this thread have completed; there is no guarantee that all matching
    asynchronous operations initiated by other threads have completed.
    """
    pass

def async_test_all() -> int:
    """
    Description
    -----------
    If all outstanding asynchronous operations have completed, the acc_async_test_all
    routine will return with a nonzero value in C and C++, or .true. in Fortran. If some asynchronous
    operations have not completed, the acc_async_test_all routine will return with a zero value
    in C and C++, or .false. in Fortran. If two or more threads share the same accelerator, the
    acc_async_test_all routine will return with a nonzero value or .true. only if all
    outstanding asynchronous operations initiated by this thread have completed; there is no guarantee that all
    asynchronous operations initiated by other threads have completed.
    """
    pass

def wait(i: int) -> None:
    """
    Description
    -----------
    The argument must be an async-argument as defined in Section 2.16.1 async clause.
    If that value appeared in one or more async clauses, the acc_wait routine will not return until
    the latest such asynchronous operation has completed on the current device. If two or more threads
    share the same accelerator, the acc_wait routine will return only if all matching asynchronous
    operations initiated by this thread have completed; there is no guarantee that all matching
    asynchronous operations initiated by other threads have completed. For compatibility with version 1.0,
    this routine may also be spelled acc_async_wait. A call to acc_wait is functionally
    equivalent to a wait directive with a matching wait argument and no async clause, as described in
    Section 2.16.3.
    """
    pass
