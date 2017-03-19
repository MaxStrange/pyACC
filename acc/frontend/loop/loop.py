"""
Module for the loop directive.

Provides one API function: loop
"""
from acc.ir.intrep import Code
from acc.frontend.loop.visitor import loop_visitor
from acc.frontend.util.errors import InvalidClauseError
import acc.frontend.util.util as util
import ast
import asttokens

def loop(clauses, meta_data, back_end, code_object, *args, **kwargs):
    """
    From the docs:
    The loop construct can describe what type of parallelism to use to
    execute the loop and declare private variables and arrays and reduction
    operations.

    Allowable clauses are:
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

        Where gang-arg is one of:
        - [num:]int-expr
        - static:size-expr
        and gang-arg-list may have at most one num and one static argument,
        and where size-expr is one of:
        - *
        - int-expr

    Restrictions:
    - Only the collapse, gang, worker, vector, seq, auto and tile clauses may
      follow a device_type clause.
    - The int-expr argument to the worker and vector clauses must be
      invariant in the kernels region.
    - A loop associated with a loop construct that does not have a seq
      clause must be written such that the loop iteration count is
      computable when entering the loop construct.
    """
    index = 0
    while index != -1:
        index, code_object = _apply_clause(index,
                                           clauses,
                                           code_object,
                                           meta_data,
                                           back_end)

    # TODO: This is proof of concept stuff

    atok = asttokens.ASTTokens(code_object.src, parse=True)
    tree = atok.tree
    v = loop_visitor(atok)
    v.visit(tree)

    meta_data.region_source = v.loop_code
    meta_data.region_vars = set(v.loop_vars)
    frame = meta_data.stackframe[0] # In 3.5, this can be stackframe.frame
    func_names = util.get_function_names_from_source(code_object.src,
            meta_data.funcs_name)

    meta_data.callers_mods = util.get_modules_from_stackframe(frame)
    meta_data.callers_funcs = util.get_functions_from_stackframe(frame, func_names)
    meta_data.funcs_funcs = util.get_functions_from_module(meta_data.funcs_module,
            func_names)
    meta_data.funcs_mods = util.get_modules_from_module(meta_data.funcs_module)

    funcs = meta_data.funcs_funcs + meta_data.callers_funcs
    module_vars = meta_data.funcs_mods + meta_data.callers_mods

    new_source = back_end.for_loop(code_object, meta_data)
    return Code(new_source)


def _apply_clause(index, clause_list, code_object, meta_data, back_end):
    """
    Consumes however much of the clause list as necessary to apply the clause
    found at index in the clause_list.

    @param index:       The index into the clause_list of the clause we are
                        interested int.

    @param clause_list: The list of the clauses that this clause is indexed in.

    @return:            The new index and new Code. If there are no more
                        clauses after this one is done, index will be -1.
    """
    args = (index, clause_list, code_object, meta_data, back_end)
    clause = clause_list[index]
    print("clause:", clause)
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
        raise InvalidClauseError("Clause either not allowed for this " +\
                "directive, or else it may be spelled " +\
                "incorrectly. Clause given: " + clause)
#TODO do this crap
def _collapse(index, clause_list, code_object, meta_data, back_end):
    """
    The 'collapse' clause is used to specify how many tightly nested loops
    are associated with the 'loop' construct. The argument to the 'collapse'
    clause must be a constant positive integer expression. If no 'collapse'
    clause is present, only the immediately following loop is associated
    with the 'loop' construct.

    If more than one loop is associated with the 'loop' construct, the
    iterations of all the associated loops are all scheduled according
    to the rest of the clauses. The trip count for all loops associated
    with the 'collapse' clause must be computable and invariant in all
    the loops.

    It is implementation-defined whether a 'gang', 'worker' or 'vector'
    clause on the construct is applied ot each loop, or to the
    linearized iteration space.
    """
    #TODO: This one's easy enough: just make sure that the number of iterations
    #      on each of the loops is invariant and countable and then set in the
    #      code_object a value to tell it which loops are talked about by the
    #      rest of the clauses.

    # for node in tree:
    #   if node is not a loop:
    #       break
    #   elif not loop is invariant and countable:
    #       break
    #   else:
    #       num_loops += 1
    # if num_loops != n:
    #   raise some sort of error that explains how many and which loops were
    #   found, and that you want n loops collapsed, but we could only
    #   guarantee num_loops
    #
    # code_object.num_loops = num_loops

    class _visitor(ast.NodeVisitor):
        def __init__(self, atok):
            self.atok = atok
            self._seen = set()

        def generic_visit(self, node):
            type_name = type(node).__name__

            if type_name == "comprehension":
                # TODO
                pass
            elif type_name == "For":
                # TODO
                pass
            ast.NodeVisitor.generic_visit(self, node)

    atok = asttokens.ASTTokens(code_object.src, parse=True)
    tree = atok.tree
    v = _visitor(atok)
    v.visit(tree)
    print("Done; exiting")
    exit()

    return -1, code_object

