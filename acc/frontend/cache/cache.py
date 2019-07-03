"""
Summary
-------
The cache directive may appear at the top of (inside of) a loop. It specifies array
elements or subarrays that should be fetched into the highest level of the cache for the body of the
loop.

Syntax
------
The syntax of the cache directive is

#pragma acc cache( [readonly:]var-list ) new-line

A var in a cache directive must be a single array element or a simple subarray. In C and C++,
a simple subarray is an array name followed by an extended array range specification in brackets,
with start and length, such as

arr[lower:length]

where the lower bound is a constant, loop invariant, or the for loop index variable plus or minus a
constant or loop invariant, and the length is a constant.

The lower bounds must be constant, loop invariant, or the do loop index variable plus or minus
a constant or loop invariant; moreover the difference between the corresponding upper and lower
bounds must be a constant.

If the optional readonly modifier appears, then the implementation may assume that the data
referenced by any var in that directive is never written to within the applicable region.

Restrictions
------------
• If an array element or subarray is listed in a cache directive, all references to that array
during execution of that loop iteration must not refer to elements of the array outside the
index range specified in the cache directive.
• See Section 2.17 Fortran Optional Arguments for discussion of Fortran optional arguments in
cache directives.
"""
