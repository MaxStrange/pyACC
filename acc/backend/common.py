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
    def __init__(self):
        """
        """
        self.importsection = ""             # Source code for the import section
        self.kernel_code_sections = []      # One source string per kernel
        self.decorated_function_code = ""   # Source code for the refactored function
