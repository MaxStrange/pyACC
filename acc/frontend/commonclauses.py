"""
This module contains all the clauses common to several constructs.
"""
import acc.frontend.util.errors as errors

def apply_clause(index, clause_list, intermediate_rep, node, dbg):
    """
    Consumes however much of the clause list as necessary to apply the clause
    found at index in the clause_list.

    @param index:               The index into the clause_list of the clause we are
                                interested in.

    @param clause_list:         The list of the clauses that this clause is indexed in.

    @param intermediate_rep:    The intermediate representation, filled with information
                                about the source code in general, but not yet this node.

    @param node:                The node who's information we are filling in with the clauses.

    @return:                    The new index. If there are no more
                                clauses after this one is done, index will be -1.

    """
    args = (index, clause_list, intermediate_rep, node, dbg)
    clause = clause_list[index]
    if   clause.startswith("async"):
        return _async(*args)
    elif clause.startswith("wait"):
        return _wait(*args)
    elif clause.startswith("num_gangs"):
        return _num_gangs(*args)
    elif clause.startswith("num_workers"):
        return _num_workers(*args)
    elif clause.startswith("vector_length"):
        return _vector_length(*args)
    elif clause.startswith("private"):
        return _private(*args)
    elif clause.startswith("firstprivate"):
        return _firstprivate(*args)
    elif clause.startswith("reduction"):
        return _reduction(*args)
    elif clause.startswith("default"):
        return _default(*args)
    elif clause.startswith("if"):
        return _if(*args)
    elif clause.startswith("self"):
        return _self(*args)
    else:
        errmsg = "Clause either not allowed for this directive, or else it may be spelled incorrectly. Clause given: {}.".format(clause)
        raise errors.InvalidClauseError(dbg.build_message(errmsg))

def _async(index, clause_list, intermediate_rep, node, dbg):
    """
    The async clause is optional; see Section 2.16 Asynchronous Behavior for more information
    """
    return -1

def _wait(index, clause_list, intermediate_rep, node, dbg):
    """
    The wait clause is optional; see Section 2.16 Asynchronous Behavior for more information.
    """
    return -1

def _num_gangs(index, clause_list, intermediate_rep, node, dbg):
    """
    The num_gangs clause is allowed on the parallel and kernels constructs.

    The value of the integer expression defines the number of parallel gangs that will execute the parallel region,
    or that will execute each kernel created for the kernels region. If the clause is not specified, an
    implementation-defined default will be used; the default may depend on the code within the
    construct. The implementation may use a lower value than specified based on limitations imposed by
    the target architecture.
    """
    return -1

def _num_workers(index, clause_list, intermediate_rep, node, dbg):
    """
    The num_workers clause is allowed on the parallel and kernels constructs.

    The value of the integer expression defines the number of workers within each gang that will be active
    after a gang transitions from worker-single mode to worker-partitioned mode. If the clause is not
    specified, an implementation-defined default will be used; the default value may be 1, and may be
    different for each parallel construct or for each kernel created for a kernels construct. The
    implementation may use a different value than specified based on limitations imposed by the target
    architecture.
    """
    return -1

def _vector_length(index, clause_list, intermediate_rep, node, dbg):
    """
    The vector_length clause is allowed on the parallel and kernels constructs.

    The value of the integer expression defines the number of vector lanes that will be active after a worker
    transitions from vector-single mode to vector-partitioned mode. This clause determines the vector length
    to use for vector or SIMD operations. If the clause is not specified, an implementation-defined
    default will be used. This vector length will be used for loop constructs annotated with the vector
    clause, as well as loops automatically vectorized by the compiler. The implementation may use a
    different value than specified based on limitations imposed by the target architecture.
    """
    return -1

def _private(index, clause_list, intermediate_rep, node, dbg):
    """
    The private clause is allowed on the parallel and serial constructs.

    It declares that a copy of each item on the list will be created for each gang.
    """
    return -1

def _firstprivate(index, clause_list, intermediate_rep, node, dbg):
    """
    The firstprivate clause is allowed on the parallel and serial constructs

    It declares that a copy of each item on the list will be created for each gang,
    and that the copy will be initialized with the value of that item on the local thread when a
    parallel or serial construct is encountered.
    """
    return -1

def _reduction(index, clause_list, intermediate_rep, node, dbg):
    """
    The reduction clause is allowed on the parallel and serial constructs.

    It specifies a reduction operator and one or more vars. It implies a copy data clause for each reduction var,
    unless a data clause for that variable appears on the compute construct. For each reduction var, a
    private copy is created for each parallel gang and initialized for that operator. At the end of the
    region, the values for each gang are combined using the reduction operator, and the result combined
    with the value of the original var and stored in the original var. If the reduction var is an array or
    subarray, the array reduction operation is logically equivalent to applying that reduction operation
    to each element of the array or subarray individually. If the reduction var is a composite variable,
    the reduction operation is logically equivalent to applying that reduction operation to each member
    of the composite variable individually. The reduction result is available after the region.

    The following table lists the operators that are valid and the initialization values; in each case, the
    initialization value will be cast into the data type of the var. For max and min reductions, the
    initialization values are the least representable value and the largest representable value for that data
    type, respectively. At a minimum, the supported data types include bool, int, float, and complex.

    However, for each reduction operator, the supported data types include only the types permitted as operands to
    the corresponding operator where (1) for max and min, the corresponding operator is less-than and (2) for
    other operators, the operands and the result are the same type.

    ----------------------------------------
    Operator            Initialization Value
    ----------------------------------------
    +                   0
    *                   1
    max                 least
    min                 largest
    &                   ~0
    |                   0
    ^                   0
    &&                  1
    ||                  0

    Restrictions
    ------------
    • A var in a reduction clause must be a scalar variable name, a composite variable name,
      an array name, an array element, or a subarray (refer to Section 2.7.1).
    • If the reduction var is an array element or a subarray, accessing the elements of the array
      outside the specified index range results in unspecified behavior.
    • The reduction var may not be a member of a composite variable.
    • If the reduction var is a composite variable, each member of the composite variable must be
      a supported datatype for the reduction operation.
    """
    return -1

def _default(index, clause_list, intermediate_rep, node, dbg):
    """
    The default clause is optional.

    The none argument tells the compiler to require that all variables
    used in the compute construct that do not have predetermined data attributes to explicitly appear
    in a data clause on the compute construct, a data construct that lexically contains the compute
    construct, or a visible declare directive. The present argument causes all arrays or composite
    variables used in the compute construct that have implicitly determined data attributes to be treated
    as if they appeared in a present clause.
    """
    return -1

def _if(index, clause_list, intermediate_rep, node, dbg):
    """
    The if clause is optional.

    When the condition in the if clause is truthy, the
    region will execute on the current device. When the condition in the if clause evaluates to False,
    the local thread will execute the region.
    """
    return -1

def _self(index, clause_list, intermediate_rep, node, dbg):
    """
    The self clause is optional.

    The self clause may have a single condition-argument. If the condition-argument is not present
    it is assumed to be True. When both an if clause and a
    self clause appear and the condition in the if clause evaluates to False
    the self clause has no effect.

    When the condition is truthy, the region will execute
    on the local device. When the condition in the self clause evaluates to False,
    the region will execute on the current device.
    """
    return -1
