"""
This is the intermediate representation module. It contains all the code that
is shared between the frontend and any backends. In other words, backends
should have access to this code, but they should not include any code from the
frontend. The frontend, meanwhile, should include this file and be agnostic
about which particular backend it is using (the backend is passed into the
frontend as an argument).
"""
import acc.frontend.util.util as util
import acc.frontend.util.errors as errors
import acc.ir.metavars as metavars
import acc.ir.icv as icv
import os
import re

class IrNode:
    """
    IntermediateRepresentation tree node. Base class for all types
    of Nodes.
    """
    def __init__(self, lineno: int, src: str, children=None):
        """
        An IrNode is a node in the IntermediateRepresentation tree.
        Each IrNode type contains all the specifics of their clauses,
        but all IrNodes contain the following items:

        - lineno: The line number (function-based - i.e., starting at 0 at the
                  function declaration) of the pragma that was found.
        - src:    The source code that the node encompasses, if it encompasses any.
        """
        if children is None:
            self.children = []
        else:
            self.children = children

        self.lineno = lineno
        self.src = src

    def add_child(self, child):
        """
        Adds `child` to this IrNode's list of children.
        """
        self.children.append(child)

class AccNode(IrNode):
    """
    The root of an IntermediateRepresentation tree.
    The line number of this node should be zero, and the
    src should be the function's source.
    """
    def __init__(self, lineno: int, src: str):
        super().__init__(lineno, src)

    def __str__(self):
        return "AccNode (Root)"

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
    def __init__(self, meta_data: metavars.MetaVars, icvs: icv.ICVs):
        """
        """
        self.meta_data = meta_data                          # All the meta data
        self.internal_control_vars = icvs                   # All the ICVs for the back-end
        self.src = meta_data.src                            # Shortcut to the source code
        self.root = AccNode(0, self.src)                    # The root of the tree
        self._lineno_lookup = {}                            # A hash table for line number -> IrNode
        self.dependency_graph = self._construct_dgraph()    # A DAG for dependency relationships

    def __repr__(self):
        s = ""
        for node in self.breadth_first_traversal():
            s += str(node) + "\n"
        return s

    def __str__(self):
        return repr(self)

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

    def breadth_first_traversal(self):
        """
        Yields the nodes in the IR one at a time, in breadth first order.
        """
        children = self.root.children
        childqueue = []
        while children:
            for child in children:
                yield child
                childqueue.append(child)
            if childqueue:
                children = childqueue.pop(0).children
            else:
                children = []

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

    def get_source_region(self, lineno: int) -> str:
        """
        Given a line number containing a pragma, return the source string that the
        directive in that pragma encapsulates. For example,

        ```python
        # pragma acc parallel loop collapse(2)
        for i in range(5):
            for j in range(6):
                for k in range(7):
                    foo()
        ```

        would result in

        ```python
        for i in range(5):
            for j in range(6):
                for k in range(7):
                    foo()
        ```

        In this example, even though the parallel loop construct has a collapse of 2,
        the entire loop is necessary for the back end to determine what to do,
        and therefore the source region is the entire loop.

        For constructs that are normally denoted in C/C++ via opening and closing braces,
        in Python, we require that the scope be denoted with a commented brace:

        ```python
        # pragma acc kernels
        #{
            foo()
            bar()
            baz()
        #}
        ```

        If the pragma is one that does not encapsulate source code, None is returned.
        """
        pragma = self._get_src_line_by_lineno(lineno)
        directive, clause_list = util.parse_pragma_to_directive_and_clauses(pragma)

        # Check for loop hybrid
        if directive == "parallel" and clause_list[0] == "loop":
            directive = "parallel loop"
        elif directive == "kernels" and clause_list[0] == "loop":
            directive = "kernels loop"

        # Now determine region based on directive
        if directive   == "parallel":
            return self._get_region_from_scope_or_braces(lineno)
        elif directive == "kernels":
            return self._get_region_from_scope_or_braces(lineno)
        elif directive == "parallel loop":
            return self._get_region_from_scope(lineno)
        elif directive == "kernels loop":
            return self._get_region_from_scope(lineno)
        elif directive == "serial":
            return self._get_region_from_scope_or_braces(lineno)
        elif directive == "data":
            return self._get_region_from_scope_or_braces(lineno)
        elif directive == "enter":  # enter data
            return None
        elif directive == "exit":   # exit data
            return None
        elif directive == "host_data":
            return self._get_region_from_scope_or_braces(lineno)
        elif directive == "loop":
            return self._get_region_from_scope(lineno)
        elif directive == "cache":
            return None
        elif directive == "atomic":
            return self._get_src_line_by_lineno(lineno + 1)
        elif directive == "declare":
            return None
        elif directive == "init":
            return None
        elif directive == "shutdown":
            return None
        elif directive == "set":
            return None
        elif directive == "update":
            return None
        elif directive == "wait":
            return None
        elif directive == "routine":
            return self._get_region_from_scope(lineno)
        else:
            raise ValueError("Unrecognized construct or directive:", directive)

    def _construct_dgraph(self):
        """
        Constructs a directed acyclic graph (DAG) for showing
        dependencies between all the variables in the decorated function's
        source code.
        """
        # TODO
        return []

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

        # TODO: Determine the best way to specify 'code blocks' in Python
        #       In C/C++, you can use curly braces to show the scope of the construct,
        #       but in Python, that's not really an option. Probably best to do
        #       a special comment to close the construct region.
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

    def _get_region_from_scope_or_braces(self, lineno: int) -> str:
        """
        If the line after lineno is a commented open-brace ('#{'),
        the region spanned by the open and close braces will be returned. This will
        not include the braces themselves.

        If the line after lineno is not a commented open-brace, this method
        will return the block of code as inferred by Python's whitespace rules,
        so a for loop, for example:

        ```python
        for i in range(7):
            foo()
            bar()
            for j in range(9):
                baz()
        print("hello world")
        ```

        would be returned with the `print("hello world")` removed, since it is not
        part of the for loop's block.
        """
        nextline = self._get_src_line_by_lineno(lineno + 1)
        regex = re.compile(r"(\s)*#(\s)*{.*")
        if regex.match(nextline):
            return self._get_region_from_braces(lineno)
        else:
            return self._get_region_from_scope(lineno)

    def _get_region_from_braces(self, lineno: int) -> str:
        """
        Gets the region of source code starting from lineno + 1 which is enclosed
        by commented braces. Lineno + 1 must be an open brace.
        """
        regex_open = re.compile(r"(\s)*#(\s)*{.*")
        regex_close = re.compile(r"(\s)*#(\s)*}.*")

        # Sanity check the input
        openbrace = self._get_src_line_by_lineno(lineno + 1)
        assert regex_open.match(openbrace), "Line {} should be an open brace but is '{}'.".format(lineno + 1, openbrace)

        # Now walk through the lines starting at lineno + 1, adding the lines
        # that are not a brace to the region_lines, and stopping once we reach the ending brace
        possible_lines = self.src.splitlines()[lineno + 1 : ]
        region_lines = []

        # Because it is possible that we have multiple regions of brace-enclosed source,
        # we must keep track of any open-braces we see, and only return once we have seen
        # the right close-brace
        nopens = 0
        for line in possible_lines:
            if regex_open.match(line):
                nopens += 1
            elif regex_close.match(line):
                nopens -= 1

            if nopens == 0:
                return os.linesep.join(region_lines)
            else:
                region_lines.append(line)

        errorlines = [self._get_src_line_by_lineno(i) for i in (lineno - 1, lineno)]
        errorlines = os.linesep.join(errorlines)
        raise SyntaxError("Missing closing brace for open brace at line {} inside of function. Lines around error: {}".format(lineno, errorlines))

    def _get_region_from_scope(self, lineno: int) -> str:
        """
        Gets the region of source code starting from lineno + 1 which is governed
        by Python's whitespace code block rules.
        """
        possible_lines = self.src.splitlines()[lineno + 1 : ]
        region_lines = []

        # TODO: Handle explicit line continuation (\)
        # Walk the source lines starting at lineno + 1, and once our leading whitespace
        # gets back to where we started, we are done
        currentws = -1
        for number, line in enumerate(possible_lines, start=lineno + 1):
            if number == lineno + 1:
                # This is the starting amount of leading whitespace
                startingws = len(line) - len(line.lstrip(' '))
            else:
                currentws = len(line) - len(line.lstrip(' '))

            if currentws == startingws:
                break
            else:
                region_lines.append(line)

        return os.linesep.join(region_lines)

    def _get_src_line_by_lineno(self, lineno: int) -> str:
        """
        Returns the source code at the given function-oriented line number.
        """
        return self.src.splitlines()[lineno]

    def _pragma_encompasses_child(self, child: IrNode, lineno: int) -> bool:
        """
        Returns True if the given child node should be contained in the pragma
        found in the source code at lineno. Returns False otherwise.

        According to my reading of the spec, only kernels, serial, and parallel
        constructs can encompass other nodes.
        """
        # Get the directive from the pragma
        pragma = self.src.splitlines()[lineno]
        directive_and_clauses = pragma.partition("acc")[-1].split(' ')
        directive_and_clauses = [word for word in directive_and_clauses if word != '']
        directive = directive_and_clauses[0]

        # Determine if we are contained in this pragma
        return directive in ("parallel", "kernels", "serial")
