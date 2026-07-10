import random
import heapq

class Mix_sequences_interleaved:
    def __init__(self, max_cycle: int = 60, chunk_size: int = None):
        self.max_cycle = max_cycle
        self.chunk_size = chunk_size  # If None, split at shared address occurrences
    
    def __call__(self, sequences: list, seed: int = None):
        """
        Randomly mixes multiple instruction programs by interleaving chunks of instructions
        while preserving relative timing delays within each original program.
        
        Args:
            sequences (list[dict]): List of programs {cycle: (type, address)}
            seed (int | None): Random seed
            self.max_cycle (int): Maximum cycle number in output
        
        Returns:
            dict: Mixed program {cycle: (type, address)}
        """
        
        rng = random.Random(seed)
        
        # Find the shared start/end address
        shared_address = self._find_shared_address(sequences)
        
        # Step 1: Split each program into chunks
        program_chunks = []
        for program in sequences:
            if not program:
                continue
            
            # Sort by cycle
            sorted_items = sorted(program.items(), key=lambda x: x[0])
            
            # Split into chunks based on shared address or fixed size
            chunks = self._split_into_chunks(sorted_items, shared_address)
            program_chunks.append(chunks)
        
        if not program_chunks:
            return {}
        
        # Step 2: Create priority queue for chunk selection
        heap = []
        chunk_pointers = [0] * len(program_chunks)
        
        for prog_idx, chunks in enumerate(program_chunks):
            if chunks:
                random_priority = rng.random()
                heapq.heappush(heap, (random_priority, prog_idx, 0))  # (priority, program_idx, chunk_idx)
        
        # Step 3: Interleave chunks
        mixed_program = {}
        current_cycle = 1
        
        # Track the base cycle for each program
        program_bases = [None] * len(program_chunks)
        
        while heap:
            _, prog_idx, chunk_idx = heapq.heappop(heap)
            
            chunks = program_chunks[prog_idx]
            chunk = chunks[chunk_idx]
            
            # Get the first instruction's offset for this chunk
            first_offset = chunk[0][0] if chunk else 0
            
            # Determine base cycle for this program if not set
            if program_bases[prog_idx] is None:
                program_bases[prog_idx] = current_cycle
                base_cycle = current_cycle
            else:
                base_cycle = program_bases[prog_idx]
            
            # Place all instructions in the chunk
            for offset, (cycle, instr) in enumerate(chunk):
                actual_cycle = base_cycle + cycle if cycle is not None else base_cycle + offset
                
                # Handle cycle collisions
                while actual_cycle in mixed_program and actual_cycle <= self.max_cycle:
                    actual_cycle += 1
                
                if actual_cycle > self.max_cycle:
                    break
                
                mixed_program[actual_cycle] = instr
                current_cycle = max(current_cycle, actual_cycle + 1)
            
            # Schedule next chunk if available
            if chunk_idx + 1 < len(chunks):
                random_priority = rng.random()
                heapq.heappush(heap, (random_priority, prog_idx, chunk_idx + 1))
        
        # Step 4: Ensure output starts and ends with shared address
        mixed_program = self._ensure_shared_address_boundaries(mixed_program, shared_address)
        
        # Step 5: Compress if necessary
        if mixed_program and max(mixed_program.keys()) > self.max_cycle:
            mixed_program = self._compress_program(mixed_program)
        
        return mixed_program
    
    def _find_shared_address(self, sequences):
        """Find the address that appears at the start and end of all programs"""
        if not sequences:
            return None
        
        # Get first and last instruction from first program
        first_program = sequences[0]
        if not first_program:
            return None
        
        sorted_first = sorted(first_program.items(), key=lambda x: x[0])
        start_addr = sorted_first[0][1][1] if sorted_first else None
        end_addr = sorted_first[-1][1][1] if sorted_first else None
        
        # Verify all programs share these addresses
        for program in sequences[1:]:
            if not program:
                continue
            sorted_prog = sorted(program.items(), key=lambda x: x[0])
            if sorted_prog and (sorted_prog[0][1][1] != start_addr or sorted_prog[-1][1][1] != end_addr):
                # Fall back to most common address
                start_addr = self._get_most_common_address(sequences, position='start')
                end_addr = self._get_most_common_address(sequences, position='end')
                break
        
        return start_addr  # Return start address as the shared boundary marker
    
    def _get_most_common_address(self, sequences, position='start'):
        """Get the most common address at start or end of programs"""
        addresses = []
        for program in sequences:
            if not program:
                continue
            sorted_prog = sorted(program.items(), key=lambda x: x[0])
            if sorted_prog:
                if position == 'start':
                    addresses.append(sorted_prog[0][1][1])
                else:
                    addresses.append(sorted_prog[-1][1][1])
        
        if not addresses:
            return None
        
        from collections import Counter
        return Counter(addresses).most_common(1)[0][0]
    
    def _split_into_chunks(self, sorted_items, shared_address):
        """Split a program into chunks based on shared address occurrences or fixed size"""
        chunks = []
        current_chunk = []
        
        if self.chunk_size:
            # Split by fixed size
            for i, (cycle, instr) in enumerate(sorted_items):
                current_chunk.append((cycle, instr))
                if len(current_chunk) >= self.chunk_size:
                    chunks.append(current_chunk)
                    current_chunk = []
            if current_chunk:
                chunks.append(current_chunk)
        else:
            # Split at shared address occurrences (excluding first and last)
            for cycle, instr in sorted_items:
                current_chunk.append((cycle, instr))
                # Split when we encounter the shared address (but not at the very end)
                if instr[1] == shared_address and len(current_chunk) > 1:
                    chunks.append(current_chunk)
                    current_chunk = []
            
            # Add remaining instructions as final chunk
            if current_chunk:
                chunks.append(current_chunk)
        
        # Ensure we don't have empty chunks
        return [chunk for chunk in chunks if chunk]
    
    def _ensure_shared_address_boundaries(self, program, shared_address):
        """Ensure the output program starts and ends with the shared address"""
        if not program or shared_address is None:
            return program
        
        sorted_cycles = sorted(program.items())
        
        # Check if first instruction has shared address
        first_cycle, first_instr = sorted_cycles[0]
        if first_instr[1] != shared_address:
            # Add shared address at beginning
            new_program = {1: (first_instr[0], shared_address)}
            # Shift all existing instructions
            shift = 2
            for cycle, instr in sorted_cycles:
                new_program[cycle + shift - 1] = instr
            program = new_program
            sorted_cycles = sorted(program.items())
        
        # Check if last instruction has shared address
        last_cycle, last_instr = sorted_cycles[-1]
        if last_instr[1] != shared_address:
            # Add shared address at end
            program[max(program.keys()) + 1] = (last_instr[0], shared_address)
        
        return program
    
    def _compress_program(self, program):
        """Compress program to remove gaps and fit within max_cycle"""
        compressed = {}
        new_cycle = 1
        sorted_cycles = sorted(program.keys())
        for old_cycle in sorted_cycles:
            if new_cycle <= self.max_cycle:
                compressed[new_cycle] = program[old_cycle]
                new_cycle += 1
            else:
                break
        return compressed


# Example usage
#if __name__ == "__main__":
#    p1 = {3: ('read', 5), 14: ('read', 10), 26: ('read', 18), 29: ('write', 5)}
#    p2 = {4: ('read', 5), 12: ('write', 7), 32: ('read', 8), 35: ('write', 12), 39: ('write', 1), 51: ('write', 5)}
#    
#    mixer = Mix_sequences_interleaved(max_cycle=60)
#    mixture = mixer([p1, p2], seed=42)
#    
#    print("Mixed program:")
#    for cycle in sorted(mixture.keys()):
#        print(f"  {cycle}: {mixture[cycle]}")
