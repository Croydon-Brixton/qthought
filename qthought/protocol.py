from copy import deepcopy
from .requirements import Requirements
from .quantumsystem import QuantumSystem


# ----------------------------------------------------------------------------------------------------------------------
class ProtocolStep:
    """
    Protocol step class for filling a protocol.
    A protocol instance has three attributes:

    Attributes:
        domain (list): required resources (qubits, quregs, agents) in the protocol step
        descr (str): describes the step in words
        action (func): performs the action of the step.
    """

    def __init__(self, domain:dict, descr:str, time:int, action):
        '''
        domain : list, specifies the domain (all of the requirements) for the specific step
        descr  : str,  describes the step in words
        time   : int,  time of the step in the protocol. To be set maually.
        action : func, performs the action of the step
        '''
        assert isinstance(domain, dict), "Please provide your domain as a dict of the form " \
                                         "{'Ressource': ['Name1', 'Name2']}. " \
                                         "E.g. {'Qubit' : ['s']}"
        assert isinstance(descr, str), 'Please provide the description as a str object.'

        self.domain = domain
        self.descr = descr
        self.time = time
        self.action = action

    def __str__(self):
        return self.descr + '(t:' + str(self.time) + ')'

    def __add__(self, other):
        """Addition of two protocol steps automatically assembles a protocol"""
        assert isinstance(other, ProtocolStep), 'Can only add a ProtocolStep to ProtocolStep. Not %s' + str(type(other))
        p = Protocol()
        p += self
        p += other
        return p

    def __radd__(self, other):
        if other == 0:
            return self
        elif isinstance(other, Protocol):
            p = Protocol()
            p.add_step(self)
            return p
        else:
            assert False, 'Not implemented yet'  # TODO

    def __repr__(self):
        full_str = 'ProtocolStep instance:\n'
        full_str += str(self)
        return full_str


# ----------------------------------------------------------------------------------------------------------------------
class Protocol:
    def __init__(self, silent=True):
        self.n_steps = 0
        self.steps = ()
        self.requires = Requirements()
        self.silent = silent

    def __len__(self):
        return self.n_steps

    def __str__(self):
        # Used to spell out the protocol in words
        full_str = ''
        for step in self.steps:
            full_str += 'Step %d: ' % step[0]
            full_str += str(step[1])
            full_str += '\n'
        full_str += '\n' + str(self.requires)
        return full_str

    def __repr__(self):
        """Outputs string description of protocol directly in console"""
        return self.__str__()

    def __iadd__(self, other):
        if isinstance(other, ProtocolStep):
            self.add_step(other)
        else:
            assert False, 'Currently only adding Protocol Steps is implemented'  #TODO
        return self

    # TODO: Define add for (protocol, protocol) and (protocol, protocol_step)
    def __add__(self, other):
        if other == 0:
            return self
        elif isinstance(other, ProtocolStep):
            self.add_step(other)
            return self  # for protocol step instance
        else:
            assert False, 'Currently not implemented yet'  # TODO

    def add_step(self, step):
        # Check whether step is a valid protocol_step object
        assert isinstance(step, ProtocolStep)
        # Get step id to enlist in protocol
        id = deepcopy(self.n_steps)

        # Add requirements of protocol step to full requirements of protocol
        self.requires.add(step.domain)

        # Add the new step to the protocoll with id
        self.steps += ((id, step),)

        self.n_steps += 1
        if not self.silent: print('Step %d added' % id)

    def get_requirements(self):
        return self.requires.get()

    def run(self, qsys, t_start = 0, t_end = 10000, silent=False):
        assert isinstance(qsys, QuantumSystem), 'Please provide a QuantumSystem to run the protocol on.'

        for step in self.steps:
            if t_start <= step[1].time <= t_end:
                if silent and step[1].descr == 'Print state':
                    continue
                else:
                    step[1].action(qsys)

                if not silent:
                    print(step[0], step[1].descr, 't:' + str(step[1].time))
                    print('State:')
                    qsys.print_wavefunction()
            else:
                continue

    def run_manual(self, qsys, t_start = 0, t_end = 10000, silent=False):
        for step in self.steps:
            if t_start <= step[1].time <= t_end:
                if silent and step[1].descr == 'Print state':
                    continue
                else:
                    step[1].action(qsys)

                if not silent:
                    print('='*15)
                    print(step[0], step[1].descr, 't:' + str(step[1].time))
                    print(qsys)
            else:
                continue

    def get_times(self):
        times = []
        for step in self.steps:
            times += [step[1].time]
        return times





