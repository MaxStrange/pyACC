"""
Summary
-------
This construct defines a region of the program that is to be executed sequentially on
the current device.

Syntax
------
The syntax of the OpenACC serial construct is

#pragma acc serial [clause-list] new-line
structured block

where clause is one of the following:

- async [( int-expr )]
- wait [( int-expr-list )]
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
- private( var-list )
- firstprivate( var-list )
- attach( var-list )
- default( none | present )

Description
-----------
When the program encounters an accelerator serial construct, one gang of one
worker with a vector length of one is created to execute the accelerator serial region sequentially.
The single gang begins executing the code in the structured block in gang-redundant mode, even
though there is a single gang. The serial construct executes as if it were a parallel construct
with clauses num_gangs(1) num_workers(1) vector_length(1).
If the async clause does not appear, there is an implicit barrier at the end of the accelerator serial
region, and the execution of the local thread will not proceed until the gang has reached the end of
the serial region.
If there is no default(none) clause on the construct, the compiler will implicitly determine data
attributes for variables that are referenced in the compute construct that do not have predetermined
data attributes and do not appear in a data clause on the compute construct, a lexically containing
data construct, or a visible declare directive. If there is no default(present) clause
on the construct, an array or composite variable referenced in the serial construct that does
not appear in a data clause for the construct or any enclosing data construct will be treated as
if it appeared in a copy clause for the serial construct. If there is a default(present)
clause on the construct, the compiler will implicitly treat all arrays and composite variables without
predetermined data attributes as if they appeared in a present clause. A scalar variable referenced
in the serial construct that does not appear in a data clause for the construct or any enclosing
data construct will be treated as if it appeared in a firstprivate clause.

Restrictions
------------
• A program may not branch into or out of an OpenACC serial construct.
• A program must not depend on the order of evaluation of the clauses, or on any side effects
of the evaluations.
• Only the async and wait clauses may follow a device_type clause.
• At most one if clause may appear. In Fortran, the condition must evaluate to a scalar logical
value; in C or C++, the condition must evaluate to a scalar integer value.
• At most one default clause may appear, and it must have a value of either none or
present.
The copy, copyin, copyout, create, no_create, present, deviceptr, and attach
data clauses are described in Section 2.7 Data Clauses. The private and firstprivate
clauses are described in Sections 2.5.11 and Sections 2.5.12. The device_type clause is
described in Section 2.4 Device-Specific Clauses
"""
