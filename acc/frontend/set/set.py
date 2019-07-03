"""
Summary
-------
The set directive provides a means to modify internal control variables using
directives. Each form of the set directive is functionally equivalent to a matching runtime API routine.

Syntax
------
The syntax of the set directive is:
#pragma acc set [clause-list] new-line

where clause is one of the following
- default_async ( int-expr )
- device_num ( int-expr )
- device_type ( device-type-list )
"""
