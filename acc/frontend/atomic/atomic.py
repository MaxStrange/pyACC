"""
Summary
-------
An atomic construct ensures that a specific storage location is accessed and/or
updated atomically, preventing simultaneous reading and writing by gangs, workers, and vector threads
that could result in indeterminate values.

Syntax
------
The syntax of the atomic constructs is:

#pragma acc atomic [atomic-clause] new-line
expression-stmt

or:

#pragma acc atomic update capture new-line
structured-block

Where atomic-clause is one of read, write, update, or capture. The expression-stmt is an
expression statement with one of the following forms:

If the atomic-clause is read:
v = x;

If the atomic-clause is write:
x = expr;

If the atomic-clause is update or no clause appears:
x++;
x--;
++x;
--x;
x binop= expr;
x = x binop expr;
x = expr binop x;

If the atomic-clause is capture:
v = x++;
v = x--;
v = ++x;
v = --x;
v = x binop= expr;
v = x = x binop expr;
v = x = expr binop x;

The structured-block is a structured block with one of the following forms:
{v = x; x binop= expr;}
{x binop= expr; v = x;}
{v = x; x = x binop expr;}
{v = x; x = expr binop x;}
{x = x binop expr; v = x;}
{x = expr binop x; v = x;}
{v = x; x = expr;}
{v = x; x++;}
{v = x; ++x;}
{++x; v = x;}
{x++; v = x;}
{v = x; x--;}
{v = x; --x;}
{--x; v = x;}
{x--; v = x;}

In the preceding expressions:
• x and v (as applicable) are both l-value expressions with scalar type.
• During the execution of an atomic region, multiple syntactic occurrences of x must designate
  the same storage location.
• Neither of v and expr (as applicable) may access the storage location designated by x.
• Neither of x and expr (as applicable) may access the storage location designated by v.
• expr is an expression with scalar type.
• binop is one of +, *, -, /, &, ˆ, |, <<, or >>.
• binop, binop=, ++, and -- are not overloaded operators.
• The expression x binop expr must be mathematically equivalent to x binop (expr). This
  requirement is satisfied if the operators in expr have precedence greater than binop, or by
  using parentheses around expr or subexpressions of expr.
• The expression expr binop x must be mathematically equivalent to (expr) binop x. This
  requirement is satisfied if the operators in expr have precedence equal to or greater than binop,
  or by using parentheses around expr or subexpressions of expr.
• For forms that allow multiple occurrences of x, the number of times that x is evaluated is
  unspecified.

An atomic construct with the read clause forces an atomic read of the location designated by x.
An atomic construct with the write clause forces an atomic write of the location designated by
x.

An atomic construct with the update clause forces an atomic update of the location designated
by x using the designated operator or intrinsic. Note that when no clause appears, the semantics
are equivalent to atomic update. Only the read and write of the location designated by x are
performed mutually atomically. The evaluation of expr or expr-list need not be atomic with respect
to the read or write of the location designated by x.

An atomic construct with the capture clause forces an atomic update of the location designated
by x using the designated operator or intrinsic while also capturing the original or final value of
the location designated by x with respect to the atomic update. The original or final value of the
location designated by x is written into the location designated by v depending on the form of the
atomic construct structured block or statements following the usual language semantics. Only
the read and write of the location designated by x are performed mutually atomically. Neither the
evaluation of expr or expr-list, nor the write to the location designated by v, need to be atomic with
respect to the read or write of the location designated by x.

For all forms of the atomic construct, any combination of two or more of these atomic constructs
enforces mutually exclusive access to the locations designated by x. To avoid race conditions, all
accesses of the locations designated by x that could potentially occur in parallel must be protected
with an atomic construct.

Atomic regions do not guarantee exclusive access with respect to any accesses outside of atomic
regions to the same storage location x even if those accesses occur during the execution of a reduction
clause.

If the storage location designated by x is not size-aligned (that is, if the byte alignment of x is not a
multiple of the size of x), then the behavior of the atomic region is implementation-defined.

Restrictions
------------
• All atomic accesses to the storage locations designated by x throughout the program are
  required to have the same type and type parameters.
• Storage locations designated by x must be less than or equal in size to the largest available
  native atomic operator width.
"""
