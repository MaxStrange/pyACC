"""
Worker clause
"""

class WorkerClause:
    def __init__(self, num_workers: int):
        """
        """
        if num_workers is None:
            self.num_workers = -1  # TODO: this corresponds to when there is a worker clause, but no number
        else:
            self.num_workers = num_workers


    def __str__(self):
        return "{}".format(self.num_workers)
