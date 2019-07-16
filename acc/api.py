"""
The main accelerator decorator and load_back_end function.

These two functions are the only API functions from an end-user's perspective.
"""
import acc.frontend.util.errors as errors
import acc.frontend.util.util as util
import acc.frontend.frontend as frontend
import acc.ir.metavars as metavars
import acc.ir.icv as icv
import acc.ir.intrep as intrep
import dill
import functools
import inspect
import os
import sys

# The default device type, used if not overridden by the user
DEFAULT_DEVICE_TYPE = 'host'

# The default device number, used if not overridden by the user
DEFAULT_DEVICE_NUM  = 0

# The default asynchronous queue, used when not specified by async clauses
DEFAULT_ASYNC       = 0

# The back end
back = None

# The control variables
icvs = None

def _initialize_acc():
    """
    Initializes the OpenACC runtime if not already initialized. This should
    wrap every runtime API function.
    """
    def decorate(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _construct_icvs()
            if back is None:
                load_back_end()
            return func(*args, **kwargs)
        return wrapper
    return decorate

def acc():
    """
    The main accelerator decorator.

    Usage:

    ```python
    @acc()
    def function_to_accelerate(data, ret):
        #pragma acc parallel loop copyout=ret[0:len(data)]
        for d in data:
            ret.append(d ** 2)
    ```

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
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Initialize the OpenACC internal control variables if not already initialized
            _construct_icvs()
            if back is None:
                load_back_end(back_end=icvs.current_device_type)
            try:
                getattr(back, "compile")
            except AttributeError:
                raise ImportError("Back end does not have a 'compile' function.")

            # Grab the source code from the decorated function
            source = dill.source.getsource(func).splitlines()[1:]  # strip the decorator
            source = os.linesep.join(source)

            # Grab the decorated function's signature
            signature = inspect.signature(func)

            # Grab the top of the stack
            stackframe = inspect.stack()[1]

            # Grab the decorated function's modules
            module = sys.modules[func.__module__]
            mods_mods = util.get_modules_from_module(module)

            # Put together all the stuff we need in order to rewrite the function
            funcname = func.__name__
            meta_data = metavars.MetaVars(src=source, stackframe=stackframe, signature=signature, funcs_name=funcname, funcs_module=module, funcs_mods=mods_mods)

            intermediate_rep = intrep.IntermediateRepresentation(meta_data, icvs)
            dbg = errors.Debug(intermediate_rep)
            for pragma, linenumber in frontend.parse_pragmas(intermediate_rep.src, *args, **kwargs):
                dbg.lineno = linenumber
                # Side-effect-y: this function modifies intermediate_rep each time
                frontend.accumulate_pragma(intermediate_rep, pragma, linenumber, dbg, *args, **kwargs)

            # Pass the intermediate representation into the backend to get the new source code
            new_source = back.compile(intermediate_rep)

            # Dump the source code that we created into a file
            oldmodulesource = dill.source.getsource(module)
            signature_line = "def {}{}:".format(func.__name__, signature)
            signature_line_number = oldmodulesource.splitlines().index(signature_line) - 1 # deal with decorator
            last_line_number = len(source.splitlines()) + signature_line_number + 1
            newmodulesource = _replace_source(oldmodulesource, new_source, signature_line_number, last_line_number)
            fpath = util.compile_kernel_module(newmodulesource)

            # Import the new module.
            mod = util.load_kernel_module(fpath)

            # Return the result of executing the newly written function.
            func_to_execute = getattr(mod, funcname)
            return func_to_execute(*args, **kwargs)
        return wrapper
    return decorate

def load_back_end(back_end="host"):
    """
    Call this function and pass in a module name as a string.
    This will load the given back end. If "default" is passed in,
    it will use the default back end.
    """
    if back_end.lower() == "host":
        back_end = "acc.backend.host"
    elif back_end.lower() == "nvidia":
        back_end = "acc.backend.cuda"
    elif back_end.lower() == "radeon":
        back_end = "acc.backend.opencl"

    # Set the back end to whatever is the last item in a string of x.y.z...
    global back
    back = __import__(back_end)
    components = back_end.split('.')
    for comp in components[1:]:
        back = getattr(back, comp)

@_initialize_acc()
def get_num_devices(devtype: str) -> int:
    """
    Returns the number of devices of the given type.
    """
    pass

@_initialize_acc()
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
    - If the device type specified is not available, the behavior is implementation-defined; in
      particular, the program may abort.
    - If some compute regions are compiled to only use one device type, calling this routine with a
      different device type may produce undefined behavior.
    """
    icvs.current_device_type = devtype
    load_back_end(icvs.current_device_type)

@_initialize_acc()
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
    - If the device type has not yet been selected, the value acc_device_none may be returned.
    """
    return icvs.current_device_type

@_initialize_acc()
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
    - If the value of devicenum is greater than or equal to the value returned by acc_get_num_devices
      for that device type, the behavior is implementation-defined.
    - Calling acc_set_device_num implies a call to acc_set_device_type with that
      device type argument.
    """
    pass

@_initialize_acc()
def get_device_num(devtype: str) -> int:
    """
    The acc_get_device_num routine returns the value of acc-current-device-num-var for the current thread.
    """
    pass

@_initialize_acc()
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

@_initialize_acc()
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

@_initialize_acc()
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

@_initialize_acc()
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

@_initialize_acc()
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

@_initialize_acc()
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

@_initialize_acc()
def wait_async(w: int, a: int) -> None:
    """
    Description
    -----------
    The arguments must be async-arguments, as defined in Section 2.16.1 async clause.
    The routine will enqueue a wait operation on the appropriate device queue associated with the
    second argument, which will wait for operations enqueued on the device queue associated with
    the first argument. See Section 2.16 Asynchronous Behavior for more information. A call to
    acc_wait_async is functionally equivalent to a wait directive with a matching wait argument
    and a matching async argument, as described in Section 2.16.3.
    """
    pass

@_initialize_acc()
def wait_all() -> None:
    """
    Description
    -----------
    The acc_wait_all routine will not return until all the asynchronous operations
    have completed. If two or more threads share the same accelerator, the acc_wait_all routine
    will return only if all asynchronous operations initiated by this thread have completed; there is no
    guarantee that all asynchronous operations initiated by other threads have completed. For com2393 patibility with version 1.0, this routine may also be spelled acc_async_wait_all. A call to
    acc_wait_all is functionally equivalent to a wait directive with no wait argument list and no
    async argument, as described in Section 2.16.3.
    """
    pass

@_initialize_acc()
def wait_all_async(i: int) -> None:
    """
    Description
    -----------
    The argument must be an async-argument as defined in Section 2.16.1 async clause.
    The routine will enqueue a wait operation on the appropriate device queue for each other device
    queue. See Section 2.16 Asynchronous Behavior for more information. A call to acc_wait_all_async
    is functionally equivalent to a wait directive with no wait argument list and a matching async
    argument, as described in Section 2.16.3.
    """
    pass

@_initialize_acc()
def get_default_async() -> int:
    """
    Description
    -----------
    The acc_get_default_async routine returns the value of
    acc-default-async-var for the current thread, which is the asynchronous queue used when an async clause appears
    without an async-argument or with the value acc_async_noval.
    """
    pass

@_initialize_acc()
def set_default_async(i: int) -> None:
    """
    Description
    -----------
    The acc_set_default_async routine tells the runtime to place any directives
    with an async clause that does not have an async-argument or with the special acc_async_noval
    value into the specified asynchronous activity queue instead of the default asynchronous activity
    queue for that device by setting the value of acc-default-async-var for the current thread. The
    special argument acc_async_default will reset the default asynchronous activity queue to the
    initial value, which is implementation-defined. A call to acc_set_default_async is
    functionally equivalent to a set default_async directive with a matching argument in int-expr, as
    described in Section 2.14.3.
    """
    pass

@_initialize_acc()
def on_device(devtype: str) -> int:
    """
    Description
    -----------
    The acc_on_device routine may be used to execute different paths
    depending on whether the code is running on the host or on some accelerator. If the acc_on_device
    routine has a compile-time constant argument, it evaluates at compile time to a constant. The
    argument must be one of the defined accelerator types. If the argument is acc_device_host,
    then outside of a compute region or accelerator routine, or in a compute region or accelerator
    routine that is executed on the host CPU, this routine will evaluate to nonzero for C or C++, and
    .true. for Fortran; otherwise, it will evaluate to zero for C or C++, and .false. for Fortran.
    If the argument is acc_device_not_host, the result is the negation of the result with
    argument acc_device_host. If the argument is an accelerator device type, then in a compute region
    or routine that is executed on a device of that type, this routine will evaluate to nonzero for C or
    C++, and .true. for Fortran; otherwise, it will evaluate to zero for C or C++, and .false. for
    Fortran. The result with argument acc_device_default is undefined.
    """
    pass

@_initialize_acc()
def malloc(nbytes: int):
    """
    Description
    -----------
    The acc_malloc routine may be used to allocate space in the current device
    memory. Pointers assigned from this function may be used in deviceptr clauses to tell the
    compiler that the pointer target is resident on the device. In case of an error, acc_malloc returns
    a NULL pointer.
    """
    pass

@_initialize_acc()
def free():
    """
    Description
    -----------
    The acc_free routine will free previously allocated space in the current device
    memory; the argument should be a pointer value that was returned by a call to acc_malloc. If
    the argument is a NULL pointer, no operation is performed.
    """
    pass

@_initialize_acc()
def copyin(buf, size):
    """
    Description
    -----------
    The acc_copyin routines are equivalent to the enter data directive with a
    copyin clause, as described in Section 2.7.6. In C, the arguments are a pointer to the data and
    length in bytes; the synchronous function returns a pointer to the allocated device memory, as with
    acc_malloc. In Fortran, two forms are supported. In the first, the argument is a contiguous array
    section of intrinsic type. In the second, the first argument is a variable or array element and the
    second is the length in bytes.
    The behavior of the acc_copyin routines is:
    • If the data is in shared memory, no action is taken. The C acc_copyin returns the incoming
    pointer.
    • If the data is present in the current device memory, a present increment action with the
    dynamic reference counter is performed. The C acc_copyin returns a pointer to the existing
    device memory.
    • Otherwise, a copyin action with the appropriate reference counter is performed. The C
    acc_copyin returns the device address of the newly allocated memory.
    This data may be accessed using the present data clause. Pointers assigned from the C acc_copyin
    function may be used in deviceptr clauses to tell the compiler that the pointer target is resident
    on the device.
    The _async versions of this function will perform any data transfers asynchronously on the async
    queue associated with the value passed in as the async argument. The function may return
    before the data has been transferred; see Section 2.16 Asynchronous Behavior for more details. The
    synchronous versions will not return until the data has been completely transferred.
    For compatibility with OpenACC 2.0, acc_present_or_copyin and acc_pcopyin are
    alternate names for acc_copyin.
    """
    pass

@_initialize_acc()
def create():
    """
    Description
    -----------
    The acc_create routines are equivalent to the enter data directive with a
    create clause, as described in Section 2.7.8. In C, the arguments are a pointer to the data and
    length in bytes; the synchronous function returns a pointer to the allocated device memory, as with
    acc_malloc. In Fortran, two forms are supported. In the first, the argument is a contiguous array
    section of intrinsic type. In the second, the first argument is a variable or array element and the
    second is the length in bytes.

    The behavior of the acc_create routines is:
    • If the data is in shared memory, no action is taken. The C acc_create returns the incoming
    pointer.
    • If the data is present in the current device memory, a present increment action with the
    dynamic reference counter is performed. The C acc_create returns a pointer to the existing
    device memory.
    • Otherwise, a create action with the appropriate reference counter is performed. The C acc_create
    returns the device address of the newly allocated memory.
    This data may be accessed using the present data clause. Pointers assigned from the C acc_copyin
    function may be used in deviceptr clauses to tell the compiler that the pointer target is resident
    on the device.
    The _async versions of these function may perform the data allocation asynchronously on the
    async queue associated with the value passed in as the async argument. The synchronous versions
    will not return until the data has been allocated.
    For compatibility with OpenACC 2.0, acc_present_or_create and acc_pcreate are
    alternate names for acc_create.
    """
    pass

@_initialize_acc()
def copyout():
    """
    Description
    -----------
    The acc_copyout routines are equivalent to the exit data directive with a
    copyout clause, and the acc_copyout_finalize routines are equivalent to the exit data
    directive with both copyout and finalize clauses, as described in Section 2.7.7. In C, the
    arguments are a pointer to the data and length in bytes. In Fortran, two forms are supported. In the
    first, the argument is a contiguous array section of intrinsic type. In the second, the first argument
    is a variable or array element and the second is the length in bytes.

    The behavior of the acc_copyout routines is:
    • If the data is in shared memory, no action is taken.
    • Otherwise, if the data is not present in the current device memory, a runtime error is issued.
    • Otherwise, a present decrement action with the dynamic reference counter is performed (acc_copyout),
    or the dynamic reference counter is set to zero (acc_copyout_finalize). If both
    reference counters are then zero, a copyout action is performed.

    The _async versions of these functions will perform any associated data transfers asynchronously
    on the async queue associated with the value passed in as the async argument. The function may
    return before the data has been transferred or deallocated; see Section 2.16 Asynchronous Behavior
    for more details. The synchronous versions will not return until the data has been completely
    transferred. Even if the data has not been transferred or deallocated before the function returns, the data
    will be treated as not present in the current device memory.
    """
    pass

@_initialize_acc()
def delete():
    """
    Description
    -----------
    The acc_delete routines are equivalent to the exit data directive with a
    delete clause,
    and the acc_delete_finalize routines are equivalent to the exit data directive with both
    delete clause and finalize clauses, as described in Section 2.7.10. The arguments are as for
    acc_copyout.

    The behavior of the acc_delete routines is:
    • If the data is in shared memory, no action is taken.
    • Otherwise, if the data is not present in the current device memory, a runtime error is issued.
    • Otherwise, a present decrement action with the dynamic reference counter is performed (acc_delete),
    or the dynamic reference counter is set to zero (acc_delete_finalize). If both
    reference counters are then zero, a delete action is performed.

    The _async versions of these function may perform the data deallocation asynchronously on the
    async queue associated with the value passed in as the async argument. The synchronous versions
    will not return until the data has been deallocated. Even if the data has not been deallocated before
    the function returns, the data will be treated as not present in the current device memory.
    """
    pass

@_initialize_acc()
def update_device():
    """
    Description
    -----------

    The acc_update_device routine is equivalent to the update directive with a
    device clause, as described in Section 2.14.4. In C, the arguments are a pointer to the data and
    length in bytes. In Fortran, two forms are supported. In the first, the argument is a contiguous array
    section of intrinsic type. In the second, the first argument is a variable or array element and the
    second is the length in bytes. For data not in shared memory, the data in the local memory is copied
    to the corresponding device memory. It is a runtime error to call this routine if the data is not present
    in the current device memory.

    The _async versions of this function will perform the data transfers asynchronously on the async
    queue associated with the value passed in as the async argument. The function may return
    before the data has been transferred; see Section 2.16 Asynchronous Behavior for more details. The
    synchronous versions will not return until the data has been completely transferred.
    """
    pass

@_initialize_acc()
def update_self():
    """
    Description
    -----------
    The acc_update_self routine is equivalent to the update directive with a
    self clause, as described in Section 2.14.4. In C, the arguments are a pointer to the data and
    length in bytes. In Fortran, two forms are supported. In the first, the argument is a contiguous array
    section of intrinsic type. In the second, the first argument is a variable or array element and the
    second is the length in bytes. For data not in shared memory, the data in the local memory is copied
    to the corresponding device memory. There must be a device copy of the data on the device when
    calling this routine, otherwise no action is taken by the routine. It is a runtime error to call this
    routine if the data is not present in the current device memory.

    The _async versions of this function will perform the data transfers asynchronously on the async
    queue associated with the value passed in as the async argument. The function may return
    before the data has been transferred; see Section 2.16 Asynchronous Behavior for more details. The
    synchronous versions will not return until the data has been completely transferred.
    """
    pass

@_initialize_acc()
def map_data():
    """
    Description
    -----------
    The acc_map_data routine is similar to an enter data directive with a create
    clause, except instead of allocating new device memory to start a data lifetime, the device address
    to use for the data lifetime is specified as an argument. The first argument is a host address,
    followed by the corresponding device address and the data length in bytes. After this call, when the
    host data appears in a data clause, the specified device memory will be used. It is an error to call
    acc_map_data for host data that is already present in the current device memory. It is undefined
    to call acc_map_data with a device address that is already mapped to host data. The device
    address may be the result of a call to acc_malloc, or may come from some other device-specific
    API routine. After mapping the device memory, the dynamic reference count for the host data is set
    to one, but no data movement will occur. Memory mapped by acc_map_data may not have the
    associated dynamic reference count decremented to zero, except by a call to acc_unmap_data.
    See Section 2.6.6 Reference Counters.
    """
    pass

@_initialize_acc()
def unmap_data():
    """
    Description
    -----------
    The acc_unmap_data routine is similar to an exit data directive with a
    delete clause, except the device memory is not deallocated. The argument is pointer to the host
    data. A call to this routine ends the data lifetime for the specified host data. The device memory is
    not deallocated. It is undefined behavior to call acc_unmap_data with a host address unless that
    host address was mapped to device memory using acc_map_data. After unmapping memory the
    dynamic reference count for the pointer is set to zero, but no data movement will occur. It is an
    error to call acc_unmap_data if the structured reference count for the pointer is not zero. See
    Section 2.6.6 Reference Counters.
    """
    pass

@_initialize_acc()
def deviceptr():
    """
    Description
    -----------
    The acc_deviceptr routine returns the device pointer associated with a host
    address. The argument is the address of a host variable or array that has an active lifetime on the
    current device. If the data is not present in the current device memory, the routine returns a NULL
    value.
    """
    pass

@_initialize_acc()
def hostptr():
    """
    Description
    -----------
    The acc_hostptr routine returns the host pointer associated with a device
    address. The argument is the address of a device variable or array, such as that returned from acc_deviceptr,
    acc_create or acc_copyin. If the device address is NULL, or does not correspond to any host
    address, the routine returns a NULL value
    """
    pass

@_initialize_acc()
def is_present():
    """
    Description
    -----------
    The acc_is_present routine tests whether the specified host data is accessible
    from the current device. In C, the arguments are a pointer to the data and length in bytes; the
    function returns nonzero if the specified data is fully present, and zero otherwise. In Fortran, two
    forms are supported. In the first, the argument is a contiguous array section of intrinsic type. In the
    second, the first argument is a variable or array element and the second is the length in bytes. The
    function returns .true. if the specified data is in shared memory or is fully present, and .false.
    otherwise. If the byte length is zero, the function returns nonzero in C or .true. in Fortran if the
    given address is in shared memory or is present at all in the current device memory.
    """
    pass

@_initialize_acc()
def memcpy_to_device():
    """
    Description
    -----------
    The acc_memcpy_to_device routine copies bytes of data from the local
    address in src to the device address in dest. The destination address must be an address accessible
    from the current device, such as an address returned from acc_malloc or acc_deviceptr, or
    an address in shared memory.

    The _async version of this function will perform the data transfers asynchronously on the async
    queue associated with the value passed in as the async argument. The function may return
    before the data has been transferred; see Section 2.16 Asynchronous Behavior for more details. The
    synchronous versions will not return until the data has been completely transferred.
    """
    pass

@_initialize_acc()
def memcpy_from_device():
    """
    Description
    -----------
    The acc_memcpy_from_device routine copies bytes data from the device
    address in src to the local address in dest. The source address must be an address accessible
    from the current device, such as an addressed returned from acc_malloc or acc_deviceptr,
    or an address in shared memory.

    The _async version of this function will perform the data transfers asynchronously on the async
    queue associated with the value passed in as the async argument. The function may return
    before the data has been transferred; see Section 2.16 Asynchronous Behavior for more details. The
    synchronous versions will not return until the data has been completely transferred.
    """
    pass

@_initialize_acc()
def memcpy_device():
    """
    Description
    -----------
    The acc_memcpy_device routine copies bytes data from the device address
    in src to the device address in dest. Both addresses must be addresses in the current device
    memory, such as would be returned from acc_malloc or acc_deviceptr. If dest and src
    overlap, the behavior is undefined.

    The _async version of this function will perform the data transfers asynchronously on the async
    queue associated with the value passed in as the async argument. The function may return
    before the data has been transferred; see Section 2.16 Asynchronous Behavior for more details. The
    synchronous versions will not return until the data has been completely transferred.
    """
    pass

@_initialize_acc()
def attach():
    """
    Description
    -----------
    The acc_attach routines are passed the address of a host pointer. If the data is
    in shared memory, or if the pointer *ptr is in shared memory or is not present in the current device
    memory, or the address to which the *ptr points is not present in the current device memory, no
    action is taken. Otherwise, these routines perform the attach action (Section 2.7.2).
    These routines may issue a data transfer from local memory to device memory. The _async
    version of this function will perform the data transfers asynchronously on the async queue associated
    with the value passed in as the async argument. The function may return before the data has been
    transferred; see Section 2.16 Asynchronous Behavior for more details. The synchronous version
    will not return until the data has been completely transferred.
    """
    pass

@_initialize_acc()
def detach():
    """
    Description
    -----------
    The acc_detach routines are passed the address of a host pointer. If the data is
    in shared memory, or if the pointer *ptr is in shared memory or is not present in the current device
    memory, if the attachment counter for the pointer *ptr is zero, no action is taken. Otherwise, these
    routines perform the detach action (Section 2.7.2).

    The acc_detach_finalize routines are equivalent to an exit data directive with detach
    and finalize clauses, as described in Section 2.7.12 detach clause. If the data is in shared
    memory,or if the pointer *ptr is not present in the current device memory, or if the attachment
    counter for the pointer *ptr is zero, no action is taken. Otherwise, these routines perform the
    immediate detach action (Section 2.7.2).

    These routines may issue a data transfer from local memory to device memory. The _async
    versions of these functions will perform the data transfers asynchronously on the async queue
    associated with the value passed in as the async argument. These functions may return before the data
    has been transferred; see Section 2.16 Asynchronous Behavior for more details. The synchronous
    versions will not return until the data has been completely transferred.
    """
    pass

def _construct_icvs():
    """
    Construct the ICVs object out of the environment variables
    and/or values that have been set by runtime API calls.
    """
    global icvs
    if icvs is None:
        current_device_type = os.environ.get('ACC_DEVICE_TYPE', default=DEFAULT_DEVICE_TYPE)
        current_device_num = os.environ.get('ACC_DEVICE_NUM', default=DEFAULT_DEVICE_NUM)
        default_async = DEFAULT_ASYNC

        icvs = icv.ICVs(current_device_type, current_device_num, default_async)

def _replace_source(oldsrc, newsrc, startlineno, endlineno):
    """
    Removes lines from oldsrc starting at startlineno and going through endlineno,
    then puts newsrc in that location instead and returns the result.
    """
    lines = oldsrc.splitlines()
    lines[startlineno:endlineno] = newsrc.splitlines()
    return os.linesep.join(lines)
