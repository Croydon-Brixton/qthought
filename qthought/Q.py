'''
Author: Simon Mathis (mathissi@ethz.ch)
Date: 25.12.2018

Library corresponding to assumption Q in the RF paper.
Contains the semantics of the 'Born rule' , i.e. the overlap
computation in our implementation.
'''
from copy import deepcopy
import numpy as np
import warnings


def filter_subspace(wavefunc: dict, subspace: list) -> dict:
    """
    Filters out component of wavefunction which lies in subspace
    :param wavefunc: dict, contains complex amplitudes of the wavefunction
                           in computational basis states
    :param subspace: list, The list of computational basis states in str format that span the subspace
                           e.g. ['100', '101']
    :return:         dict, The non-normalized wavefunction contained in the given 'subspace'
    """
    filtered_wf = deepcopy(wavefunc)

    for key in wavefunc.keys():
        if key not in subspace:
            filtered_wf[key] = 0.0j

    return filtered_wf


def renormalize(wavefunc: dict, tol = 1e-7) -> dict:
    """
    Renormalize a wavefunction. Returns None if the wavefunction has norm 0.
    :param wavefunc: dict, contains complex amplitudes of the wavefunction
                           in computational basis states
    :param tol:      int,  The tolerance below which a state will be said to
                           have zero overlap with another.
    :return:         dict, The renormalized wavefunction as a dictionary of amplitudes to the
                           computational basis states. If wavefunction is non-renormalizable,
                           'None' will be returned.
    """
    summands = [abs(val) ** 2 for val in wavefunc.values()]
    state_norm = np.sqrt(sum(summands))

    # catch the case of a non renormalizeable (zero) wavefunction:
    if state_norm < tol:
        warnings.warn('Warning! Wavefunction norm smaller than tolerance. Likely there is no overlap or a '
                      'bug in your code.')
        return None

    for key, val in wavefunc.items():
        wavefunc[key] = val / state_norm

    return wavefunc


def overlap(psi: dict, phi: dict) -> complex:
    """
    Calculates the inner product between two states <phi|psi>.
    :param psi:  dict, describing state |psi>
    :param phi:  dict, describing state |phi>
    :return:     inner product <phi|psi>
    """
    assert isinstance(psi, dict), 'Please provide your state as a dict.'
    assert isinstance(phi, dict), 'Please provide your state as a dict.'
    assert len(psi) >= len(phi), 'Make sure you compare states of the same length.'

    psi_array = np.zeros(len(psi), dtype=complex)
    phi_array = np.zeros(len(psi), dtype=complex)

    for i, key in enumerate(psi.keys()):
        psi_array[i] = psi[key]

        if key not in phi.keys():
            phi_array[i] = 0
        else:
            phi_array[i] = phi[key]

    return np.inner(psi_array, np.conj(phi_array))


def overlaps_with_subspace(wavefunc: dict, subspace: list) -> bool:
    """
    Calculates if there is overlap betweeen the wavefunction and the subspace spanned
    by the computational basis vectors provided in the subspace parameter.
    Note: This only works for subspaces aligned with the comp. basis.
    :param wavefunc: dict, contains complex amplitudes of the wavefunction
                           in computational basis states
    :param subspace: list, list containing the computational basis vectors which
                           span the subspace
    :return: bool
    """
    assert isinstance(wavefunc, dict), 'Please provide your state as a dict.'
    assert isinstance(subspace, list), 'Please provide subspace as a list of str.'

    # Deal with empty subspace:
    if not subspace:
        return False
    assert isinstance(subspace[0], str), 'Please provide subspace as a list of str.'
    assert len(wavefunc) >= len(subspace)
    tol = 1e-7

    for basisvector in subspace:
        if abs(wavefunc[basisvector]) > tol:
            return True

    return False


def project_wavefunction(wavefunc: dict, subspace: list) -> dict:
    proj_wf_unnorm = filter_subspace(wavefunc, subspace)
    return renormalize(proj_wf_unnorm)


def probability_in_subspace(wavefunc: dict, subspace: list) -> float:
    """
    Calculates the probability that the wavefunction 'wavefunc' lies in 'subspace'
    Note: This only works for subspaces aligned with the comp. basis.
    :param wavefunc: dict, contains complex amplitudes of the wavefunction
                           in computational basis states
    :param subspace: list, list containing the computational basis vectors which
                           span the subspace
    :return: float
    """
    assert isinstance(wavefunc, dict), 'Please provide your state as a dict.'
    assert isinstance(subspace, list), 'Please provide subspace as a list of str.'

    # Deal with empty subspace:
    if not subspace:
        return 0
    assert isinstance(subspace[0], str), 'Please provide subspace as a list of str.'
    assert len(wavefunc) >= len(subspace)
    subspace_prob = 0.

    # add up probabilities for all basisvectors in the subspace
    for basisvector in subspace:
        basisvector_prob = abs(wavefunc[basisvector]) ** 2
        subspace_prob += basisvector_prob

    return subspace_prob


#TODO: move to quantum_systems
def outer_subspace_product(subspace1: list, subspace2: list, reverse: bool = False) -> list:
    """
    Forms the outer (cartesian) product of two subspaces which are both aligned
    with the comp. basis.
    :param subspace1: list, list containing the computational basis vectors which
                            span the subspace 1
    :param subspace2: list, list containing the computational basis vectors which
                            span the subspace 2
    :param reverse:   bool, if True the order of the cartesian product is reversed
                            i.e. subspace2 x subspace1
    :return: list, the cartesian product of subspace 1 & 2 in the specified order
    """
    assert isinstance(subspace1, list), 'Please provide subspace as a list of str.'
    assert isinstance(subspace2, list), 'Please provide subspace as a list of str.'

    product_subspace = []
    if subspace1 == []: return subspace2
    if subspace2 == []: return subspace1

    for basisvector1 in subspace1:
        for basisvector2 in subspace2:
            if reverse:
                product_subspace += [basisvector2 + basisvector1]
            else:
                product_subspace += [basisvector1 + basisvector2]
    return product_subspace


def all_basis_vectors(n: int) -> list:
    """Returns a list of all 2**n the basis vectors of a qureg of length n as strings"""
    assert n >= 0, "n must be > 0"
    basis_1dim = ['0', '1']

    if n == 0:
        return []
    if n == 1:
        return basis_1dim
    else:
        current_basis = basis_1dim
        for i in range(1, n):
            # can be made more efficient (e.g. by current_basis, current basis until we reach sqrt(n))
            current_basis = outer_subspace_product(basis_1dim, current_basis)

    return current_basis