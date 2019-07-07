"""
This module contains all the tests for the Parallel-Loop hybrid construct.
"""
import src
import unittest

class TestParalellLoop(unittest.TestCase):
    def test_nominal(self):
        """
        Test the nominal use of a parallel loop.
        """
        sqrd = src.test_function()
        expected = [0, 1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
        self.assertEqual(len(sqrd), len(expected))

        for i, (s, e) in enumerate(zip(sqrd, expected)):
            self.assertEqual(s, e, "sqrd[{}] should equal expected[{}], but {} != {}".format(i, i, s, e))

if __name__ == "__main__":
    unittest.main()
