#   Basic arithmetic library for ProjectQ
#   Date:   20 Mar 2018
#   Author: Simon Mathis
#   Contact: mathissi@student.ethz.ch
#
#   Library to provide basic arithmetic Math gates such as an Adder or Subtractor gate.
#   The Adder gate is used in the inference mechanism of an Agent and the Subtractor is
#   its inverse.

from projectq.ops import BasicMathGate


def add(a, b):
    return (a, a + b)


def subtract(a, b):
    return (a, a - b)


# ----------------------------------------------------------------------------------------------------------------------
class Adder(BasicMathGate):
    """
    Adder Gate to add state of one qubit to that of another.

    Example:
    Adder() | (to_add, where_to_add_to)

    Output:
    (to_add, where_to_add_to + to_add)
    """

    def __init__(self):
        BasicMathGate.__init__(self, add)


# ----------------------------------------------------------------------------------------------------------------------
class Subtractor(BasicMathGate):
    """
    Subtract Gate to subtract state of one qubit from that of another.

    Example:
    Subtractor() | (to_subtract, where_to_subtract_from)

    Output:
     (to_subtract, where_to_subtract_from - to_subtract)
    """

    def __init__(self):
        BasicMathGate.__init__(self, subtract)

    def get_inverse(self):
        return Adder()


# ----------------------------------------------------------------------------------------------------------------------
Subtract = Subtractor()


# Define the inverse of an Adder() gate to be a Subtractor() gate
def invert_add(_):
    return Subtractor()


setattr(Adder, "get_inverse", invert_add)

Add = Adder()
