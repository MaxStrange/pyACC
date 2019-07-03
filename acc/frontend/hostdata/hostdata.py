"""
Summary
-------
The host_data construct makes the address of data in device memory available on
the host.

Syntax
------
The syntax of the OpenACC host_data construct is

#pragma acc host_data clause-list new-line
structured block

where clause is one of the following:

- use_device( var-list )
- if( condition )
- if_present

Description
-----------
This construct is used to make the address of data in device memory available in
host code.

Restrictions
------------
• A var in a use_device clause must be the name of a variable or array.
• At least one use_device clause must appear.
• At most one if clause may appear. In Fortran, the condition must evaluate to a scalar logical
value; in C or C++, the condition must evaluate to a scalar integer value.
• See Section 2.17 Fortran Optional Arguments for discussion of Fortran optional arguments in
use_device clauses.
"""
