"""
This is the intermediate representation module. It contains all the code that
is shared between the frontend and any backends. In other words, backends
should have access to this code, but they should not include any code from the
frontend. The frontend, meanwhile, should include this file and be agnostic
about which particular backend it is using (the backend is passed into the
frontend as an argument).
"""

class Code:
    """
    This class represents source code along with any meta variables needed by
    backend's API functions. It should also have utility functions for
    manipulating the source code.
    """
    def __init__(self, src):
        """
        @param src: Source code. I imagine that this will be a string.
        """
        self._src = src
