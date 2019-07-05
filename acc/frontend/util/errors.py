"""
Errors used by the frontend.
"""

class Debug:
    """
    Debug machine for building useful error messages.
    """
    def __init__(self, intermediate_rep):
        self.intermediate_rep = intermediate_rep
        self.lineno = None

    def build_message(self, additionalmsg=None):
        """
        Builds a useful error message. If given, adds `additionalmsg`
        on a new line after the built message.
        """
        line = self.intermediate_rep.src.splitlines()[self.lineno]
        msg = "Error at line:\n{}\n".format(line)
        if additionalmsg is not None:
            msg += additionalmsg
        return msg

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
