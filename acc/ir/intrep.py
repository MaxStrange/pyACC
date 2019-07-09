"""
This is the intermediate representation module. It contains all the code that
is shared between the frontend and any backends. In other words, backends
should have access to this code, but they should not include any code from the
frontend. The frontend, meanwhile, should include this file and be agnostic
about which particular backend it is using (the backend is passed into the
frontend as an argument).
"""
import re

class IrNode:
    """
    IntermediateRepresentation tree node. Base class for all types
    of Nodes.
    """
    def __init__(self, lineno, children=None):
        if children is None:
            self.children = []
        else:
            self.children = children

        self.lineno = lineno

    def add_child(self, child):
        """
        Adds `child` to this IrNode's list of children.
        """
        self.children.append(child)

class AccNode(IrNode):
    """
    The root of an IntermediateRepresentation tree.
    """
    def __init__(self, lineno):
        super().__init__(lineno)

class IntermediateRepresentation:
    """
    This class contains everything that the backend should need to rewrite
    the decorated function.

    This class is a Tree-like data structure, where the root node contains
    the information about the whole function that was decorated,
    then that node's children contain information about top-level pragmas
    in the function, and children under those children contain information
    about pragmas inside their parents' scope.

    # TODO: Give an example
    """
    def __init__(self, meta_data, icvs):
        """
        """
        self.meta_data = meta_data          # All the meta data
        self.internal_control_vars = icvs   # All the ICVs for the back-end
        self.src = meta_data.src            # Shortcut to the source code
        self.root = AccNode(0)              # The root of the tree
        self._lineno_lookup = {}            # A hash table for line number -> IrNode

    def add_child(self, child):
        """
        Adds a child node to the tree. Determines where to add the node
        by seeing what the node's line number is and then going back
        up in the source code until it finds either the pragma construct
        that encompasses this new node or else it reaches the top of the
        function, in which case this node is added as a child of root.
        """
        # Add the child to the hash table. There shouldn't already be a node for this line number.
        assert child.lineno not in self._lineno_lookup, "Line number {} already in hash. Hash: {}".format(child.lineno, self._lineno_lookup)
        self._lineno_lookup[child.lineno] = child

        parent = self._get_parent(child)
        parent.add_child(child)

    def get_ancestors(self, node: IrNode) -> [IrNode]:
        """
        If `node` is already present in the IR tree, this method returns a list of
        references to the ancestors of that node.

        If `node` is not already present in the IR tree, this method returns a list
        of references to the ancestors that would exist, were this node inserted into
        the tree right now.
        """
        ancestors = []
        parent = self._get_parent(node)
        while id(parent) != id(self.root):
            ancestors.append(parent)
            parent = self._get_parent(parent)

        # Lastly, append the root
        ancestors.append(self.root)
        return ancestors

    def _get_parent(self, child: IrNode) -> IrNode:
        """
        Finds the parent of the given child. The last resort parent is the
        root node, which is the parent to everyone.
        """
        # Get the source code above child and reverse it for easy iteration
        src_lines_above_child = self.src.splitlines()[0:child.lineno]
        src_lines_above_child.reverse()
        line_numbers = [i for i in range(0, child.lineno)]
        line_numbers.reverse()

        # Walk up from here, looking for pragmas
        regexp = re.compile(r"^((\s)*#(\s)*(pragma)(\s)*(acc))")
        for lineno, line in zip(line_numbers, src_lines_above_child):
            if regexp.match(line):
                # This line is a '#pragma acc' line. Check if it encompasses me.
                if self._pragma_encompasses_child(child, lineno):
                    parent = self._get_node_by_lineno(lineno)
                    assert parent is not None, "Could not find node for pragma {} at line {}".format(line, lineno)
                    return parent

        # If we get here it is because we have scanned the whole function and not
        # found any nodes that encompass the child.
        return self.root

    def _get_node_by_lineno(self, lineno: int) -> IrNode:
        """
        Returns a reference to the node that was created for the pragma at the
        given lineno. If we can't find the node, we return None.
        """
        if lineno in self._lineno_lookup:
            return self._lineno_lookup[lineno]
        else:
            return None

    def _pragma_encompasses_child(self, child: IrNode, lineno: int) -> bool:
        """
        Returns True if the given child node should be contained in the pragma
        found in the source code at lineno. Returns False otherwise.
        """
        # TODO: Only certain types of constructs can actually encompass others
        #       Do this method
        return False
