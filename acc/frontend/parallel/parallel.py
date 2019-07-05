import acc.frontend.commonclauses as commonclauses
import acc.ir.intrep as intrep
import acc.frontend.loop.loop as loop
import ast
import asttokens

class ParallelNode(intrep.IrNode):
    """
    Node for the IntermediateRepresentation tree that is used for parallel constructs.
    """
    def __init__(self, lineno: int):
        super().__init__(lineno)
        self.async_ = None
        self.wait = None
        self.num_gangs = None
        self.num_workers = None
        self.vector_length = None
        self.device_type = None
        self.if_ = None
        self.self_ = None
        self.reduction = None
        self.copy = None
        self.copyin = None
        self.copyout = None
        self.create = None
        self.no_create = None
        self.present = None
        self.deviceptr = None
        self.attach = None
        self.private = None
        self.firstprivate = None
        self.default = None

def parallel(clauses, intermediate_rep, lineno, *args, **kwargs):
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
    The device_type clause is described in Section 2.4 Device-Specific Clauses.
    """
    parallel_node = ParallelNode(lineno)
    index = 0
    while index != -1:
        index = _apply_clause(index, clauses, intermediate_rep, parallel_node)
    intermediate_rep.add_child(parallel_node)

def _apply_clause(index, clause_list, intermediate_rep, loop_node):
    """
    Consumes however much of the clause list as necessary to apply the clause
    found at index in the clause_list.

    @param index:               The index into the clause_list of the clause we are
                                interested in.

    @param clause_list:         The list of the clauses that this clause is indexed in.

    @param intermediate_rep:    The intermediate representation, filled with information
                                about the source code in general, but not yet this node.

    @param loop_node:           The node who's information we are filling in with the clauses.

    @return:                    The new index. If there are no more
                                clauses after this one is done, index will be -1.

    """
    args = (index, clause_list, intermediate_rep, loop_node)
    clause = clause_list[index]
    if   clause.startswith("loop"):
        return _loop(*args)
    elif clause.startswith("device_type"):
        return _device_type(*args)
    elif clause.startswith("copy"):
        return _copy(*args)
    elif clause.startswith("copyin"):
        return _copyin(*args)
    elif clause.startswith("copyout"):
        return _copyout(*args)
    elif clause.startswith("create"):
        return _create(*args)
    elif clause.startswith("no_create"):
        return _no_create(*args)
    elif clause.startswith("present"):
        return _present(*args)
    elif clause.startswith("deviceptr"):
        return _deviceptr(*args)
    elif clause.startswith("attach"):
        return _attach(*args)
    else:
        return commonclauses.apply_clause(*args)

def _loop(index, clause_list, intermediate_rep, parallel_node):
    """
    A parallel construct can be combined with a loop construct by
    the following:

    `#pragma acc prallel loop etc`

    When this is done, it insinuates that the parallel region
    is comprised of a single loop immediately following the pragma.
    So add a loop node to the parallel node and finish parsing
    as if we were parsing a loop node.

    Once we return from this function, the parallel node will get
    added to the IR tree, along with its child.
    """
    loop_node = loop.LoopNode(parallel_node.lineno)
    while index != -1:
        index = loop._apply_clause(index + 1, clause_list, intermediate_rep, loop_node)
    parallel_node.add_child(loop_node)
    return index  # should be -1

def _device_type(index, clause_list, intermediate_rep, parallel_node):
    """
    """
    return -1

def _copy(index, clause_list, intermediate_rep, parallel_node):
    """
    """
    return -1

def _copyin(index, clause_list, intermediate_rep, parallel_node):
    """
    """
    return -1

def _copyout(index, clause_list, intermediate_rep, parallel_node):
    """
    """
    return -1

def _create(index, clause_list, intermediate_rep, parallel_node):
    """
    """
    return -1

def _no_create(index, clause_list, intermediate_rep, parallel_node):
    """
    """
    return -1

def _present(index, clause_list, intermediate_rep, parallel_node):
    """
    """
    return -1

def _deviceptr(index, clause_list, intermediate_rep, parallel_node):
    """
    """
    return -1

def _attach(index, clause_list, intermediate_rep, parallel_node):
    """
    """
    return -1
