from functools import wraps
from itertools import chain

from projectq.ops import get_inverse

from .utils.arithmeticgates import Add
from .utils.subspace import overlaps_with_subspace, probability_in_subspace, project_wavefunction

from .quantumsystem import QuantumSystem
from .agents import InferenceTable


# ---------- 1. Internal workings --------------------------------------------------------------------------------------
def find_possible_branches(qsys: QuantumSystem, subsys: str) -> tuple:
    """
    Finds all possible branches (with respective probabilities) in which a given QuantumSystem
    can branch under measurement of the specified subsystem in collapse theory.

    Args:
        qsys (QuantumSystem): The QuantumSystem object for which the possible branches should be computed.
        subsys (str): The name of the subsystem in the QuantumSystem which is measured. `subsys` has to
            be a valid subsystem of QuantumSystem.

    Returns:
        possible_branches (list): A list of the possible branches, i.e. disjoint subspaces belonging to
            the different possible eigenvalues obtained when measuring subsys (each subspace is in list
            format).
        states (list): A list of the respective wavefunctions projected on each of the possible branches.
        probabilities (list): A list of probabilities for `qsys` to collapse into the respective branches.

    Raises:
        Assertion: If `qsys` is not a QuantumSystem object.
    """

    assert isinstance(qsys, QuantumSystem), 'Argument `qsys` has to be a valid QuantumSystem'
    wf = qsys.get_wavefunction()
    possible_branches = []
    states = []
    probabilities = []

    for n in range(1 << len(qsys[subsys])):
        branch_n = qsys.subspace_of_state_n(subsys, n)

        if overlaps_with_subspace(wf, branch_n):
            prob_n = probability_in_subspace(wf, branch_n)
            possible_branches.append(branch_n)
            states.append(project_wavefunction(wf, branch_n))
            probabilities.append(prob_n)

    return possible_branches, states, probabilities


