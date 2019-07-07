"""
This module tests the nominal ("happy path") usage.
"""
import unittest
import os
import sys

mydir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(mydir, "../..")))
import acc.api as openacc

####################################################################################
###################### SOURCE CODE TO TEST #########################################
####################################################################################

@openacc.acc()
def no_pragmas0():
    pass

@openacc.acc()
def no_pragmas1():
    """
    Docstring. Hey there.
    """
    pass

####################################################################################
###################### ACTUAL TESTS ################################################
####################################################################################

class TestNominalUsage(unittest.TestCase):
    def test_no_pragmas(self):
        """
        Test the simplest possible use case - a decorated function with no pragmas at all.
        """
        # Simple crash tests
        no_pragmas0()
        no_pragmas1()

if __name__ == "__main__":
    unittest.main()
