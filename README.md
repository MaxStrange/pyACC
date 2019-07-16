# pyACC

[![Build Status](https://travis-ci.org/MaxStrange/pyACC.svg?branch=master)](https://travis-ci.org/MaxStrange/pyACC)

OpenACC for Python

Rhymes with "kayak".

Ever wanted to write OpenACC in Python? Neither have I, but I figured it would
be fun to program a way to do it. BTW, if you actually want functionality that is similar
to OpenACC (i.e., super easy speed up of possibly already existing code), but in Python,
take a look at [Numba](https://github.com/numba/numba), which this project will be using
for GPU-acceleration.

The idea is that you can use Python metaprogramming to accomplish the same
thing as OpenACC compiler directives. E.g.:

```python
@acc()
def do_something(data, ret):
    #pragma acc parallel loop copyout=ret[0:len(data)]
    for d in data:
        ret.append(d ** 2)
```

At least, that's the idea. Currently, I've only written a bare minimum proof of concept.

## Purpose

This project aims to create a fully compliant implementation of the OpenACC 2.7 standard,
but in Python, instead of C/C++ or Fortran. Currently, a host-side back end uses multiprocessing
and exposes only one level of parallelism.

## How does it work?

How can OpenACC work in Python, you ask? Let me tell you! OpenACC in C/C++ works via compiler pragmas,
which means that the compiler is responsible for generating code that takes advantage of
hardware accelerators.

In Python, there isn't really much of a compilation phase; indeed, part of the draw of Python is
how easy it is to iterate on code implementations, which is partly enabled by removing the separate
compilation step in the C/C++ workflow. So, instead of adding a new compilation step to OpenACC Python,
I've simply used Python's introspective abilities to make it OpenACC compliant.

Specifically, the user decorates a function with `@acc()` and comments the code in that function
with `#pragma acc parallel whatever` just like they would in C/C++ OpenACC. When the Python code
is running, any time the `@acc()`-decorated function is called, this library hooks the function call,
scans the source code of the decorated function, rewrites it according to the comments,
imports the rewritten code, and calls the rewritten function instead of the user-created one.
This means there is a significant overhead of just-in-time compilation every time an `@acc()`-decorated
function is called, however, for large enough input sizes, this should not matter.

## Status

This project is mostly for fun, though I am hoping to squeeze as much performance out of it as I can,
and I would welcome contributions too. I'm working on it entirely in my spare time (of which I have little),
and I try to work on other things as well, so this is unlikely to be usable any time soon. Though
I hope to have a host-side back end example up and running soon.

## Installation

This project is tested on Python 3.5, 3.6, and 3.7. It is not pip-installable right now. It can
be tested by following the directions in .travis.yml.
