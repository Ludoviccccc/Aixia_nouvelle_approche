import random 
import copy

class MutationInstructions:
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
    def __init__(self,
            num_mutations:int=1,
            max_cycle:int=60,
            min_address:int = 0,
            max_address:int=19,
            max_instructions:int=None,
    ):
        self.num_mutations = num_mutations
        self.max_cycle = max_cycle
        self.min_address = min_address
        self.max_address = max_address
        self.max_instructions = max_instructions


    def __call__(self,instructions,
        ):
        # Create a deep copy to avoid modifying the original
        mutated = copy.deepcopy(instructions)
        instruction_types = ['read', 'write']
        
        # Get all possible cycles (0 to max_cycle)
        used_cycles = set(mutated.keys())
        max_used_cycle = max(used_cycles)
        min_used_cycle = min(used_cycles)
        min_used_cycle_set = set([min_used_cycle])
        max_used_cycle_set = set([max_used_cycle])
        #all_cycles = set(range(0, self.max_cycle + 1))
        all_cycles = set(range(min_used_cycle, max_used_cycle + 1))
        available_cycles = list(all_cycles - used_cycles)

        
        for _ in range(self.num_mutations):
            if len(mutated)>2:
                mutation_type = random.choice(['add', 'delete', 'modify'])
            else:
                mutation_type = random.choice(['add'])
            
            if mutation_type == 'add' and available_cycles:
                # Add a new instruction at an available cycle
                new_cycle = random.choice(available_cycles)
                instr_type = random.choice(instruction_types)
                address = random.randint(self.min_address, self.max_address)
                mutated[new_cycle] = (instr_type, address)
                available_cycles.remove(new_cycle)
                
            elif mutation_type == 'delete' and mutated:
                # Delete a random existing instruction
                cycle_to_delete = random.choice(list(set(mutated.keys())-min_used_cycle_set - max_used_cycle_set))
                del mutated[cycle_to_delete]
                available_cycles.append(cycle_to_delete)
                
            elif mutation_type == 'modify' and mutated:
                # Modify an existing instruction
                cycle_to_modify = random.choice(list(set(mutated.keys())-min_used_cycle_set - max_used_cycle_set))
                old_type, old_address = mutated[cycle_to_modify]
                
                # Choose what to modify: type, address, or both
                modify_choice = random.choice(['type', 'address', 'both'])
                
                if modify_choice == 'type':
                    # Change instruction type only
                    new_type = 'write' if old_type == 'read' else 'read'
                    mutated[cycle_to_modify] = (new_type, old_address)
                elif modify_choice == 'address':
                    # Change address only
                    new_address = random.randint(self.min_address, self.max_address)
                    mutated[cycle_to_modify] = (old_type, new_address)
                else:
                    # Change both type and address
                    new_type = 'write' if old_type == 'read' else 'read'
                    new_address = random.randint(self.min_address, self.max_address)
                    mutated[cycle_to_modify] = (new_type, new_address)
        if len(mutated)>self.max_instructions:
            to_del = random.sample(list(mutated.keys()),len(mutated)- self.max_instructions)
            for k in to_del:
                del mutated[k]
        return mutated
