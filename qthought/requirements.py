class Requirements:
    """Class for handling the requirements of a protocol"""

    def __init__(self):
        self.req_dict = {}

    @staticmethod
    def parse(new_req:dict):
        """
        Parses new requirement and throws an assertion if it is invalid.
        :param new_req: dict
        :return:
        """
        allowed_keys = ['Qubit', 'Qureg', 'AgentMemory', 'Agent']
        for key, value in new_req.items():
            prefix = key.split('(')[0]
            assert prefix in allowed_keys, 'Allowed Keys: Qubit, Qureg(n), AgentMemory(n), Agent(n,m)' \
                                           ' not ' + str(key)
            assert isinstance(value, (list, str)), "Please provide the values as a list of strings (e.g. " \
                                                   "['Alice', 'Bob']) not: " + str(value)
            if prefix == 'Qubit':
                assert key == prefix

            elif prefix == 'Qureg':
                size = key.split('(')[1].split(')')[0]
                assert int(size), 'Invalid size ' + size

            elif prefix == 'AgentMemory':
                size = key.split('(')[1].split(')')[0]
                assert int(size), 'Invalid size ' + size

            elif prefix == 'Agent':
                mem_size = key.split('(')[1].split(',')[0]
                pred_size = key.split('(')[1].split(',')[1].split(')')[0]
                assert int(mem_size), 'Invalid size ' + mem_size
                assert int(pred_size), 'Invalid size' + pred_size

    def add(self, new_req:dict):
        """
        new_req : dict, dictionary with new requirements to add
        """
        self.parse(new_req)

        for key in new_req.keys():
            requirements_to_add = new_req[key]
            if not isinstance(requirements_to_add, list):
                requirements_to_add = [requirements_to_add]

            if key not in self.req_dict.keys():
                self.req_dict[key] = requirements_to_add

            else:
                self.req_dict[key] = list(set().union(self.req_dict[key], requirements_to_add))

    def __iadd__(self, new_req:dict):
        self.add(new_req)
        return self

    def get(self):
        self.consolidate()
        return self.req_dict

    def consolidate(self):
        # NOTE: Currently only works for one size of AGENT_MEMORY in system
        # TODO: Generalize to arbitrary AgentMemory sizes
        """
        Gets rid of unnecessary AGENT_MEMORY requirements if a full Agent is in the
        list of requirements
        :return:
        """
        # Check if there are AGENT_MEMORY and AGENT keys:
        mem_key = None
        agent_key = None
        mem_names = []
        agent_names = []

        for key in self.req_dict.keys():
            if key.split('(')[0] == 'AgentMemory':
                mem_names += self.req_dict[key]
                mem_key = key
            if key.split('(')[0] == 'Agent':
                agent_names += self.req_dict[key]
                agent_key = key

        if mem_key is not None and agent_key is not None:
            new_names = []
            for name in mem_names:
                if name not in agent_names:
                    new_names += [name]

            self.req_dict[mem_key] = new_names
            if new_names == []:
                self.req_dict.pop(mem_key)

    def __str__(self):
        """Outputs the requirements as a string"""
        self.consolidate()
        full_str = 'Requirements: \n'
        full_str += '-' * 30 + '\n'
        for key, value in self.req_dict.items():
            newline = key.ljust(18) + str(value) + '\n'
            full_str += newline
        return full_str

    def __repr__(self):
        """Outputs string description directly in console"""
        return self.__str__()


