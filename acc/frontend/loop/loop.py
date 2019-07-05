"""
Module for the loop directive.

Provides one API function: loop
"""
from acc.ir.intrep import IntermediateRepresentation, IrNode
from acc.frontend.util.errors import InvalidClauseError
from acc.frontend.loop.loopvisitors import collapse
import acc.frontend.util.util as util
import ast
import asttokens

class LoopNode(IrNode):
    """
    Node for the IntermediateRepresentation tree that is used for loop constructs.
    """
    def __init__(self, lineno: int):
        super().__init__(lineno)
        self.collapse = None
        self.gang = None
        self.worker = None
        self.vector = None
        self.seq = None
        self.auto = None
        self.tile = None
        self.device_type = None
        self.independent = None
        self.private = None
        self.reduction = None

def loop(clauses, intermediate_rep, lineno, *args, **kwargs):
    """
    From the OpenACC 2.7 standard:

    Summary
    -------
    The OpenACC loop construct applies to a loop which must immediately follow this
    directive. The loop construct can describe what type of parallelism to use to execute the loop and
    declare private vars and reduction operations.

    Syntax
    ------
    The syntax of the loop construct is

    #pragma acc loop [clause-list] new-line
    for loop

    where clause is one of the following:

    - collapse( n )
    - gang [( gang-arg-list )]
    - worker [( [num:]int-expr )]
    - vector [( [length:]int-expr )]
    - seq
    - auto
    - tile( size-expr-list )
    - device_type( device-type-list )
    - independent
    - private( var-list )
    - reduction( operator:var-list )

    where gang-arg is one of:
    - [num:]int-expr
    - static:size-expr
    and gang-arg-list may have at most one num and one static argument,

    and where size-expr is one of:
    - *
    - int-expr

    Some clauses are only valid in the context of a kernels construct; see the descriptions below.
    An orphaned loop construct is a loop construct that is not lexically enclosed within a compute
    construct. The parent compute construct of a loop construct is the nearest compute construct that
    lexically contains the loop construct.

    Restrictions
    ------------
    • Only the collapse, gang, worker, vector, seq, auto, and tile clauses may follow
    a device_type clause.
    • The int-expr argument to the worker and vector clauses must be invariant in the kernels
    region.
    • A loop associated with a loop construct that does not have a seq clause must be written
    such that the loop iteration count is computable when entering the loop construct.
    """
    loop_node = LoopNode(lineno)
    index = 0
    while index != -1:
        index = _apply_clause(index, clauses, intermediate_rep, loop_node)
    intermediate_rep.add_child(loop_node)

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
    if   clause.startswith("collapse"):
        return _collapse(*args)
    elif clause.startswith("gang"):
        return _gang(*args)
    elif clause.startswith("worker"):
        return _worker(*args)
    elif clause.startswith("vector"):
        return _vector(*args)
    elif clause.startswith("seq"):
        return _seq(*args)
    elif clause.startswith("auto"):
        return _auto(*args)
    elif clause.startswith("tile"):
        return _tile(*args)
    elif clause.startswith("device_type"):
        return _device_type(*args)
    elif clause.startswith("independent"):
        return _independent(*args)
    elif clause.startswith("private"):
        return _private(*args)
    elif clause.startswith("reduction"):
        return _reduction(*args)
    else:
        errmsg = "Clause either not allowed for this directive, or else it may be spelled incorrectly. Clause given: {} at line: {}".format(clause, loop_node.lineno)
        raise InvalidClauseError(errmsg)

def _collapse(index, clause_list, intermediate_rep, loop_node):
    """
    The collapse clause is used to specify how many tightly nested loops are associated with the
    loop construct. The argument to the collapse clause must be a constant positive integer expression.
    If no collapse clause appears, only the immediately following loop is associated with the
    loop construct.

    If more than one loop is associated with the loop construct, the iterations of all the associated loops
    are all scheduled according to the rest of the clauses. The trip count for all loops associated with the
    collapse clause must be computable and invariant in all the loops.
    It is implementation-defined whether a gang, worker or vector clause on the construct is
    applied to each loop, or to the linearized iteration space.
    """
    #TODO: This one's easy enough: just make sure that the number of iterations
    #      on each of the loops is invariant and countable and then set in the
    #      intermediate_value a value to tell it which loops are talked about by the
    #      rest of the clauses.

    atok = asttokens.ASTTokens(intermediate_rep.src, parse=True)
    v = collapse.CollapseVisitor(atok)
    tree = atok.tree
    v.visit(tree)

    #intermediate_rep.meta_data.region_source = v.loop_code
    #intermediate_rep.meta_data.region_vars = set(v.loop_vars)
    #frame = intermediate_rep.meta_data.stackframe[0] # In 3.5, this can be stackframe.frame
    #func_names = util.get_function_names_from_source(intermediate_rep.src, intermediate_rep.meta_data.funcs_name)

    #intermediate_rep.meta_data.callers_mods = util.get_modules_from_stackframe(frame)
    #intermediate_rep.meta_data.callers_funcs = util.get_functions_from_stackframe(frame, func_names)
    #intermediate_rep.meta_data.funcs_funcs = util.get_functions_from_module(intermediate_rep.meta_data.funcs_module, func_names)
    #intermediate_rep.meta_data.funcs_mods = util.get_modules_from_module(intermediate_rep.meta_data.funcs_module)

    #funcs = intermediate_rep.meta_data.funcs_funcs + intermediate_rep.meta_data.callers_funcs
    #module_vars = intermediate_rep.meta_data.funcs_mods + intermediate_rep.meta_data.callers_mods

    return -1

