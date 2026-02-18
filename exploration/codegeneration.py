import random
import copy

def generate_instruction_sequence(num_instructions=None, max_cycle=60, min_address=0,max_address=19):
    """
    Generate a random dictionary of assembly instructions.
    
    Args:
        num_instructions: Number of instructions to generate (if None, random between 1-20)
        max_cycle: Maximum cycle number (default: 60)
        max_address: Maximum memory address (default: 19)
    
    Returns:
        Dictionary with format {cycle: (type, address)}
    """
    if num_instructions is None:
        num_instructions = random.randint(1, 20)  # Random number of instructions
        # Ensure we don't generate more instructions than available cycles
    num_instructions = min(num_instructions, max_cycle + 1)
    
    instructions = {}
    instruction_types = ['read', 'write']
    
    # Generate unique cycle numbers
    cycles = random.sample(range(0, max_cycle + 1), num_instructions)
    
    for cycle in cycles:
        instr_type = random.choice(instruction_types)
        address = random.randint(min_address, max_address)
        instructions[cycle] = (instr_type, address)
    
    return dict(sorted(instructions.items()))

def mutate_instruction_sequence(instructions, num_mutations=1, max_cycle=60, max_address=19):
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
        mutation_type = random.choice(['add', 'delete', 'modify'])
        
        if mutation_type == 'add' and available_cycles:
            # Add a new instruction at an available cycle
            new_cycle = random.choice(available_cycles)
            instr_type = random.choice(instruction_types)
            address = random.randint(0, max_address)
            mutated[new_cycle] = (instr_type, address)
            available_cycles.remove(new_cycle)
            
        elif mutation_type == 'delete' and mutated:
            # Delete a random existing instruction
            cycle_to_delete = random.choice(list(mutated.keys()))
            del mutated[cycle_to_delete]
            available_cycles.append(cycle_to_delete)
            
        elif mutation_type == 'modify' and mutated:
            # Modify an existing instruction
            cycle_to_modify = random.choice(list(mutated.keys()))
            old_type, old_address = mutated[cycle_to_modify]
            
            # Choose what to modify: type, address, or both
            modify_choice = random.choice(['type', 'address', 'both'])
            
            if modify_choice == 'type':
                # Change instruction type only
                new_type = 'write' if old_type == 'read' else 'read'
                mutated[cycle_to_modify] = (new_type, old_address)
            elif modify_choice == 'address':
                # Change address only
                new_address = random.randint(0, max_address)
                mutated[cycle_to_modify] = (old_type, new_address)
            else:
                # Change both type and address
                new_type = 'write' if old_type == 'read' else 'read'
                new_address = random.randint(0, max_address)
                mutated[cycle_to_modify] = (new_type, new_address)
    
    return mutated


def compare_sequences(original, mutated):
    """Compare two sequences and show the differences."""
    original_cycles = set(original.keys())
    mutated_cycles = set(mutated.keys())
    
    added = mutated_cycles - original_cycles
    deleted = original_cycles - mutated_cycles
    common = original_cycles & mutated_cycles
    
    changes = []
    for cycle in common:
        if original[cycle] != mutated[cycle]:
            changes.append(cycle)
    
    print("Changes:")
    if added:
        print(f"  Added cycles: {sorted(added)}")
    if deleted:
        print(f"  Deleted cycles: {sorted(deleted)}")
    if changes:
        print(f"  Modified cycles: {sorted(changes)}")
        for cycle in sorted(changes):
            print(f"    {cycle}: {original[cycle]} -> {mutated[cycle]}")
    if not (added or deleted or changes):
        print("  No changes (mutation resulted in identical sequence)")
    print()

# Example usage and testing
#if __name__ == "__main__":
#    print("=== Instruction Sequence Mutation Demo ===\n")
#    
#    # Generate an original sequence
#    original = generate_instruction_sequence(num_instructions=8)
#    print_instruction_sequence(original, "Original Sequence")
#    print()
#    
#    # Test different numbers of mutations
#    for num_mutations in [1, 2, 3]:
#        print(f"\n--- Performing {num_mutations} mutation(s) ---")
#        mutated = mutate_instruction_sequence(original, num_mutations=num_mutations)
#        print_instruction_sequence(mutated, "Mutated Sequence")
#        compare_sequences(original, mutated)
#    
#    # Test edge cases
#    print("\n=== Edge Case Tests ===")
#    
#    # Empty sequence mutation (only additions possible)
#    print("\nMutating empty sequence:")
#    empty_seq = {}
#    mutated_empty = mutate_instruction_sequence(empty_seq, num_mutations=2)
#    print_instruction_sequence(empty_seq, "Original (empty)")
#    print_instruction_sequence(mutated_empty, "Mutated")
#    compare_sequences(empty_seq, mutated_empty)
#    
#    # Full sequence mutation (only deletions/modifications possible)
#    print("\nMutating full sequence (all cycles used):")
#    full_seq = {cycle: ('read', 0) for cycle in range(0, 61)}
#    mutated_full = mutate_instruction_sequence(full_seq, num_mutations=3)
#    print(f"Original has {len(full_seq)} instructions")
#    print(f"Mutated has {len(mutated_full)} instructions")
#    compare_sequences(full_seq, mutated_full)
