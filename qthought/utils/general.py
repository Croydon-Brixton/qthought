#   Basic utilities library for Project Q
#   Author: Simon Mathis
#   Contact: mathissi@student.ethz.ch
#   Basic utilities for project-q to insprect states, print hte wavefunction and
#   carry out several other handy operations such as converting integers to bitstrings

import warnings
from copy import deepcopy

from numpy import fromstring, int8, array
from projectq.ops import X


# --- Rounding ---
def cround(number: complex, precision: int = 2) -> complex:
    """Rounds complex number by separately rounding real and imag part to given precision."""
    if number.imag == 0:
        return round(number.real, precision)
    elif number.real == 0:
        return round(number.imag, precision)*1j
    return round(number.real, precision) + round(number.imag, precision) * 1j


# --- INT <-> BITSTRING UTILS ---
def int_to_bitstring(n: int, desired_len=None) -> str:
    """Converts an integer into a bitstring (unicode representation) of desired length. MSB leftmost, LSB rightmost"""
    bitstring = bin(n)[2:]

    if desired_len:
        current_len = len(bitstring)
        assert current_len <= desired_len, 'Desired length too short and would result in cut-off'
        front = '0' * (desired_len - current_len)
        return front + bitstring

    return bitstring


def slice_bitstring_to_array(bitstring: str):
    """Slices bitstring of bits in unicode encoding into array"""
    with warnings.catch_warnings():  # To get rid of the deprecation warning for fromstring
        warnings.simplefilter("ignore")
        bitarray = (fromstring(bitstring, dtype=int8) - ord('0'))  # -ord removes the unicode encoding (48) of 0

    return bitarray


def int_to_bit_array(n: int, desired_len=None):
    """Turns an integer n into its corresponding bitstring in a numpy array

    Output :    array, [MSB, . . . , LSB]
    """
    bitstring = int_to_bitstring(n, desired_len)

    return slice_bitstring_to_array(bitstring)


# --- STATE ACCESSING AND PRINTING UTILS ---
def map_to_computational_basis(mapping: dict):
    """Maps a projectq mapping to the computational basis index such that
    qureg[0]  ... LSB
    qureg[-1] ... MSB"""
    n_qubits = len(mapping)
    n_states = 2 ** n_qubits

    weighting_factors = array([2 ** mapping[i] for i in range(n_qubits)][::-1])

    comp_basis_index = []
    for state_i in range(n_states):
        comp_basis_index += [sum(int_to_bit_array(state_i, desired_len=n_qubits)* weighting_factors)]

    # comp_basis_index[i] is the index  of the amplitude of the ith comp basis state in the wavefunction
    return comp_basis_index


def access_state(eng):
    """Function to access the state of the wavefunction of engine eng"""
    eng.flush()  # Flush engine to make sure all gates before state acess are executed
    mapping, wavefunction = deepcopy(eng.backend.cheat())
    n_qubits = len(mapping)
    n_states = len(wavefunction)

    comp_basis_index = map_to_computational_basis(mapping)

    correctly_ordered_state = {}

    for state_i in range(n_states):
        correctly_ordered_state[int_to_bitstring(state_i, desired_len=n_qubits)] = wavefunction[
            comp_basis_index[state_i]]

    return correctly_ordered_state


def print_state(eng, to_output=False):
    """Prints current state of eng in Dirac notation"""
    state = access_state(eng)

    output_string = ''

    for key, value in zip(state.keys(), state.values()):
        if value != 0:
            if any(output_string):
                output_string += ' + ' + str(cround(value)) + '|' + key + '>'
            else:
                output_string += str(cround(value)) + '|' + key + '>'

    if to_output:
        return output_string
    else:
        print(output_string)


# --- READOUT UTILS---
def readout(qureg, as_type='int'):
    """
    Function to read out the (comp. basis) state of a projectq.qureg as one of the types
    'array', 'int', or 'str'
    Notation:
    MSB ... qureg[-1]
    LSB ... qureg[0]
    """
    # TODO: Somehow this has unforseen effects when used with resetting of qubits instead of deallocation.
    result = array([int(qubit) for qubit in qureg])[::-1]

    if as_type == 'array':
        return result
    elif as_type == 'int':
        weights = array([2 ** i for i in range(len(result))])[::-1]
        return sum(result * weights)
    elif as_type == 'str':
        weights = array([2 ** i for i in range(len(result))])[::-1]
        result_int = sum(result * weights)
        return int_to_bitstring(result_int, desired_len=len(result))

    assert False, "as_type can only be one of 'array', 'int' or 'str'"


# --- GATE OPERATION UTILS ---
def prepare_state_n(qureg: list, n: int):
    """Prepares the n-th state starting from the 0-state. (i.e. adds the number n to the register)

    qureg:  list, list containing the qubits of the quantum register
    n :      int, the integer number state to be prepared

    Notation:
    qureg[0] - LSB
    qureg[-1] - MSB
    """
    assert 2 ** len(qureg) > n, "State %d does not fit into register of len %d (max: %d)." % (
    n, len(qureg), 2 ** len(qureg) - 1)

    bitstr = bin(n)[2:]
    while len(bitstr) < len(qureg):
        bitstr = '0' + bitstr

    # reverse bitstring for correct ordering
    bitstr = bitstr[::-1]

    for i, bit in enumerate(bitstr):
        if bit == '1':
            X | qureg[i]


def state_i_to_1(i, qureg):
    """
    Maps computational basis state |i> to |11...11>  (and vice versa - own inverse)

    :param i:  Integer index of the state |i>
    :type i: int
    :param qureg: ProjectQ Qubit register
    :type qureg: list
    :return: None
    """
    n_qubits = len(qureg)
    to_flip = int_to_bit_array(i, n_qubits)

    for ix, value in enumerate(to_flip[::-1]):
        if value == 0:
            X | qureg[ix]
