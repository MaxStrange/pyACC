"""
This module exposes a class for passing the internal control variables (ICVs)
to the backend.
"""

class ICVs:
    """
    Internal Control Variables.
    """
    def __init__(self, current_device_type, current_device_num, default_async):
        """
        From the spec:

        An OpenACC implementation acts as if there are internal control variables (ICVs) that control the
        behavior of the program. These ICVs are initialized by the implementation, and may be given
        values through environment variables and through calls to OpenACC API routines. The program
        can retrieve values through calls to OpenACC API routines.

        The ICVs are:
        - acc-current-device-type-var - controls which type of device is used.
        - acc-current-device-num-var - controls which device of the selected type is used.
        - acc-default-async-var - controls which asynchronous queue is used when none is specified in
          an async clause.
        """
        self.current_device_type = current_device_type
        self.current_device_num = current_device_num
        self.default_async = default_async
