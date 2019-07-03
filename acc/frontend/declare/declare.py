"""
Summary
-------
A declare directive is used in the declaration section of a Fortran subroutine,
function, or module, or following a variable declaration in C or C++. It can specify that a var is to be
allocated in device memory for the duration of the implicit data region of a function, subroutine
or program, and specify whether the data values are to be transferred from local memory to device
memory upon entry to the implicit data region, and from device memory to local memory upon exit
from the implicit data region. These directives create a visible device copy of the var.

Syntax
------
The syntax of the declare directive is:

#pragma acc declare clause-list new-line

where clause is one of the following:
- copy( var-list )
- copyin( [readonly:]var-list )
- copyout( var-list )
- create( var-list )
- present( var-list )
- deviceptr( var-list )
- device_resident( var-list )
- link( var-list )

The associated region is the implicit region associated with the function, subroutine, or program in
which the directive appears. If the directive appears in the declaration section of a Fortran module
subprogram or in a C or C++ global scope, the associated region is the implicit region for the whole
program. The copy, copyin, copyout, present, and deviceptr data clauses are described
in Section 2.7 Data Clauses.

Restrictions
------------
• A declare directive must appear in the same scope as any var in any of the data clauses on
the directive.
• A var in a declare declare must be a variable or array name, or a Fortran common block
name between slashes.
• A var may appear at most once in all the clauses of declare directives for a function,
subroutine, program, or module.
• In Fortran, assumed-size dummy arrays may not appear in a declare directive.
• In Fortran, pointer arrays may be specified, but pointer association is not preserved in device
memory.
• In a Fortran module declaration section, only create, copyin, device_resident, and
link clauses are allowed.
• In C or C++ global scope, only create, copyin, deviceptr, device_resident and
link clauses are allowed.
• C and C++ extern variables may only appear in create, copyin, deviceptr, device_resident
and link clauses on a declare directive.
• In C and C++, only global and extern variables may appear in a link clause. In Fortran,
only module variables and common block names (enclosed in slashes) may appear in a link
clause.
• In C or C++, a longjmp call in the region must return to a setjmp call within the region.
• In C++, an exception thrown in the region must be handled within the region.
• See Section 2.17 Fortran Optional Arguments for discussion of Fortran optional dummy
arguments in data clauses, including device_resident clauses.
"""
