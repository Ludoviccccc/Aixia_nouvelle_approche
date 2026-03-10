import random 
import copy
import sys
sys.path.append('../../')
from exploration.codegeneration import Address_Management
def mutate_instruction_sequence(instructions, 
                                    addr_management:Address_Management,
                                    num_mutations=1,
                                    max_cycle=60,
                                    num_instructions=None,
                                    ):
    """
    Mutate an instruction sequence by adding, deleting, or modifying instructions.
    
    Args:
        instructions: Original instruction dictionary
        num_mutations: Number of mutations to perform
        max_cycle: Maximum cycle number (default: 60)
        max_address: Maximum memory address (default: 19)
    
    Returns:
        New mutated dictionary
    """



    # Create a deep copy to avoid modifying the original
    mutated = copy.deepcopy(instructions)
    instruction_types = ['read', 'write']
    
    # Get all possible cycles (0 to max_cycle)
    all_cycles = set(range(0, max_cycle + 1))
    used_cycles = set(mutated.keys())
    available_cycles = list(all_cycles - used_cycles)
    
    for _ in range(num_mutations):
        if len(mutated)>1:
            mutation_type = random.choice(['add', 'delete', 'modify'])
        else:
            mutation_type = random.choice(['add', 'modify'])
        
        if mutation_type == 'add' and available_cycles:
            # Add a new instruction at an available cycle
            new_cycle = random.choice(available_cycles)
            instr_type = random.choice(instruction_types)
            new_bank,new_row = random.choice(addr_management.address2loc.available_rows)
            mutated[new_cycle] = (instr_type, new_row,new_bank)
            available_cycles.remove(new_cycle)
            
        elif mutation_type == 'delete' and mutated:
            # Delete a random existing instruction
            cycle_to_delete = random.choice(list(mutated.keys()))
            del mutated[cycle_to_delete]
            available_cycles.append(cycle_to_delete)
            
        elif mutation_type == 'modify' and mutated:
            # Modify an existing instruction
            cycle_to_modify = random.choice(list(mutated.keys()))
            old_type, (old_row,old_bank,id_old) = mutated[cycle_to_modify]
            
            # Choose what to modify: type, address, or both
            modify_choice = random.choice(['type', 'address', 'both'])
            
            if modify_choice == 'type':
                # Change instruction type only
                new_type = 'write' if old_type == 'read' else 'read'
                mutated[cycle_to_modify] = (new_type, (old_row,old_bank,id_old))
            elif modify_choice == 'address':
                # Change address only
                new_bank,new_row = random.choice(addr_management.address2loc.available_rows)
                #new_address = random.randint(min_address, max_address)
                mutated[cycle_to_modify] = (old_type, (new_row,new_bank,id_old))
            else:
                # Change both type and address
                new_type = 'write' if old_type == 'read' else 'read'
                new_bank,new_row = random.choice(addr_management.address2loc.available_rows)
                #new_address = random.randint(min_address, max_address)
                mutated[cycle_to_modify] = (new_type, (new_row,new_bank,id_old))
    if len(mutated)>num_instructions:
        to_del = random.sample(list(mutated.keys()),len(mutated)- num_instructions)
        for k in to_del:
            del mutated[k]
    return mutated

def mutate_paire_instructions(programs0,programs1,num_mutations, max_cycle=60, max_address=19,num_instructions=None):
    return mutate_instruction_sequence(programs0,num_mutations,max_cycle = max_cycle,max_address=max_address,num_instructions=num_instructions),mutate_instruction_sequence(programs1,num_mutations,max_cycle = max_cycle,max_address=max_address,num_instructions=num_instructions)