def _gang(index, clause_list, intermediate_rep, loop_node):
    """
    When the parent compute construct is a parallel construct, or on an orphaned loop construct,
    the gang clause specifies that the iterations of the associated loop or loops are to be executed in
    parallel by distributing the iterations among the gangs created by the parallel construct. A
    loop construct with the gang clause transitions a compute region from gang-redundant mode
    to gang-partitioned mode. The number of gangs is controlled by the parallel construct; only
    the static argument is allowed. The loop iterations must be data independent, except for vars
    specified in a reduction clause. The region of a loop with the gang clause may not contain
    another loop with the gang clause unless within a nested compute region.

    When the parent compute construct is a kernels construct, the gang clause specifies that the
    iterations of the associated loop or loops are to be executed in parallel across the gangs. An argument
    with no keyword or with the num keyword is allowed only when the num_gangs does not appear
    on the kernels construct. If an argument with no keyword or an argument after the num keyword
    is specified, it specifies how many gangs to use to execute the iterations of this loop. The region of a
    loop with the gang clause may not contain another loop with a gang clause unless within a nested
    compute region.

    The scheduling of loop iterations to gangs is not specified unless the static argument appears as
    an argument. If the static argument appears with an integer expression, that expression is used
    as a chunk size. If the static argument appears with an asterisk, the implementation will select a
    chunk size. The iterations are divided into chunks of the selected chunk size, and the chunks are
    assigned to gangs starting with gang zero and continuing in round-robin fashion. Two gang loops
    in the same parallel region with the same number of iterations, and with static clauses with the
    same argument, will assign the iterations to gangs in the same manner. Two gang loops in the
    same kernels region with the same number of iterations, the same number of gangs to use, and with
    static clauses with the same argument, will assign the iterations to gangs in the same manner.
    """
    return -1

def _worker(index, clause_list, intermediate_rep, loop_node):
    """
    When the parent compute construct is a parallel construct, or on an orphaned loop construct,
    the worker clause specifies that the iterations of the associated loop or loops are to be executed
    in parallel by distributing the iterations among the multiple workers within a single gang. A loop
    construct with a worker clause causes a gang to transition from worker-single mode to worker
    partitioned mode. In contrast to the gang clause, the worker clause first activates additional
    worker-level parallelism and then distributes the loop iterations across those workers. No argument
    is allowed. The loop iterations must be data independent, except for vars specified in a reduction
    clause. The region of a loop with the worker clause may not contain a loop with the gang or
    worker clause unless within a nested compute region.

    When the parent compute construct is a kernels construct, the worker clause specifies that the
    iterations of the associated loop or loops are to be executed in parallel across the workers within
    a single gang. An argument is allowed only when the num_workers does not appear on the
    kernels construct. The optional argument specifies how many workers per gang to use to execute
    the iterations of this loop. The region of a loop with the worker clause may not contain a loop
    with a gang or worker clause unless within a nested compute region.
    All workers will complete execution of their assigned iterations before any worker proceeds beyond
    the end of the loop.
    """
    return -1

def _vector(index, clause_list, intermediate_rep, loop_node):
    """
    When the parent compute construct is a parallel construct, or on an orphaned loop construct,
    the vector clause specifies that the iterations of the associated loop or loops are to be executed in
    vector or SIMD mode. A loop construct with a vector clause causes a worker to transition from
    vector-single mode to vector-partitioned mode. Similar to the worker clause, the vector clause
    first activates additional vector-level parallelism and then distributes the loop iterations across those
    vector lanes. The operations will execute using vectors of the length specified or chosen for the
    parallel region. The region of a loop with the vector clause may not contain a loop with the
    gang, worker, or vector clause unless within a nested compute region.

    When the parent compute construct is a kernels construct, the vector clause specifies that the
    iterations of the associated loop or loops are to be executed with vector or SIMD processing. An
    argument is allowed only when the vector_length does not appear on the kernels construct.
    If an argument is specified, the iterations will be processed in vector strips of that length; if no
    argument is specified, the implementation will choose an appropriate vector length. The region of
    a loop with the vector clause may not contain a loop with a gang, worker, or vector clause
    unless within a nested compute region.

    All vector lanes will complete execution of their assigned iterations before any vector lane proceeds
    beyond the end of the loop.
    """
    return -1

def _seq(index, clause_list, intermediate_rep, loop_node):
    """
    The seq clause specifies that the associated loop or loops are to be executed sequentially by the
    accelerator. This clause will override any automatic parallelization or vectorization.
    """
    return -1

