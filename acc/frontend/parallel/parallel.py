"""
Summary
-------
This fundamental construct starts parallel execution on the current device.

Syntax
------
The syntax of the OpenACC parallel construct is

#pragma acc parallel [clause-list] new-line
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
- reduction( operator:var-list )
- copy( var-list )
- copyin( [readonly:]var-list )
- copyout( var-list )
- create( var-list )
- no_create( var-list )
- present( var-list )
- deviceptr( var-list )
- attach( var-list )
- private( var-list )
- firstprivate( var-list )
- default( none | present )

Description
-----------
When the program encounters an accelerator parallel construct, one or more
gangs of workers are created to execute the accelerator parallel region. The number of gangs, and
the number of workers in each gang and the number of vector lanes per worker remain constant for
the duration of that parallel region. Each gang begins executing the code in the structured block
in gang-redundant mode. This means that code within the parallel region, but outside of a loop
construct with gang-level worksharing, will be executed redundantly by all gangs.
One worker in each gang begins executing the code in the structured block of the construct. Note:
Unless there is a loop construct within the parallel region, all gangs will execute all the code within
the region redundantly.
If the async clause does not appear, there is an implicit barrier at the end of the accelerator parallel
region, and the execution of the local thread will not proceed until all gangs have reached the end
of the parallel region.
If there is no default(none) clause on the construct, the compiler will implicitly determine data
attributes for variables that are referenced in the compute construct that do not have predetermined
data attributes and do not appear in a data clause on the compute construct, a lexically containing
data construct, or a visible declare directive. If there is no default(present) clause
on the construct, an array or composite variable referenced in the parallel construct that does
not appear in a data clause for the construct or any enclosing data construct will be treated as if
it appeared in a copy clause for the parallel construct. If there is a default(present)
clause on the construct, the compiler will implicitly treat all arrays and composite variables without
predetermined data attributes as if they appeared in a present clause. A scalar variable referenced
in the parallel construct that does not appear in a data clause for the construct or any enclosing
data construct will be treated as if it appeared in a firstprivate clause.

Restrictions
------------
• A program may not branch into or out of an OpenACC parallel construct.
• A program must not depend on the order of evaluation of the clauses, or on any side effects
of the evaluations.
• Only the async, wait, num_gangs, num_workers, and vector_length clauses
may follow a device_type clause.
• At most one if clause may appear. In Fortran, the condition must evaluate to a scalar logical
value; in C or C++, the condition must evaluate to a scalar integer value.
• At most one default clause may appear, and it must have a value of either none or
present.

The copy, copyin, copyout, create, no_create, present, deviceptr, and attach
data clauses are described in Section 2.7 Data Clauses. The private and firstprivate
clauses are described in Sections 2.5.11 and Sections 2.5.12.
The device_type clause is de691 scribed in Section 2.4 Device-Specific Clauses.
"""
