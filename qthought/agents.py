#   Basic library for implementing Agent systems in ProjectQ
#   Date:   8 Dec 2018
#   Author: Simon Mathis
#   Contact: mathissi@student.ethz.ch
from math import ceil
from numpy import log2
from warnings import warn

from projectq.meta import Control
from projectq.ops import *

from .utils.arithmeticgates import Add
from .utils.general import int_to_bit_array, readout, state_i_to_1


# ----------------------------------------------------------------------------------------------------------------------
class InferenceTable:
    """
    Class to store inference tables for agents.
    """
    def __init__(self, input_var: str, input_time: int, output_var: str, output_time: int, tbl: dict):
        """
        Creates an InferenceTable object

        :param input_var:  str, Name of the considered input variable/subsystem that is observed
        :param input_time: int, Time at which the observation of the input variable happens in the protocol
        :param output_var:  str, Name of the considered output variable/subsytem that is observed
        :param output_time: int, Time at which the observation of the output variable happens in the protocol
        :param tbl: dict, The dictionary containing for each possible value of the input_var (key) a list of
                          possible outcomes of the output_var (value)
        """

        self.input = input_var
        self.input_time = input_time
        self.output = output_var
        self.output_time = output_time
        self.tbl = tbl

        # Parse the inputs
        self.parse()

    def __getitem__(self, index: str):
        if index == 'input':
            return self.input, self.input_time
        elif index == 'output':
            return self.output, self.output_time
        elif index == 'table':
            return self.tbl
        else:
            assert False, 'inference_table object has no attribute %s. Allowed values: input, output, table' % index

    def __str__(self) -> str:
        full_str = 'In:({0}:t{1})'.format(self.input, self.input_time).ljust(22) + '|' + \
                   '  Out: ({0}:t{1})'.format(self.output, self.output_time)
        full_str += '\n' + '-' * (len(full_str) + 7)
        for key, val in self.tbl.items():
            full_str += '\n \t {0}'.format(key).ljust(15) + '| \t ' + str(val)

        return full_str.expandtabs(10)

    def __len__(self) -> int:
        """Returns the length of the dict belonging to the inference table"""
        return len(self.tbl)

    def __repr__(self) -> str:
        """
        Give complete information on inference table without print statement in
        command-line
        """
        return self.__str__()

    def parse(self):
        for key, value in self.tbl.items():
            assert isinstance(key, int), "Invalid inference table. Use keys in the format (int) 0,1,2, ... " \
                                         "and make sure the number of provided keys matches the dimension of " \
                                         "the memory system."
            assert isinstance(value, list), "Invalid inference table value. Can only predict integer values " \
                                            "corresponding to comp. basis states of pred. system"
            assert isinstance(value[0], int), "Please provide states as int corresponding to your respective" \
                                              " bitstring."


