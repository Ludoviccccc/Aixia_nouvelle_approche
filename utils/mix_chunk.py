import random
import heapq

class Mix_sequences_chunks:
    def __init__(self,
                 max_cycle: int = 60,
                 max_instructions:int=None,
                 ):
        self.max_cycle = max_cycle
        self.num_parts = 2
        self.seed = None
        self.max_instructions = max_instructions
    def mix(self,sequences):
        """
        Randomly mixes multiple instruction programs into one.
    
        Args:
            sequences (list[dict]): List of programs {cycle: (type, address)}
            self.num_parts (int): Number of chunks to split each program into
            self.seed (int | None): Random self.seed
            self.max_cycle (int): Maximum cycle number in output
    
        Returns:
            dict: Mixed program {cycle: (type, address)}
        """
    
        rng = random.Random(self.seed)
    
        # Step 1: sort each program by cycle
        sorted_programs = []
        for program in sequences:
            instrs = sorted(program.items(), key=lambda x: x[0])
            sorted_programs.append(instrs)
    
        # Step 2: split each program into self.num_parts chunks
        chunks = []
        for instrs in sorted_programs:
            if not instrs:
                continue
    
            chunk_size = max(1, len(instrs) // self.num_parts)
            for i in range(0, len(instrs), chunk_size):
                chunk = instrs[i:i + chunk_size]
                chunks.append(chunk)
    
        # Step 3: shuffle chunks
        rng.shuffle(chunks)
    
        # Step 4: flatten chunks into a single instruction list
        mixed_instrs = []
        for chunk in chunks:
            mixed_instrs.extend(chunk)
    
        if not mixed_instrs:
            return {}
    
        # Step 5: assign new increasing random cycles
        num_instrs = len(mixed_instrs)
        available_cycles = sorted(
            rng.sample(range(1, self.max_cycle + 1), k=num_instrs)
        )
    
        # Step 6: build final program
        mixed_program = {
            cycle: instr
            for cycle, (_, instr) in zip(available_cycles, mixed_instrs)
        }

        while len(mixed_program)>self.max_instructions:
            to_del = random.sample(list(mixed_program.keys()),len(mixed_program)- self.max_instructions)
            for k in to_del:
                del mixed_program[k]
        assert len(mixed_program)<=self.max_instructions, f'number of instrutions is too high {len(mixed_program)}'
        return mixed_program
    def __call__(self, sequences: list):
        programs_core0 = [seq['core0'] for seq in sequences]
        programs_core1 = [seq['core1'] for seq in sequences]
        output = {'core0':self.mix(sequences=programs_core0),
                  'core1':self.mix(sequences=programs_core1)}
        return output 
