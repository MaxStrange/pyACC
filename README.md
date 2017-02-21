# pyACC
OpenACC for Python

Rhymes with "kayak".

Ever wanted to write OpenACC in Python? Neither have I, but I figured it would
be fun to program a way to do it.

The idea is that you can use Python metaprogramming to accomplish the same
thing as OpenACC compiler directives. E.g.:

```python
@acc(con_or_dir="parallel", clauses=["loop", "copyout=ret[0:len(data)]")
def dosomething(data, ret):
    for d in data:
        ret.append(d ** 2)
```

At least, that's the idea. Currently, I've only written a bare minimum proof of concept.

Currently, my idea is to have a front end and any number of back ends. The front end is in
this repository, and so is a default back end, which uses parallel processing to parallelize
the decorated regions of code. Other back ends could use pyOpenCL or pyCUDA (or anything else)
to parallelize the decorated region.

Obviously, pyACC would be significantly slower than OpenACC, but pyOpenCL or pyCUDA are also
slower than their C/C++ counterparts. Blah blah blah speed/usability tradeoff blah blah.

## Dependencies
Just pip3 install the following:
- asttokens
- dill
- tqdm (probably won't be necessary in the future)