# ----------------------------------------------------------------------------------------------------------------------
class Agent:
    """
    Class to implement agents in projectq. An Agent consists of

    (1) A memory qureg (to store the memory as a state)
    (2) A prediction qureg (to store the prediction as a state)
    (3) An inference system (used to make an inference from the memory to the prediction system
    with the help of an inference table and the inference mechanism described in XXX.
    """

    def __init__(self, eng, n_memory:int, n_pred:int, inference_table=None, no_prediction_state=0):
        """
        :param eng: ProjectQ.engine, engine to which the qubits of Agent are allocated
        :param n_memory: int, number of memory qubits of the Agent
        :param n_pred:   int, number of prediction qubits of the Agent
        :param inference_table: precomputed inference table
        :type  inference_table: InferenceTable
        """
        assert n_memory >= n_pred, 'Cannot make more different predictions than observed memory states'

        self.n_inference = 2 ** n_memory * n_pred
        n_inference = self.n_inference
        self.memory_ = eng.allocate_qureg(n_memory)
        self.pred_ = eng.allocate_qureg(n_pred)
        self.inference_sys_ = eng.allocate_qureg(n_inference)
        self.inference_made_ = False
        self.inf_sys_prepared_ = False
        self.eng_ = eng
        self.n_qubits = n_memory + n_pred + n_inference

        # Initialize empty inference table with zeros and generate
        # inference_dict for easier access of inference system:
        self.inference_table_ = {}
        self.inference_dict_ = {}
        for i in range(2 ** n_memory):
            self.inference_table_[i] = no_prediction_state
            # inference_dict_[i] returns the qubits needed for
            #  prediction belonging to memory state i
            self.inference_dict_[i] = self.inference_sys_[i * n_pred:(i + 1) * n_pred]

        if inference_table is not None:
            self.set_inference_table(inference_table)

    @classmethod
    def from_dim(cls, eng, memory_dim:int, pred_dim:int, inference_table=None):
        '''
        Used to initialize an Agent via giving the dimensions of the memory and prediction system.
        :param eng: ProjectQ.engine, engine to which the qubits of Agent are allocated
        :param memory_dim: int, dimension of memory system of Agent
        :param pred_dim:   int, dimension of predictions of Agent (d-1 predictions + '?' possible)
        :param inference_table: dict, precomputed inference table
        '''
        n_memory = ceil(log2(memory_dim))
        n_pred = ceil(log2(pred_dim))

        return cls(eng, n_memory, n_pred, inference_table)

    def __len__(self):
        """Returns the number of qubits of the quantum system"""
        return self.n_qubits

    def __getitem__(self, index: int):
        """ Method to access the Agent qubits.

        :int index:
        :return:
        """
        full_sys = self.memory_ + self.pred_ + self.inference_sys_
        return full_sys[index]

    def memory(self):
        """Getter for the memory register of the agent"""
        return self.memory_

    def prediction(self):
        """Getter for the prediction register of the agent"""
        return self.pred_

    def inference_sys(self):
        """Getter for the inference system register of the agent"""
        return self.inference_sys_

    def all(self, with_inf_sys=True):
        """Getter for all registers that make up the agent combined."""
        if with_inf_sys:
            return self.memory() + self.prediction() + self.inference_sys()
        else:
            return self.memory() + self.prediction()

    def set_inference_table(self, inference_table, no_prediction_state: int = 0):
        """ Initializes the agents inference table with the given inference table.

        :inference_table object inference_table: The inference system of the Agent
        :int no_prediction_state: The state corresponding to the agents statement 'I do not know'
        :return:
        """
        assert len(inference_table) <= 2**len(self.memory_), \
            'Your inference table is too long and cannot be stored in the requested no. of qubits. ' \
            'Make your inference table smaller or raise the number of memory qubits n_memory of the Agent. '
        inference_table.parse()

        for key, predictions in inference_table.tbl.items():
            if len(predictions) > 1:
                self.inference_table_[key] = no_prediction_state
            else:
                assert predictions[0] < 2 ** len(self.pred_), 'Inference value is higher than the provided ' \
                                                              'number of prediction qubits can store.'
                self.inference_table_[key] = predictions[0]

    def get_inference_table(self):
        """Getter for the agents inference table."""
        return self.inference_table_

    def prep_inference(self):
        """Loads the agents inference table into the inference system."""
        for key, qureg in self.inference_dict_.items():
            pred_value = self.inference_table_[key]
            n_pred = len(qureg)

            to_flip = int_to_bit_array(pred_value, n_pred)[::-1]
            for ix, flip in enumerate(to_flip):
                if flip:
                    X | qureg[ix]
        self.inf_sys_prepared_ = True

    def make_inference(self, reverse=False):
        """Calls the inference operation, i.e.
        calls the circuit that copies the prediction state belonging to the state i of the memory into the
        prediction register."""
        if not self.inf_sys_prepared_:
            warn('make_inference called without setting an inference_table')

        for key, Ti in self.inference_dict_.items():
            # Step 1: Transform memory state corresponding to input i into 'All(1)' state
            i = int(key)
            state_i_to_1(i, self.memory_)
            with Control(self.eng_, self.memory_):
                # Step 2: Controlled on the memory state being in 'All(1)' state
                #         and Ti being true, copy the i-th prediction in the prediction register
                if reverse:
                    get_inverse(Add) | (Ti, self.pred_)
                else:
                    Add | (Ti, self.pred_)
            # Step 3: Transform memory state back from All(1) to i
            state_i_to_1(i, self.memory_)

        self.inference_made_ = True

    def readout(self):
        """Reads out the memory and prediction registers and returns the results"""
        # TODO: Update as this produces issues
        obs = readout(self.memory_)
        pred = readout(self.pred_)
        return obs, pred