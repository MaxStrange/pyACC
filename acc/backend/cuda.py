"""
This is the CUDA back end.
"""
import acc.frontend.loop.loop as loop
import acc.frontend.parallel.parallel as parallel
import acc.backend.common as common

def compile(intermediate_rep):
    """
    """
    modified_src = intermediate_rep.src
    for node in intermediate_rep.breadth_first_traversal():
        modified_src = _apply_node(modified_src, node, intermediate_rep)
    return modified_src

def _apply_node(modified_src, node, intermediate_rep):
    """
    """
    args = (modified_src, node, intermediate_rep)

    if   type(node) == parallel.ParallelNode:
        modified_src = _apply_parallel_node(*args)
    elif type(node) == loop.LoopNode:
        modified_src = _apply_loop_node(*args)
    else:
        # TODO
        raise NotImplementedError("Please implement this type of node in the back end.")
    return modified_src

def _apply_parallel_node(modified_src, node, intermediate_rep):
    """
    Parallel
    --------

    1. When the program encounters a parallel region, it must launch n gangs of
       m workers, each operating in v-lane vector (SIMD) mode.
    2. Each gang begins executing the parallel region in gang-redundant mode,
       meaning that one worker in each gang will execute the parallel region
       up until a `loop` region is encountered.
    3. If there is no `async` clause, there is an implicit barrier across gangs
       at the end of the parallel region, so that the local thread may not continue
       executing until all gangs have finished the region.

    TODO: Figure out:
    If there is no default(none) clause on the construct, the compiler will implicitly determine data
    attributes for variables that are referenced in the compute construct that do not have predetermined
    data attributes and do not appear in a data clause on the compute construct, a lexically containing
    data construct, or a visible declare directive.

    If there is no default(present) clause on the construct, an array or composite variable referenced
    in the parallel construct that does not appear in a data clause for the construct
    or any enclosing data construct will be treated as if it appeared in a copy clause for the parallel construct.

    If there is a default(present) clause on the construct, the compiler will implicitly treat all arrays
    and composite variables without predetermined data attributes as if they appeared in a present clause.
    A scalar variable referenced in the parallel construct that does not appear in a data clause
    for the construct or any enclosing data construct will be treated as if it appeared in a firstprivate clause.
    """
    return modified_src

def _apply_loop_node(modified_src, node, intermediate_rep):
    """
    """
    return modified_src
