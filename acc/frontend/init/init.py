"""
Summary
-------
The init directive tells the runtime to initialize the runtime for that device type.
This can be used to isolate any initialization cost from the computational cost, when collecting
performance statistics. If no device type is specified all devices will be initialized. An init
directive may be used in place of a call to the acc_init runtime API routine, as described in

Syntax
------
The syntax of the init directive is:
#pragma acc init [clause-list] new-line

where clause is one of the following:
-device_type ( device-type-list )
-device_num ( int-expr )
"""
