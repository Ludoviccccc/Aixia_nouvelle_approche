import random
import copy
import sys
sys.path.append('../')
#from exploration.match_virtual_physical_addresses import Address2Loc


class Address_Management:
    def __init__(self,
            max_cycle=60,
            min_address_core_0 = 0,
            max_address_core_0 = 19,
            min_address_core_1 = 0,
            max_address_core_1 = 19,
            num_instructions=None,
            max_instructions=5,
            ):
        self.min_address_core_0 = min_address_core_0
        self.max_address_core_0 = max_address_core_0
        self.min_address_core_1 = min_address_core_1
        self.max_address_core_1 = max_address_core_1
        self.max_cycle = max_cycle
        self.num_instructions = num_instructions
        self.max_instructions = max_instructions
    def generate_instruction_sequence(self,min_address,max_address,address_x=None):
        """
        Generate a random dictionary of assembly instructions.
        
        Args:
            num_instructions: Number of instructions to generate (if None, random between 1-20)
            max_cycle: Maximum cycle number (default: 60)
            max_address: Maximum memory address (default: 19)
        
        Returns:
            Dictionary with format {cycle: (type, address)}
        """
        if self.num_instructions is None:
            num_instructions = random.randint(2, self.max_instructions)  # Random number of instructions
        else:
            num_instructions = self.num_instructions
        # Ensure we don't generate more instructions than available cycles
        num_instructions = min(num_instructions, self.max_cycle + 1)
        
        instructions = {}
        instructions_adjoint = {}
        instruction_types = ['read', 'write']
        
        # Generate unique cycle numbers
        cycles = sorted(random.sample(range(0, self.max_cycle + 1), num_instructions))
        
        for i,cycle in enumerate(cycles):
            if address_x:
                if i==0 or i==num_instructions-1:
                    address = address_x
                else:
                    address = random.randint(min_address,max_address)
            else:
                address = random.randint(min_address,max_address)
            instr_type = random.choice(instruction_types)
            #instructions[cycle] = (instr_type, address)
            instructions[cycle] = (instr_type, address)
        return dict(sorted(instructions.items()))
    def __call__(self,address_x):
        output = {}
        output['core0'] = self.generate_instruction_sequence(self.min_address_core_0,self.max_address_core_0,address_x=address_x)
        output['core1'] = self.generate_instruction_sequence(self.min_address_core_1,self.max_address_core_1,address_x=address_x)
        return output