class QuantumTree:
    """
    A class to keep track of possible branches with their respective probabilities in collapse theories.
    Each branch of the `QuantumTree` is a `QuantumSystem` instance, corresponding to a possible outcome state.

    Args:
        qsys (QuantumSystem): The `QuantumSystem` which will be used as the root of the tree structure.

    Attributes:
        branches_ (list): A list of QuantumSystem objects, each corresponding to one branch of the tree structure
        probabilities_ (list): A list of the probabilities of occurence for the respective branches

    Raises:
        Assertion: If `qsys` is not a valid QuantumSystem object
    """

    def __init__(self, qsys: QuantumSystem):
        assert isinstance(qsys, QuantumSystem)
        self.branches_ = [qsys]
        self.probabilities_ = [1.]

    def branch_out(self, subsys: str, silent=True, inplace=True):
        """
        Splits the branches of a `QuantumTree` instance according to the possible measurement outcomes of a
        measurement on `subsys`. Note that this function modifies the given `QuantumTree` object inplace.

        Args:
            subsys (str): The subsystem along which the branches are computed. `subsys` must be a valid subsystem
                of the branches of the given `QuantumTree` object. (Otherwise an assertion is raised)
            silent (bool): If False, the generation message for the individual branches and their init states
                is printed to the console.
            inplace (bool): If True, the `QuantumTree` object is modified inplace.

        Returns:
            new_branches (list): A list of `QuantumSystem` objects, corresponding to the possible branches.
            new_probabilities(list): The list of probabilities to the respective new branches

        Raises:
            Assertion: If `subsys` is not a valid subsystem of the branches of the given `QuantumTree`.
        """
        # Initialize empty lists
        new_branches = []
        new_probabilities = []

        # Go through branches in `QuantumTree` and for each branch find the subbranches in which it will split
        for branch, branch_probability in zip(self.branches_, self.probabilities_):
            reqs = branch.reqs_
            _, states, probabilities = find_possible_branches(branch, subsys)

            # Initialize a `QuantumSystem` in the respective state for each of the possible subbranches and
            # add them to the `new_branches` list.
            for state, state_probability in zip(states, probabilities):
                system_branch_i = QuantumSystem(reqs, silent=silent)
                system_branch_i.set_wavefunction(state, silent=silent)
                new_branches.append(system_branch_i)
                new_probabilities.append(branch_probability * state_probability)
            # Deallocate old branches
            if inplace:
                branch.reset(silent=silent)
                del branch

        # Update the branches and probabilities of the `QuantumTree` instance.
        if inplace:
            self.branches_ = new_branches
            self.probabilities_ = new_probabilities

        return new_branches, new_probabilities

    def split_branch(self, index: int):
        """ Splits off a branch of the given `QuantumTree` instance and creates a new `QuantumTree` out of it.

        Args:
            index (int): The index of the branch in the given `QuantumTree` which should serve as the root of the
                new `QuantumTree` that will be generated.

        Returns:
            QuantumTree: A new `QuantumTree` with root self.branches[index]
        """
        return QuantumTree(self.branches_[index])

    def get_position(self, branch_index:int, subsys:str):
        """Returns the array indices of the position of subsystem `subsys` in branch `branch_index` of the
        given QuantumTree object."""
        return self.branches[branch_index].get_position(subsys)

    def __getitem__(self, index: int):
        """Returns the branch with given `index` as a QuantumSystem object.

        Args:
            index (int): The index of a branch in the given `QuantumTree`.

        Returns:
            QuantumSystem: The `QuantumSystem` corresponding to the `index`-th branch of the given `QuantumTree`.
        """
        return self.branches_[index]

    def __len__(self):
        """Returns the number of branches."""
        return len(self.branches_)

    def __repr__(self):
        """Simple console output"""
        full_str = 'BranchTree object \n'
        full_str += 'Branches: {0} \n'.format(len(self))
        full_str += 'Nqubits:  {0} per branch'.format(len(self.branches[0]))
        return full_str

    def __str__(self):
        full_str = ''
        for i, branch in enumerate(self.branches):
            if i == 0:  # Add print order on top
                full_str = 'Print order:'.ljust(14) + str(branch.subsystems[::-1]) + '\n'
            full_str += '---- Branch {0} ----\n'.format(i)
            branch['eng'].flush()
            full_str += branch.print_wavefunction(to_output=True)
            full_str += '\n'
        return full_str

    @property
    def branches(self) -> list:
        """Getter for the branches"""
        return self.branches_

    @property
    def subsystems(self, index: int = 0) -> list:
        """
        Returns the subsystem ordering (in hardware - reverse for print order) of the branch indexed
        by `index` of the given `QuantumTree`.

        Args:
            index (int): The index of a branch in the given `QuantumTree`.

        Returns:
            str: The ordering (in hardware - reverse for print order) of the subsystems of branch `index`.
        """
        return self.branches[index].subsystems

    def readout(self, branch:int, subsys:str, order='internal'):
        return self.branches[branch].readout(subsys, order)


# -------- 2. Wrapper for operations on QuantumSystems -----------------------------------------------------------------
def enable_branching(collapse_system=None, silent=True):
    """
    Wrapper function to enable functions that work on a `QuantumSystem` to also work on a `QuantumTree`.
    By passing a string argument to `collapse_system` a branching in the `QuantumTree` will be invoked.
    """

    def actual_decorator(func):
        @wraps(func)  # lift docstring and code of `func` to the wrapped function
        def wrapped_func(qsys, *args, **kwargs):
            if isinstance(qsys, QuantumTree):
                outputs = []
                for branch in qsys:
                    output = func(branch, *args, **kwargs)
                    outputs.append(output)
                if collapse_system is not None:
                    assert isinstance(collapse_system, str), 'The subsystem to collapse must be a `str` type object'
                    if not silent: print('Branching along subsystem {0}'.format(collapse_system))
                    qsys.branch_out(subsys=collapse_system)
                return outputs
            elif isinstance(qsys, QuantumSystem):
                output = func(qsys, *args, **kwargs)
                return output
            else:
                assert False, 'Argument `qsys` must be one of (QuantumTree, QuantumSystem)'

        return wrapped_func

    return actual_decorator


@enable_branching()
def get_possible_outcomes(qsys: QuantumSystem, subsys_y: str) -> list:
    possible_states = []
    wavefunc = qsys.get_wavefunction()
    for j in range(2 ** len(qsys[subsys_y])):
        output_j_subspace = qsys.subspace_of_state_n(subsys_y, j)
        if overlaps_with_subspace(wavefunc, output_j_subspace):
            possible_states += [j]
    return possible_states


@enable_branching()
def reset(qsys: QuantumSystem, silent=True) -> None:
    qsys.reset(silent)


