"""
Summary
-------
This construct defines a region of the program that is to be compiled into a sequence
of kernels for execution on the current device.

Syntax
------
The syntax of the OpenACC kernels construct is

#pragma acc kernels [clause-list] new-line
structured block

where clause is one of the following:

- async [( int-expr )]
- wait [( int-expr-list )]
- num_gangs( int-expr )
- num_workers( int-expr )
- vector_length( int-expr )
- device_type( device-type-list )
- if( condition )
- self [( condition )]
- copy( var-list )
- copyin( [readonly:]var-list )
- copyout( var-list )
- create( var-list )
- no_create( var-list )
- present( var-list )
- deviceptr( var-list )
- attach( var-list )
- default( none | present )

Description
-----------
The compiler will split the code in the kernels region into a sequence of acceler699 ator kernels.
Typically, each loop nest will be a distinct kernel. When the program encounters a
kernels construct, it will launch the sequence of kernels in order on the device. The number and
configuration of gangs of workers and vector length may be different for each kernel.
If the async clause does not appear, there is an implicit barrier at the end of the kernels region, and
the local thread execution will not proceed until all kernels have completed execution.
If there is no default(none) clause on the construct, the compiler will implicitly determine data
attributes for variables that are referenced in the compute construct that do not have predetermined
data attributes and do not appear in a data clause on the compute construct, a lexically containing
data construct, or a visible declare directive. If there is no default(present) clause
on the construct, an array or composite variable referenced in the kernels construct that does
not appear in a data clause for the construct or any enclosing data construct will be treated as
if it appeared in a copy clause for the kernels construct. If there is a default(present)
clause on the construct, the compiler will implicitly treat all arrays and composite variables without
predetermined data attributes as if they appeared in a present clause. A scalar variable referenced
in the kernels construct that does not appear in a data clause for the construct or any enclosing
data construct will be treated as if it appeared in a copy clause.

Restrictions
------------
• A program may not branch into or out of an OpenACC kernels construct.
• A program must not depend on the order of evaluation of the clauses, or on any side effects
of the evaluations.
• Only the async, wait, num_gangs, num_workers, and vector_length clauses
may follow a device_type clause.
• At most one if clause may appear. In Fortran, the condition must evaluate to a scalar logical
value; in C or C++, the condition must evaluate to a scalar integer value.
• At most one default clause may appear, and it must have a value of either none or
present.

The copy, copyin, copyout, create, no_create, present, deviceptr, and attach
data clauses are described in Section 2.7 Data Clauses. The device_type clause is described in
Section 2.4 Device-Specific Clauses.
"""
