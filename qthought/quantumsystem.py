#   Basic utilities library for Project Q
#   Author: Simon Mathis
#   Contact: mathissi@student.ethz.ch
#   This file implements a QuantumSystem class which bundles together different quantum objects
#   (e.g. qubits, agents, ...) to a convenient object which supports indexing and several other
#   methods.

import warnings
import  numpy as np

from projectq import MainEngine
from projectq.ops import X, Measure, All

from .utils.subspace import all_basis_vectors, outer_subspace_product, renormalize, filter_subspace, \
    overlaps_with_subspace
from .utils.general import print_state, access_state, int_to_bitstring, readout, cround

from .agents import Agent
from .requirements import Requirements
from termcolor import colored


def get_agent_dim(string):
    """
    Parses a string such as AGENT(3,5) for the dimensions [3, 5]
    :str string:
    :list:
    """
    string_list = string[1:-1].split(',')
    return [int(i) for i in string_list]


class QuantumSystem:
    """A class container to combine all required objects for quantum thought experiments such as the Frauchinger-Renner
    paradox.

    Note:
    Internal representation of the state: LSB - MSB
    i.e.   QuantumSystem['all'][0] ... LSB
           QuantumSystem['all'][-1]... MSB

    Print convention: MSB - LSB
    """

    def __init__(self, requirements: dict, silent=False, colored_output=True):
        if isinstance(requirements, Requirements): # Enables usage of both: dict and Requirement for `requirements`
            requirements = requirements.get()
        self.reqs_ = requirements
        self.eng_ = MainEngine()
        self.res_ = {} # Available resources in the `QuantumSystem`
        self.subsys_order_ = []  # order as returned by self.entire_sys() or self['all'] methods
        self.subsys_len = []
        self.n_qubits_ = 0
        self.colored_output = colored_output

        eng = self.eng_
        resources = self.res_

        for req in requirements:
            codename = req.split('(')[0]
            if codename == 'Qubit':
                for qubit_name in requirements[req]:
                    resources[qubit_name] = eng.allocate_qubit()
                    if not silent: print('Require ' + req + ' ' + qubit_name)
                    self.subsys_order_ += [qubit_name]
                    self.subsys_len += [1]
                    self.n_qubits_ += 1

            if codename == 'AgentMemory':
                n_memory = int(req.split('(')[1].split(')')[0])
                for memory_name in requirements[req]:
                    resources[memory_name + '_memory'] = eng.allocate_qureg(n_memory)
                    if not silent: print('Require ' + req + ' ' + memory_name)
                    self.subsys_order_ += [memory_name + '_memory']
                    self.subsys_len += [n_memory]
                    self.n_qubits_ += n_memory

            if codename == 'Agent':
                for agent_name in requirements[req]:
                    n_memory, n_pred = get_agent_dim(req[5:])
                    resources[agent_name] = Agent(eng, n_memory, n_pred, inference_table=None)
                    resources[agent_name + '_memory'] = resources[agent_name].memory()
                    resources[agent_name + '_prediction'] = resources[agent_name].prediction()
                    if not silent: print('Require ' + req + ' ' + agent_name)
                    self.subsys_order_ += [agent_name]
                    self.subsys_len += [len(resources[agent_name])]
                    self.n_qubits_ += len(resources[agent_name])

            if codename == 'Qureg':
                for qureg_name in requirements[req]:
                    reg_len = int(req[6:-1])
                    resources[qureg_name] = eng.allocate_qureg(reg_len)
                    if not silent: print('Require Qureg(%d)' % reg_len + qureg_name)
                    self.subsys_order_ += [qureg_name]
                    self.subsys_len += [reg_len]
                    self.n_qubits_ += reg_len

    @property
    def n_qubits(self):
        """ Returns the number of qubits in the QuantumSystem."""
        return self.n_qubits_

    @property
    def requirements(self):
        """ Returns the requirements used to build the QuantumSystem"""
        return self.reqs_

    @property
    def engine(self):
        """ Returns projectq engine on which the QuantumSystem is run"""
        return self.eng_

    @property
    def subsystems(self):
        """ Returns a list of the subsystems in the given QuantumSystem in the indexing order
        (Note: This is reversed from the printing order)"""
        return self.subsys_order_

    def __copy__(self):
        """ Returns a copy of the QuantumSystem"""
        qsys_copy = QuantumSystem(self.reqs_)
        qsys_copy.set_wavefunction(self.get_wavefunction())
        return qsys_copy

    def __len__(self):
        """Returns the number of qubits in the QuantumSystem."""
        return self.n_qubits

    def __str__(self):
        """Returns the most important attributes of the QuantumSystem as string."""
        full_str = 'QuantumSystem object: \n'
        full_str += 'Nqubits:'.ljust(14) + '%d \n' % len(self)
        if self.colored_output:
            colored_subsys = ''
            for subsys in self.subsystems[::-1]:
                colored_subsys += self._color_subsys(subsys) + ' '
            full_str += 'Print order:'.ljust(14) + colored_subsys + '\n'
            full_str += 'Wavefunction: \n'
            full_str += self.print_wavefunction(to_output=True)
        else:
            full_str += 'Print order:'.ljust(14) + str(self.subsystems[::-1]) + '\n'
            full_str += 'Wavefunction: \n'
            self['eng'].flush()
            full_str += print_state(self['eng'], to_output=True)
        return full_str

    def __repr__(self):
        """Return QuantumSystem string description to output for interactive programming."""
        return self.__str__()

    def __getitem__(self, index: str):
        """Method for accessing the QuantumSystem engine and ressources"""
        if index == 'eng':
            return self.eng_
        elif index == 'all':
            return self.entire_sys()
        else:
            assert index in self.res_, 'Your quantum system has no subsystem %s' % index
            return self.res_[index]

    def get_position(self, index: str):
        """Returns the array indices of the position of self[index]"""
        obj = self[index]
        obj_length = len(obj)
        obj = obj[0]
        all_objs = self['all']

        for i, other_obj in enumerate(all_objs):
            if obj is other_obj:
                return [j for j in range(i, i + obj_length)]

        assert False, 'Error: Position not found'

    def get_wavefunction(self):
        """Returns the wave function of the quantum system"""
        self['eng'].flush()
        return access_state(self['eng'])

    def _color_key(self, key, colors=[None, 'red', 'blue', 'green', 'magenta']):
        colored_key = ''

        # Set the possible colors and their order
        colors = colors

        # Flip key to get internal ordering. Flip subsystems to get print-ordering
        internal_key = key[::-1]
        subsystems = self.subsystems[::-1]

        # Iterate over the subsystems and color them differently in the order specified in `colors`
        for i, subsystem in enumerate(subsystems):
            position = self.get_position(subsystem)
            start_pos = min(position)
            end_pos = max(position) + 1
            subsystem_internal_state = internal_key[start_pos:end_pos]  # note this is in internal order
            colored_key += colored(subsystem_internal_state[::-1], colors[i % len(colors)])  # flip to get print order
        return colored_key

    def _color_subsys(self, subsys, colors=[None, 'red', 'blue', 'green', 'magenta']):
        assert subsys in self.subsystems, 'Your QuantumSystem has no subsystem `{0}`'.format(subsys)
        subsys_index = self.subsystems[::-1].index(subsys)
        return colored(subsys, colors[subsys_index % len(colors)])

    def print_wavefunction(self, to_output=False):
        """Prints wave function of the quantum system to the console"""
        self['eng'].flush()
        state = access_state(self['eng'])

        output_string = ''
        for key, value in zip(state.keys(), state.values()):
            if self.colored_output:
                key = self._color_key(key)
            if value != 0:
                if any(output_string):
                    output_string += ' + ' + str(cround(value)) + '|' + key + '>'
                else:
                    output_string += str(cround(value)) + '|' + key + '>'
        if to_output:
            return output_string
        else:
            print(output_string)

    def set_wavefunction(self, wf, silent=False):
        """Sets the quantum system to a custom wavefunction."""
        # wavefunction contains 2^n values for n qubits
        # TODO: Write a simple function that embeds a smaller dict into the full wf dict to get rid of this assertion
        assert len(wf) == (1 << len(self)), 'Please provide all possible states, even if they have 0 amplitude.'
        wf_norm = renormalize(wf)

        if wf_norm is not None:
            eng = self['eng']
            eng.flush()
            eng.backend.set_wavefunction(list(wf_norm.values()), self['all'])
            eng.flush()
            if not silent: print('Wavefunction set to custom state.')

        else:
            assert False, 'Invalid wavefunction.'

    def entire_sys(self):
        """Returns an array with all qubits in the QuantumSystem
        Ordering: LSB ([0]) - MSB ([-1])"""
        entire_sys = []
        for subsys in self.subsystems:
            if type(self.res_[subsys]) is Agent:
                entire_sys += self.res_[subsys].all()
            else:
                entire_sys += self.res_[subsys]

        return entire_sys

    def reset(self, silent=False): #TODO: NOTE that projectQ seems to have a bug with qubit deallocation (Measure, tag)
        """ Resets all qubits of the QuantumSystem to state 0.
        """

        All(Measure) | self['all']
        self['eng'].flush()
        for qbit in self['all']:
            if readout([qbit]) == 1:
                X | qbit
        All(Measure) | self['all']
        if not silent: print('Quantum system reset to: ' + readout(self['all'], as_type='str'))

    def subspace_of_state_n(self, subsys_x, n):
        """
        Constructs the subspace in which subsys_x is in state n (in computational basis)
        """
        subsys_x_position = self.get_position(subsys_x)
        post_len = subsys_x_position[0]
        x_len = len(subsys_x_position)
        pre_len = len(self) - post_len - x_len

        subspace = outer_subspace_product(all_basis_vectors(pre_len), [int_to_bitstring(n, desired_len=x_len)])
        subspace = outer_subspace_product(subspace, all_basis_vectors(post_len))

        return subspace

    def project_to_subspace(self, subspace: list):
        """Project the system to a subspace specified by a list of strings"""
        wavefunc = self.get_wavefunction()
        proj_wf_unnorm = filter_subspace(wavefunc, subspace)
        proj_wf_norm = renormalize(proj_wf_unnorm)

        if proj_wf_norm is not None:
            eng = self['eng']
            eng.flush()
            eng.backend.set_wavefunction(list(proj_wf_norm.values()), self['all'])
            eng.flush()
            return proj_wf_norm

        warnings.warn('No overlap. No projection was performed.')
        print('No overlap')
        return 0

    def readout(self, subsys:str, order = 'internal') -> str:
        assert order in ['internal', 'print'], '`order` must be one of [`internal`, `print`]'
        assert subsys in self.res_, 'Your QuantumSystem has no subsystem {0}'.format(subsys)

        possible_states = []    #TODO: Make the below more efficient by using the ProjectQ native readout.
        wavefunc = self.get_wavefunction()
        for j in range(2 ** len(self[subsys])):
            output_j_subspace = self.subspace_of_state_n(subsys, j)
            if overlaps_with_subspace(wavefunc, output_j_subspace):
                possible_states += [np.binary_repr(j, len(self[subsys]))]
        assert len(possible_states) == 1, 'Subsystem is not in pure state. It has not been measured yet'
        if order == 'internal':
            return possible_states[0]
        else:
            return possible_states[0][::-1]