def _auto(index, clause_list, intermediate_rep, loop_node):
    """
    The auto clause specifies that the implementation must analyze the loop and determine whether
    the loop iterations are data independent and, if so, select whether to apply parallelism to this loop
    or whether to run the loop sequentially. The implementation may be restricted to the types of
    parallelism it can apply by the presence of loop constructs with gang, worker. or vector
    clauses for outer or inner loops. When the parent compute construct is a kernels construct, a
    loop construct with no independent or seq clause is treated as if it has the auto clause.
    """
    return -1

def _tile(index, clause_list, intermediate_rep, loop_node):
    """
    The tile clause specifies that the implementation should split each loop in the loop nest into two
    loops, with an outer set of tile loops and an inner set of element loops. The argument to the tile
    clause is a list of one or more tile sizes, where each tile size is a constant positive integer expression
    or an asterisk. If there are n tile sizes in the list, the loop construct must be immediately followed
    by n tightly-nested loops. The first argument in the size-expr-list corresponds to the innermost loop
    of the n associated loops, and the last element corresponds to the outermost associated loop. If the
    tile size is specified with an asterisk, the implementation will choose an appropriate value. Each
    loop in the nest will be split or strip-mined into two loops, an outer tile loop and an inner element
    loop. The trip count of the element loop will be limited to the corresponding tile size from the
    size-expr-list. The tile loops will be reordered to be outside all the element loops, and the element
    loops will all be inside the tile loops.

    If the vector clause appears on the loop construct, the vector clause is applied to the element
    loops. If the gang clause appears on the loop construct, the gang clause is applied to the tile
    loops. If the worker clause appears on the loop construct, the worker clause is applied to the
    element loops if no vector clause appears, and to the tile loops otherwise.
    """
    return -1

def _device_type(index, clause_list, intermediate_rep, loop_node):
    """
    The 'device_type' clause is described in Section 2.4 Device-Specific
    Clauses.
    """
    return -1

def _independent(index, clause_list, intermediate_rep, loop_node):
    """
    The independent clause tells the implementation that the iterations of this loop are data-independent
    with respect to each other. This allows the implementation to generate code to execute the iterations
    in parallel with no synchronization. When the parent compute construct is a parallel construct,
    the independent clause is implied on all loop constructs without a seq or auto clause.

    Note
    ----
    • It is likely a programming error to use the independent clause on a loop if any iteration
    writes to a variable or array element that any other iteration also writes or reads, except for
    vars in a reduction clause or accesses in atomic regions.
    """
    return -1

def _private(index, clause_list, intermediate_rep, loop_node):
    """
    The private clause on a loop construct specifies that a copy of each item in var-list will be
    created. If the body of the loop is executed in vector-partitioned mode, a copy of the item is created
    for each thread associated with each vector lane. If the body of the loop is executed in worker
    partitioned vector-single mode, a copy of the item is created for and shared across the set of threads
    associated with all the vector lanes of each worker. Otherwise, a copy of the item is created for and
    shared across the set of threads associated with all the vector lanes of all the workers of each gang.
    """
    return -1

def _reduction(index, clause_list, intermediate_rep, loop_node):
    """
    The reduction clause specifies a reduction operator and one or more vars. For each reduction
    var, a private copy is created in the same manner as for a private clause on the loop construct,
    and initialized for that operator; see the table in Section 2.5.13 reduction clause. At the end of the
    loop, the values for each thread are combined using the specified reduction operator, and the result
    combined with the value of the original var and stored in the original var at the end of the parallel
    or kernels region if the loop has gang parallelism, and at the end of the loop otherwise. If the
    reduction var is an array or subarray, the reduction operation is logically equivalent to applying that
    reduction operation to each array element of the array or subarray individually. If the reduction var
    is a composite variable, the reduction operation is logically equivalent to applying that reduction
    operation to each member of the composite variable individually.

    In a parallel region, if the reduction clause is used on a loop with the vector or worker
    clauses (and no gang clause), and the reduction var is private, the value of the private reduction
    var will be updated at the exit of the loop. If the reduction var is not private in the parallel region,
    or if the reduction clause is used on a loop with the gang clause, the value of the reduction var
    will not be updated until the end of the parallel region.

    If a variable is involved in a reduction that spans multiple nested loops where two or more of those
    loops have associated loop directives, a reduction clause containing that variable must appear
    on each of those loop directives.

    Restrictions
    ------------
    • A var in a reduction clause must be a scalar variable name, a composite variable name,
    an array name, an array element, or a subarray (refer to Section 2.7.1).
    • Reduction clauses on nested constructs for the same reduction var must have the same reduction operator.
    • The reduction clause may not appear on an orphaned loop construct with the gang
    clause, or on an orphaned loop construct that will generate gang parallelism in a procedure
    that is compiled with the routine gang clause.
    • The restrictions for a reduction clause on a compute construct listed in in Section 2.5.13
    reduction clause also apply to a reduction clause on a loop construct.
    • See Section 2.17 Fortran Optional Arguments for discussion of Fortran optional arguments in
    reduction clauses.
    """
    return -1
