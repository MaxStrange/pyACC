"""
Common methods and data structures used by the back ends.
"""
class CompilerTarget:
    """
    This class represents the compiler target. The compiler target is source code
    for a single Python module. As such, it is of the following form:

    ```python
    # Imports
    import whatever
    import anotherwhatever
    import multiprocessing
    import pycuda

    # Kernel Function(s)
    def kernel_add_vectors(a, b, i, j, q):
        res = []
        for idx in range(i, j):
            res.append(a[i] + b[i])
        q.put((res, i))

    # decorated_function's modified source
    def docorated_function(a, b):
        q = multiprocessing.Queue()
        processes = []
        ngangs = 8
        nelems_per_gang = int(len(a) / ngangs)
        for idx in range(ngangs):
            i = idx * nelems_per_gang
            j = i + nelems_per_gang if idx != (len(a) - 1) else len(a)
            p = multiprocessing.Process(target=kernel_add_vectors, args=(a, b, i, j, q))

        for p in processes:
            p.start()

        res = [0 for _ in range(len(a))]
        for idx in range(ngangs):
            part, i, j = q.get()
            res[i:j] = part

        for p in processes:
            p.join()

        return res
    ```
    """
    def __init__(self, intermediate_rep):
        """
        """
        self.importsection = ""             # Source code for the import section
        self.kernel_code_sections = []      # One source string per kernel
        self.decorated_function_code = ""   # Source code for the refactored function
        self._modules = set()               # Set of modules the new code will import

        # Add the import statements for the needed modules
        for mod in intermediate_rep.meta_data.funcs_mods:
            self.add_import(mod)

    def add_import(self, module):
        """
        Utility function for adding an import statement.

        Adds `import module` to the import section of the source code, where `module`
        is the given module. Does not add it if this module is already in the import section.
        """
        if module not in self._modules:
            self.importsection += "import {}\n".format(module)

    def build(self):
        """
        Builds and returns the resultant source code.
        """
        return "{imports}\n\n{kernels}\n{decorated_function}".format(imports=self.importsection, kernels=self._build_kernels_section(), decorated_function=self.decorated_function_code)

    def _build_kernels_section(self):
        """
        Builds and returns a string representation of the kernels.
        """
        s = ""
        for kernel in self.kernel_code_sections:
            s += kernel + "\n\n"
        return s
