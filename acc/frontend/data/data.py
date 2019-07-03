"""
Summary
-------
The data construct defines vars to be allocated in the current device memory for
the duration of the region, whether data should be copied from local memory to the current device
memory upon region entry, and copied from device memory to local memory upon region exit.

Syntax
------
The syntax of the OpenACC data construct is

#pragma acc data [clause-list] new-line
structured block

where clause is one of the following:

- if( condition )
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
Data will be allocated in the memory of the current device and copied from local
memory to device memory, or copied back, as required.
The data clauses are described in Sec944 tion 2.7 Data Clauses. Structured reference counters are incremented for
data when entering a data region, and decremented when leaving the region, as described in Section 2.6.6 Reference Counters.
"""
