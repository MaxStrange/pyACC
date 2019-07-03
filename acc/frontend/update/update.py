"""
Summary
-------
The update directive is used during the lifetime of accelerator data to update vars
in local memory with values from the corresponding data in device memory, or to update vars in
device memory with values from the corresponding data in local memory.

Syntax
------
The syntax of the update directive is:
#pragma acc update clause-list new-line

where clause is one of the following:
- async [( int-expr )]
- wait [( int-expr-list )]
- device_type( device-type-list )
- if( condition )
- if_present
- self( var-list )
- host( var-list )
- device( var-list )

Multiple subarrays of the same array may appear in a var-list of the same or different clauses on
the same directive. The effect of an update clause is to copy data from device memory to local
memory for update self, and from local memory to device memory for update device. The
updates are done in the order in which they appear on the directive. At least one self, host, or
device clause must appear on the directive.
"""
