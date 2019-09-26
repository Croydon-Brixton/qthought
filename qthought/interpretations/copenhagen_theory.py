# Imports
from itertools import chain

from projectq.ops import get_inverse

from ..utils.arithmeticgates import Add
from ..utils.subspace import overlaps_with_subspace

from ..quantumsystem import QuantumSystem
from ..agents import InferenceTable


# ------------------1. Observe procedure  ------------------------------------------------------------------------------
def observe(agent_memory, qureg, reverse=False):
    assert len(agent_memory) >= len(qureg), 'Invalid observe. Observed system is larger than what memory ' \
                                            'of the agent can hold.'
    if reverse:
        get_inverse(Add) | (qureg, agent_memory)
    else:
        Add | (qureg, agent_memory)


# ------------------2. Inference procedures ----------------------------------------------------------------------------
def forward_inference(protocol,
                      subsys_x, t_x,
                      subsys_y, t_y,
                      silent=True):
    """
    Forward inference answers the question:
    Given 'subsys_x' is in comp. basis state i at time t_x of the protocol,
    what can I say about the result of a measurement of 'subsys_y' at time t_y after
    running the protocol up to t_y?
    """

    mapping = {}

    # Set up the engine and resource qubits
    qsys = QuantumSystem(protocol.get_requirements(), silent)
    n_mem_options = 2 ** len(qsys[subsys_x])  # number of possible subsys_x states
    n_pred_options = 2 ** len(qsys[subsys_y])

    assert t_x in protocol.get_times() and t_y in protocol.get_times(), 'Times t_x = %d, t_y = %d ' \
                                                                        'do not match protocol times' % (
                                                                            t_x, t_y)

    # Go through all subsys_x states and calculate the possible inference
    for i in range(n_mem_options):
        if not silent: print('----- Case %d -----' % i)

        # Run protocol until t_x
        protocol.run(qsys,
                     t_end=t_x,
                     silent=silent)

        # At t_x project wavefunction to subspace containing |i(subsys_x)>
        qsys.project_to_subspace(qsys.subspace_of_state_n(subsys_x, i))     # TODO: What if projection = 0? Error?
        if not silent:
            print('Projecting to subspace %s=%d' % (subsys_x, i))
            qsys.print_wavefunction()

        # Run protocol from t_x to t_y
        protocol.run(qsys,
                     t_start=t_x + 1,
                     t_end=t_y,
                     silent=silent)

        # Extract the statevector
        wavefunc = qsys.get_wavefunction()

        # Reset all qubits in qsys to state 0
        qsys.reset(silent)

        # compute the possible states a the end
        possible_states = []
        for j in range(n_pred_options):
            # get the subspace corresponding to subsys_y in state j
            output_j_subspace = qsys.subspace_of_state_n(subsys_y, j)
            if overlaps_with_subspace(wavefunc, output_j_subspace):
                possible_states += [j]

        # map memory state i of subsys_x to list of compatible output states for subsys_y
        mapping[i] = possible_states

    return InferenceTable(subsys_x, t_x,
                          subsys_y, t_y,
                          mapping)


def backward_inference(protocol, subsys_x, t_x, subsys_y, t_y, silent=True):
    """
    Forward inference answers the question:
    Given a measurement result of 'subsys_y' at the end of the protocol,
    what can I say about the result an Agent would have received had she done
    a measurement of 'subsys_x' before the protocol?
    running the protocol?
    """

    forward_mapping = forward_inference(protocol, subsys_x, t_x, subsys_y, t_y, silent)['table']

    output_vals = list(set(chain(*forward_mapping.values())))
    backward_mapping = {v: [] for v in output_vals}

    for inpt, possible_outputs in forward_mapping.items():
        for output in possible_outputs:
            backward_mapping[output] += [inpt]

    return InferenceTable(subsys_y, t_y,
                          subsys_x, t_x,
                          backward_mapping)
