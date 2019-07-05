"""
Errors used by the frontend.
"""

class InvalidClauseError(Exception):
    """
    Indicates an invalid clause while parsing a pragma. Either the clause
    is not allowed for this directive or the syntax of the clause is wrong.

    Please pass helpful error messages into the exception so that the
    end-user is not confused by a generic error message when they misspelled
    something.
    """
    pass

class VersionNotSupportedError(Exception):
    """
    Indicates that the version of Python is not supported.
    """
    pass
