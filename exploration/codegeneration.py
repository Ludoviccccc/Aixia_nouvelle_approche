import random
import copy
import sys
sys.path.append('../')
from exploration.match_virtual_physical_addresses import Address2Loc


class Address_Management:
    def __init__(self,
            max_cycle=60,
            min_address = 0,
            max_address = 19,
            num_addr = 40,
            num_banks = 4,
            num_instructions=None,
            max_instructions=5,
            ):
        self.num_addr = num_addr
        self.min_address = min_address
        self.max_address = max_address
        self.max_cycle = max_cycle
        self.num_instructions = num_instructions
        self.max_instructions = max_instructions
        self.address2loc = Address2Loc(self.num_addr,num_banks,min_address,max_address)
    def generate_instruction_sequence(self,
            target_bank,target_row):
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
            # Ensure we don't generate more instructions than available cycles
        num_instructions = min(num_instructions, self.max_cycle + 1)
        
        instructions = {}
        instructions_adjoint = {}
        instruction_types = ['read', 'write']
        
        # Generate unique cycle numbers
        cycles = sorted(random.sample(range(0, self.max_cycle + 1), num_instructions))
        
        for i,cycle in enumerate(cycles):
            if i!=0 and i!=len(cycles)-1:
                bank,row = random.choice(self.address2loc.available_rows)
            else:
                bank = target_bank
                row = target_row
            address = self.address2loc.location2rand_addr(bank,row)
            instr_type = random.choice(instruction_types)
            #instructions[cycle] = (instr_type, address)
            instructions[cycle] = (instr_type, address,i)
            instructions_adjoint[cycle] = (instr_type, (bank,row))
        
        return dict(sorted(instructions.items())),dict(sorted(instructions_adjoint.items()))
