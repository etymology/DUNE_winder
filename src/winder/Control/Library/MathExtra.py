###############################################################################
# Name: MathExtra.py
# Uses: Miscellaneous math functions.
# Date: 2016-08-25
# Author(s):
#   Andrew Que <aque@bb7.com>
###############################################################################

class MathExtra :
  #---------------------------------------------------------------------
  @staticmethod
  def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    """
    Return True if the values a and b are close to each other and False otherwise.

    Whether or not two values are considered close is determined according to
    given absolute and relative tolerances.

    rel_tol is the relative tolerance - it is the maximum allowed difference
    between a and b, relative to the larger absolute value of a or b. For example,
    to set a tolerance of 5%, pass rel_tol=0.05. The default tolerance is 1e-09,
    which assures that the two values are the same within about 9 decimal digits.
    rel_tol must be greater than zero.

    abs_tol is the minimum absolute tolerance - useful for comparisons near zero.
    abs_tol must be at least zero.

    If no errors occur, the result will be: abs(a-b) <= max(rel_tol * max(abs(a),
    abs(b)), abs_tol).

    The IEEE 754 special values of NaN, inf, and -inf will be handled according to
    IEEE rules. Specifically, NaN is not considered close to any other value,
    including NaN. inf and -inf are only considered close to themselves.

    Args:
      a: floating point value.
      b: floating point value.

    Returns:
      Return True if the values a and b are close to each other and False otherwise.

    Notes:
      This function comes from Python 3.5 but is not in 2.7.  Copied verbatim.
    """
    print '$$$$$ IsClose a=%e b=%e rtol*max(ab)=%e' % (a, b, rel_tol * max(abs(a), abs(b)))
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