# ------------------3. Wrapper for operations on QuantumSystems --------------------------------------------------------
# Specify what happens besides branching under 'observe'
def observe(agent_memory, qureg, reverse=False):
    assert len(agent_memory) >= len(qureg), 'Invalid observe. Observed system is larger than what memory ' \
                                            'of the agent can hold.'
    if reverse:
        get_inverse(Add) | (qureg, agent_memory)
    else:
        Add | (qureg, agent_memory)


# ------------------4. Inference procedures ----------------------------------------------------------------------------
flatten = lambda target_list: list(chain.from_iterable(target_list))
to_flat_unique = lambda target_list: list(set(flatten(target_list)))


def forward_inference(protocol, subsys_x, t_x, subsys_y, t_y, silent=True):
    # Set up the engine and resource qubits
    qtree = QuantumTree(QuantumSystem(protocol.get_requirements(), silent))

    qsys = qtree.branches[0]
    n_mem_options = 2 ** len(qsys[subsys_x])  # number of possible subsys_x states

    # Check that the given times exist in the protocol
    assert t_x in protocol.get_times() and t_y in protocol.get_times(), 'Times t_x = %d, t_y = %d ' \
                                                                        'do not match protocol times' % (
                                                                            t_x, t_y)

    # Prepare the branching structure up to the inference start point t_x
    protocol.run_manual(qtree,
                        t_end=t_x,
                        silent=silent)

    # Build up the mapping from input (subsys_x) states to output (subsys_y) states
    if not silent: print('XXXXXXXXX Reasoning starts XXXXXXXXXX')
    mapping = {}
    for branch in qtree:  # every branch is a `QuantumSystem` instance
        if not silent: print('XXXXXXXXXXXXXXXXXXXX')
        # get the state of subsys_x at t_x for this branch ('memory_state')
        wavefunc = branch.get_wavefunction()
        memory_state = []
        for n in range(n_mem_options):
            output_n_subspace = branch.subspace_of_state_n(subsys_x, n)
            if overlaps_with_subspace(wavefunc, output_n_subspace):
                memory_state.append(n)
        assert len(memory_state) == 1, 'More than one possible memory state. ' \
                                       'Seems like there is a bug in your implementation'
        memory_in = memory_state[0]
        if not silent: print('MEMORY STATE OF {0} IS:'.format(subsys_x), memory_in)

        # Run protocol from t_x to t_y on a `QuantumTree` with root `branch`
        subtree = QuantumTree(branch)
        protocol.run_manual(subtree,
                            t_start=t_x + 1,
                            t_end=t_y,
                            silent=silent)

        # compute the possible states a the end
        possible_states = to_flat_unique(get_possible_outcomes(subtree, subsys_y))
        if not silent: print('POSSIBLE STATES OF {0} ARE:'.format(subsys_y), possible_states)

        # map memory state i of subsys_x to list of compatible output states for subsys_y
        try:
            mapping[memory_in] += possible_states  # if possible states from other branches already exist, simply append
        except:
            mapping[memory_in] = possible_states
        mapping[memory_in] = list(set(mapping[memory_in]))  # Remove duplicates (e.g. [0,0,1] -> [0,1])

        # Reset all qubits in qsys to state 0
        reset(subtree, silent)
        reset(branch, silent)

    # Reset the prepared branching structure for deallocation
    reset(qtree, silent)
    reset(qsys, silent)

    return InferenceTable(subsys_x, t_x,
                          subsys_y, t_y,
                          mapping)


def backward_inference(protocol, subsys_x, t_x, subsys_y, t_y, silent=True):
    """
    Backward inference answers the question:
    Given a measurement result of 'subsys_y' at time `t_y` of the protocol,
    what can I say about the result an Agent would have received had she done
    a measurement of 'subsys_x' at time `t_x` of the protocol (t_x < t_y)?
    """
    # Perform the forward inference and get its inference table
    forward_mapping = forward_inference(protocol, subsys_x, t_x, subsys_y, t_y, silent)['table']
    if not silent:
        print(forward_mapping)

    # Reverse the infernce table by classical logic
    output_vals = list(set(chain(*forward_mapping.values())))
    backward_mapping = {v: [] for v in output_vals}

    for inpt, possible_outputs in forward_mapping.items():
        for output in possible_outputs:
            backward_mapping[output] += [inpt]

    return InferenceTable(subsys_y, t_y,
                          subsys_x, t_x,
                          backward_mapping)
