# acc

This folder contains all the code for pyACC. From an end-user's perspective,
api.py is the only module that will be used. This module multiplexes the
@acc decorator according to the ~OpenACC 2.7 standard and calls into the
frontend module.

The frontend will then call the appropriate backend according to what
backend the user has set (and installed).
