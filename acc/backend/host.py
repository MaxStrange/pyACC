"""
This is the back end's API for the default back end (the host multiprocessing back end).
The back end is responsible for taking the OpenACC-compliant information
from the front end and actually parallelizing the given code.

A back end MUST provide a `compile` function that takes an IR and returns
valid Python source code as a str. The source will be imported as a Python
module and run in place of the @acc-decorated function.
"""
import acc.frontend.loop.loop as loop
import acc.frontend.parallel.parallel as parallel
import acc.backend.common as common
import os
# Just needed for type hints
import acc.ir.intrep as intrep

def compile(intermediate_rep: intrep.IntermediateRepresentation) -> str:
    """
    Compiles the given intermediate representation into a source code string
    ready to be built into a Python module and imported.
    """
    modified_src = common.CompilerTarget(intermediate_rep)
    for node in intermediate_rep.breadth_first_traversal():
        # Updates modified_src in place
        _apply_node(modified_src, node, intermediate_rep)
    return modified_src.build()

def _apply_node(modified_src: common.CompilerTarget, node: intrep.IrNode, intermediate_rep: intrep.IntermediateRepresentation):
    """
    """
    args = (modified_src, node, intermediate_rep)

    if   type(node) == parallel.ParallelNode:
        _apply_parallel_node(*args)
    elif type(node) == loop.LoopNode:
        _apply_loop_node(*args)
    else:
        # TODO
        raise NotImplementedError("Please implement this type of node in the back end.")

def _apply_parallel_node(modified_src: common.CompilerTarget, node: intrep.IrNode, intermediate_rep: intrep.IntermediateRepresentation):
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
    # Modify the source to launch n gangs (gangs = parallel processes in host back end)

    ## Import the appropriate multiprocessing stuff into the new module if not already there
    modified_src.add_import("multiprocessing")

    ## Move the node's source code into a kernel function
    modified_src.add_kernel(kernelsrc)

    ## Place process creation, data movement, process destruction in the old location
    pass

def _apply_loop_node(modified_src: common.CompilerTarget, node: intrep.IrNode, intermediate_rep: intrep.IntermediateRepresentation):
    """
    """
    pass