def _gang(index, clause_list, code_object, meta_data, back_end):
    """
    When the parent compute construct is a 'parallel' construct, or on an
    orphaned 'loop' construct, the 'gang' clause specifies that the
    iterations of the associated loop or loops are to be exectued in
    parallel by distributing the iterations among the gangs created by
    the 'parallel' construct. A 'loop' construct with the 'gang' clause
    transitions a compute region from gang-reductant mode to gang-partitioned
    mode. The number of gangs is controlled by the 'parallel' construct;
    only the 'static' argument is allowed. The loop iterations must be data
    independent, except for variables specified in a 'reduction' clause.
    The region of a loop with the 'gang' clause may not contain another
    loop with the 'gang' clause unless within a nested compute region.

    When the parent compute construct is a 'kernels' construct, the 'gang'
    clause specifies that the iterations of the associated loop or loops
    are to be executed in parallel across the gangs. loops. [sic]
    An argument with no keyword or with the 'num' keyword is allowed only
    when the 'num_gangs' does not appear on the 'kernels' construct.
    If an argument with no keyword or an argument after the 'num'
    keyword is specified, it specifies how many gangs to use to execute
    the iterations of this loop. The region of a loop with the 'gang'
    clause may not contain another loop with a 'gang' clause unless within
    a nested compute region.

    The scheduling of loop iterations to gangs is not specified unless
    the 'static' argument appears as an argument. If the 'static' argument
    appears with an integer expression, that expression is used as a chunk
    size. If the static argument appears with an asterisk, the
    implementation will select a chunk size. The iterations are divided
    into chunks of the selected chunk size, and the chunks are assigned to
    gangs starting with gang zero and continuing in round-robin fashion.
    Two 'gang' loops in the same parallel region with the same number of
    iterations, and with 'static' clauses with the same argument, will
    assign the iterations to gangs in the same manner. Two 'gang' loops in
    the same kernels region with the same number of iterations, the same
    number of gangs to use, and with 'static' clauses with the same argument,
    will assign the iterations to gangs in the same manner.
    """
    return -1, code_object

def _worker(index, clause_list, code_object, meta_data, back_end):
    """
    When the parent compute construct is a 'parallel' construct, or on an
    orphaned 'loop' construct, the 'worker' clause specifies that the
    iterations of the associated loop or loops are to be executed in parallel
    by distributing the iterations among the multiple workers within a
    single gang. A 'loop' construct with a 'worker' clause first activates
    additional worker-level parallelism and then distributes the loop
    iterations across those workers. No argument is allowed. The loop
    iterations must be data independent, except for variables specified
    in a 'reduction' clause. The region of a loop with the 'worker' clause
    may not contain a loop with the 'gang' or 'worker' clause unless within
    a nested compute region.

    When the parent compute construct is a 'kernels' construct, the 'worker'
    clause specifies that the iterations of the associated loop or loops
    are to be executed in parallel across the workers within a gang. An
    argument is allowed only when the 'num_workers' does not appear on
    the 'kernels' construct. The optional argument specifies how many
    workers per gang to use to execute the iterations of this loop. The
    region of a loop with the 'worker' clause may not contain a loop with
    a 'gang' or 'worker' clause unless within a nested compute region.

    All workers will complete execution of their assigned iterations before
    any worker proceeds beyond the end of the loop.
    """
    return -1, code_object

def _vector(index, clause_list, code_object, meta_data, back_end):
    """
    When the parent compute construct is a 'parallel' construct, or on an
    orphaned 'loop' construct, the 'vector' clause specifies that the
    iterations of the associated loop or loops are to be executed in
    vector or SIMD mode. A 'loop' construct with a 'vector' clause causes
    a worker to transition from vector-single mode to vector-partitioned mode.
    Similar to the 'worker' clause, the 'vector' clause first activates
    additional vector-level parallelism and then distributes the loop
    iterations across those vector lanes. The operations will execute using
    vectors of the length specified or chosen for the parallel region. The
    region of a loop with a 'vector' clause may not contain a loop with
    the 'gang', 'worker' or 'vector' clause unless within a nested compute
    region.

    When the parent compute construct is a 'kernels' construct, the 'vector'
    clause specifies that the iterations of the associated loop or loops
    are to be executed with vector or SIMD processing. An argument is
    allowed only when the 'vector_length' does not appear on the 'kernels'
    construct. If an argument is specified, the implementation will choose
    an appropriate vector length. The region of a loop with the 'vector'
    clause may not contain a loop with a 'gang', 'worker' or 'vector'
    clause unless within a nested compute region.

    All vector lanes will complete execution of their assigned iterations
    before any vector lane proceeds beyond the end of the loop.
    """
    return -1, code_object

def _seq(index, clause_list, code_object, meta_data, back_end):
    """
    The 'seq' clause specifies that the associated loop or loops are to be
    executed sequentially by the acclerator. This clause will override any
    automatic parallelization or vectorization.
    """
    return -1, code_object

