"""
This is the intermediate representation module. It contains all the code that
is shared between the frontend and any backends. In other words, backends
should have access to this code, but they should not include any code from the
frontend. The frontend, meanwhile, should include this file and be agnostic
about which particular backend it is using (the backend is passed into the
frontend as an argument).
"""

class IrNode:
    """
    IntermediateRepresentation tree node. Base class for all types
    of Nodes.
    """
    def __init__(self, children=None):
        if children is None:
            self.children = []
        else:
            self.children = children

    def add_child(self, child):
        """
        Adds `child` to this IrNode's list of children.
        """
        self.children.append(child)

class AccNode(IrNode):
    """
    The root of an IntermediateRepresentation tree.
    """
    def __init__(self):
        super().__init__()

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
    def __init__(self, meta_data):
        """
        """
        self.meta_data = meta_data
        self.src = meta_data.src
        self.root = AccNode()
