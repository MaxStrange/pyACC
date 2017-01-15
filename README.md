# pyACC
OpenACC for Python

Ever wanted to write OpenACC in Python? Neither have I, but I figured it would
be fun to program a way to do it.

The idea is that you can use Python metaprogramming to accomplish the same
thing as OpenACC compiler directives. E.g.:

@acc(p_or_k='parallel', loop=True, copyout="ret[0:len(ret)]")
def dosomething(data, ret):
    for d in data:
        ret.append(d ** 2)

        
