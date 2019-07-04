"""
Summary
-------
The wait directive causes the local thread to wait for completion of asynchronous
operations on the current device, such as an accelerator parallel, kernels, or serial region or an
update directive, or causes one device activity queue to synchronize with one or more other
activity queues on the current device.

Syntax
------
The syntax of the wait directive is:
#pragma acc wait [( int-expr-list )] [clause-list] new-line

where clause is:
- async [( int-expr )]

The wait argument, if it appears, must be one or more async-arguments.

If there is no wait argument and no async clause, the local thread will wait until all operations
enqueued by this thread on any activity queue on the current device have completed.

If there are one or more int-expr expressions and no async clause, the local thread will wait until all
operations enqueued by this thread on each of the associated device activity queues have completed.

If there are two or more threads executing and sharing the same device, a wait directive with no
async clause will cause the local thread to wait until all of the appropriate asynchronous
operations previously enqueued by that thread have completed. To guarantee that operations have been
enqueued by other threads requires additional synchronization between those threads. There is no
guarantee that all the similar asynchronous operations initiated by other threads will have completed.

If there is an async clause, no new operation may be launched or executed on the async
activity queue on the current device until all operations enqueued up to this point by this thread on the
asynchronous activity queues associated with the wait argument have completed. One legal
implementation is for the local thread to wait for all the associated asynchronous device activity queues.
Another legal implementation is for the thread to enqueue a synchronization operation in such a
way that no new operation will start until the operations enqueued on the associated asynchronous
device activity queues have completed.

A wait directive is functionally equivalent to a call to one of the acc_wait, acc_wait_async,
acc_wait_all or acc_wait_all_async runtime API routines, as described in Sections 3.2.11,
3.2.12, 3.2.13 and 3.2.14.
"""
