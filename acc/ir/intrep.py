"""
This is the intermediate representation module. It contains all the code that
is shared between the frontend and any backends. In other words, backends
should have access to this code, but they should not include any code from the
frontend. The frontend, meanwhile, should include this file and be agnostic
about which particular backend it is using (the backend is passed into the
frontend as an argument).
"""

class Node:
    """
    IntermediateRepresentation tree node.
    """

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
    def __init__(self, src: str):
        self.src = src
        self.root = None