def _auto(index, clause_list, code_object, meta_data, back_end):
    """
    The 'auto' clause specifies that the implementation must analyze the
    loop and determine whether to run the loop sequentially. The
    implementation may be restricted to the types of parallelism it can
    apply by the presence of 'loop' constructs with 'gang', 'worker' or
    'vector' clauses for outer or inner loops. When the parent compute
    construct is a 'kernels' construct, a 'loop' construct with no
    'independent' or 'seq' clause is treated as if it has the 'auto' clause.
    """
    return -1, code_object

def _tile(index, clause_list, code_object, meta_data, back_end):
    """
    The 'tile' clause specifies that the implementation should split each
    loop nest into two loops, with an outer set of tile loops and an
    inner set of element loops. The argument to the 'tile' clause is a list
    of one or more tile sizes, where each tile size is a constant positive
    integer expression or an asterisk. If there are n tile sizes in the list,
    the 'loop' construct must be immediately followed by n tightly-nested
    loops. The first argument in the size-expr-list corresponds to the
    innermost loop of the n associated loops, and the last element
    corresponds to the outermost associated loop. If the tile size is specified
    with an asterisk, the implementation will choose an appropriate value.
    Each loop in the nest will be split or strip-mined into two loops, an
    outer tile loop and an inner elment loop. The trip count of the element
    loop will be limited to the corresponding tile size from the
    size-expr-list. The tile loops will be reordered to be outside all the
    element loops, and the element loops will all be inside the tile loops.

    If the 'vector' clause appears on the 'loop' construct, the 'vector' clause
    is applied to the element loops. If the 'gang' clause appears on the 'loop'
    construct, the 'gang' clause is applied ot the tile loops. If the 'worker'
    clause appears on the 'loop' construct, the 'worker' clause is applied
    to the element loops if no 'vector' clause appears, and to the tile
    loops otherwise.
    """
    return -1, code_object

def _device_type(index, clause_list, code_object, meta_data, back_end):
    """
    The 'device_type' clause is described in Section 2.4 Device-Specific
    Clauses.
    """
    return -1, code_object

def _independent(index, clause_list, code_object, meta_data, back_end):
    """
    The 'independent' clause tells the implementation that the iterations of
    this loop are data-independent with respect to each other. This allows
    the implementation to generate code to execute the iterations in parallel
    with no synchronization. When the parent compute construct is a
    'parallel' construct, the 'independent' clause is implied on all 'loop'
    constructs without a 'seq' or 'auto' clause.

    Note:
        - It is likely a programming error to use the 'independent' clause
          on a loop if any iteration writes to a variable or array element
          that any other iteration also writes or reads, except for
          variables in a 'reduction' clause or accesses in atomic regions.
    """
    return -1, code_object

def _private(index, clause_list, code_object, meta_data, back_end):
    """
    The 'private' clause on a 'loop' construct specifies that a copy of each
    item in var-list will be created. If the body of the loop is executed
    in vector-partitioned mode, a copy of the item is created for each
    thread associated with each vector lane. If the body of the loop is
    executed in worker-partitioned vector-single mode, a copy of the item is
    created for and shared across the set of threads associated with all the
    vector lanes of each worker. Otherwise, a copy of the item is created
    for and shared across the set of threads associated with all the vector
    lanes of all the workers of each gang.
    """
    return -1, code_object

def _reduction(index, clause_list, code_object, meta_data, back_end):
    """
    The 'reduction' clause specifies a reduction operator and one or more
    scalar variables. For each reduction variable, a private copy is created
    in the same manner as for a 'private' clause on the 'loop' construct,
    and initialized for that operator; see the table in Section 2.5.11
    reduction clause. At the end of the loop, the values for each thread
    are combined using the specified reduction operator, and the result
    combined with the value of the original variable and stored in the
    original variable at the end of the parallel or kernels region if the loop
    has gang parallelism, and at the end of the loop otherwise.

    In a parallel region, if the 'reduction' clause is used on a loop with
    the 'vector' or 'worker' clauses (and no 'gang' clause), and the scalar
    variable also appears in a 'private' clause on the 'parallel' construct,
    the value of the private copy of the scalar will be updated at the exit
    of the loop. If the scalar variable does not appear in a 'private' clause
    on the 'parallel' construct, or if the 'reduction' clause is used on
    a loop with the 'gang' clause, the value of the scalar will not be
    updated until the end of the parallel region.

    Restrictions
        - The 'reduction' clause may not be specified on an orphaned 'loop'
          construct with the 'gang' clause, or on an orphaned 'loop' construct
          that will generate gang parallelism in a procedure that is compiled
          with the 'routine gang' clause.
        - The restrictions for a 'reduction' clause on a compute construct
          listed in in Section 2.5.11 reduction clause also apply to a
          'reduction' clause on a loop construct.
    """
    return -1, code_object
