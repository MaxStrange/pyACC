"""
Summary
-------
The routine directive is used to tell the compiler to compile a given procedure for
an accelerator as well as for the host. In a file or routine with a procedure call, the routine
directive tells the implementation the attributes of the procedure when called on the accelerator.

Syntax
------
The syntax of the routine directive is:
#pragma acc routine clause-list new-line
#pragma acc routine ( name ) clause-list new-line

In C and C++, the routine directive without a name may appear immediately before a function
definition or just before a function prototype and applies to that immediately following function or
prototype. The routine directive with a name may appear anywhere that a function prototype
is allowed and applies to the function in that scope with that name, but must appear before any
definition or use of that function.

A C or C++ function or Fortran subprogram compiled with the routine directive for an
accelerator is called an accelerator routine.

The clause is one of the following:
- gang
- worker
- vector
- seq
- bind( name )
- bind( string )
- device_type( device-type-list )
- nohost

A gang, worker, vector, or seq clause specifies the level of parallelism in the routine.
"""
