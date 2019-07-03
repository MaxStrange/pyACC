"""
Summary
-------
The shutdown directive tells the runtime to shut down the connection to the given
accelerator, and free any runtime resources. A shutdown directive may be used in place of a call
to the acc_shutdown runtime API routine, as described in Section 3.2.8.

Syntax
------
The syntax of the shutdown directive is:
#pragma acc shutdown [clause-list] new-line

where clause is one of the following:
- device_type ( device-type-list )
- device_num ( int-expr )
"""
