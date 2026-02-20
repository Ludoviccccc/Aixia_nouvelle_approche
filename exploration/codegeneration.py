import random
import copy
import sys
sys.path.append('../')
from exploration.match_virtual_physical_addresses import Address2Loc


class Address_Management:
    def __init__(self,
            nun_instructions=None,
            max_cycle=60,
            min_address = 0,
            max_address = 19,
            num_addr = 40,
            num_banks = 4,
            num_instructions=10,
            ):
        self.num_addr = num_addr
        self.min_address = min_address
        self.max_address = max_address
        self.max_cycle = max_cycle
        self.num_instructions = num_instructions
        self.address2loc = Address2Loc(self.num_addr,num_banks,min_address,max_address)
    def generate_instruction_sequence(self):
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
            self.num_instructions = random.randint(1, 20)  # Random number of instructions
            # Ensure we don't generate more instructions than available cycles
        num_instructions = min(self.num_instructions, self.max_cycle + 1)
        
        instructions = {}
        instructions_adjoint = {}
        instruction_types = ['read', 'write']
        
        # Generate unique cycle numbers
        cycles = random.sample(range(0, self.max_cycle + 1), num_instructions)
        
        for cycle in cycles:
            bank,row = random.choice(self.address2loc.possible_rows)
            address = self.address2loc.location2rand_addr(bank,row)
            instr_type = random.choice(instruction_types)
            instructions[cycle] = (instr_type, address)
            instructions_adjoint[cycle] = (instr_type, (bank,row))
        
        return dict(sorted(instructions.items())),dict(sorted(instructions_adjoint.items()))
