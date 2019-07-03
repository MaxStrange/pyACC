"""
Summary
-------
An enter data directive may be used to define vars to be allocated in the current
device memory for the remaining duration of the program, or until an exit data directive that
deallocates the data. They also tell whether data should be copied from local memory to device
memory at the enter data directive, and copied from device memory to local memory at the
exit data directive. The dynamic range of the program between the enter data directive and
the matching exit data directive is the data lifetime for that data.

Syntax
------
The syntax of the OpenACC enter data directive is

#pragma acc enter data clause-list new-line

where clause is one of the following:

- if( condition )
- async [( int-expr )]
- wait [( int-expr-list )]
- copyin( var-list )
- create( var-list )
- attach( var-list )

The syntax of the OpenACC exit data directive is
#pragma acc exit data clause-list new-line

where clause is one of the following:

- if( condition )
- async [( int-expr )]
- wait [( int-expr-list )]
- copyout( var-list )
- delete( var-list )
- detach( var-list )
- finalize

Description
-----------
At an enter data directive, data may be allocated in the current device memory and copied from local memory to device memory.
This action enters a data lifetime for those
vars, and will make the data available for present clauses on constructs within the data lifetime.
Dynamic reference counters are incremented for this data, as described in Section 2.6.6 Reference Counters.
Pointers in device memory may be attached to point to the corresponding
device copy of the host pointer target.
At an exit data directive, data may be copied from device memory to local memory and deal located from device memory.
If no finalize clause appears, dynamic reference counters are
decremented for this data. If a finalize clause appears, the dynamic reference counters are set
to zero for this data. Pointers in device memory may be detached so as to have the same value as
the original host pointer.
The data clauses are described in Section 2.7 Data Clauses.
Reference counting behavior is described in Section 2.6.6 Reference Counters.
"""
