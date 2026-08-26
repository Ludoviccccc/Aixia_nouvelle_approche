import random
import copy

class MutationInstructions2:
    """
    Mutate an instruction sequence by adding, deleting, or modifying instructions,
    optionally guided by an outcome and a goal.
    """
    def __init__(self,
                 num_mutations: int = 1,
                 max_cycle: int = 60,
                 min_address_core_0: int = 0,
                 max_address_core_0: int = 19,
                 min_address_core_1: int = 0,
                 max_address_core_1: int = 19,
                 max_instructions: int = None,
                 ):
        self.num_mutations = num_mutations
        self.max_cycle = max_cycle
        self.min_address_core_0 = min_address_core_0
        self.max_address_core_0 = max_address_core_0
        self.min_address_core_1 = min_address_core_1
        self.max_address_core_1 = max_address_core_1
        self.max_instructions = max_instructions

    def _parse_outcome(self, outcome):
        """
        Parse the outcome dictionary to extract which instruction cycles
        (per core) are involved in each interference type.
        Returns a dict:
            {
                'ddr': {0: set([cycles]), 1: set([cycles])},
                'ddr_scheduler': {...},
                'L2_cache': {...},
                'bus': {...}   # bus has no specific cycles, returns empty sets
            }
        """
        involved = {
            'ddr': {0: set(), 1: set()},
            'ddr_scheduler': {0: set(), 1: set()},
            'L2_cache': {0: set(), 1: set()},
            'bus': {0: set(), 1: set()}   # no specific instruction info
        }

        # DDR interference
        if 'ddr_interference' in outcome:
            ddr = outcome['ddr_interference']
            core = ddr.get('core_id')
            addr = ddr.get('addr')
            if core is not None and addr is not None:
                # We cannot determine the exact cycle from outcome alone.
                # We will later mark cycles that have this address.
                involved['ddr'][core].add(('addr', addr))  # marker

        # DDR scheduler interference
        if 'ddr_scheduler_interference' in outcome:
            dsch = outcome['ddr_scheduler_interference']
            core = dsch.get('core_id')
            addr = dsch.get('addr')
            if core is not None and addr is not None:
                involved['ddr_scheduler'][core].add(('addr', addr))
            # also attacker info
            attacker_core = dsch.get('core_attacker')
            attacker_addr = dsch.get('addr_attacker')
            if attacker_core is not None and attacker_addr is not None:
                involved['ddr_scheduler'][attacker_core].add(('addr', attacker_addr))

        # L2 cache interference
        if 'L2_cache_interference' in outcome:
            l2 = outcome['L2_cache_interference']
            evicted_core = l2.get('evicted_core_id')
            evicted_addr = l2.get('evicted_addr')
            if evicted_core is not None and evicted_addr is not None:
                involved['L2_cache'][evicted_core].add(('addr', evicted_addr))
            causing_core = l2.get('causing_core_id')
            causing_addr = l2.get('causing_addr')
            if causing_core is not None and causing_addr is not None:
                involved['L2_cache'][causing_core].add(('addr', causing_addr))

        # bus interference – no specific addresses
        # (we treat it as undesirable but cannot pinpoint which instructions)

        return involved

    def _find_cycles_with_addr(self, instructions, core, addr):
        """Return a list of cycle numbers in `instructions` that have the given address."""
        cycles = []
        for cycle, (typ, a) in instructions.items():
            if a == addr:
                cycles.append(cycle)
        return cycles

    def _guided_mutate(self, instructions, core_id, goal, outcome_info,min_address,max_address):
        """
        Apply guided mutations to a single core's instruction dict.
        `goal` is a dict like {'ddr': True, 'L2_cache': False, ...}
        `outcome_info` is the parsed outcome structure.
        """
        # Make a deep copy
        mutated = copy.deepcopy(instructions)
        # Determine desired and undesired types
        desired_types = [t for t, val in goal.items() if val]
        undesired_types = [t for t, val in goal.items() if not val]

        # Collect cycles that are involved in any undesired interference
        cycles_to_remove = set()
        cycles_to_keep = set()

        for itype in undesired_types:
            markers = outcome_info.get(itype, {}).get(core_id, set())
            for marker in markers:
                if marker[0] == 'addr':
                    addr = marker[1]
                    # Find all cycles with that address
                    cycles = self._find_cycles_with_addr(mutated, core_id, addr)
                    cycles_to_remove.update(cycles)
                # For bus, we have no specific cycles; we might randomly delete some
                if itype == 'bus' and len(mutated) > 3:
                    # remove a random instruction (but not the first/last)
                    all_cycles = set(mutated.keys())
                    if len(all_cycles) > 2:
                        # avoid deleting min and max cycles (to keep boundaries)
                        removable = list(all_cycles - {min(all_cycles), max(all_cycles)})
                        if removable:
                            cycles_to_remove.add(random.choice(removable))

        # For desired types, we want to keep those instructions, and possibly add more.
        desired_addrs = set()
        for itype in desired_types:
            markers = outcome_info.get(itype, {}).get(core_id, set())
            for marker in markers:
                if marker[0] == 'addr':
                    addr = marker[1]
                    desired_addrs.add(addr)
                    cycles = self._find_cycles_with_addr(mutated, core_id, addr)
                    cycles_to_keep.update(cycles)

        # Delete undesired cycles (only if we have enough left)
        for cycle in sorted(cycles_to_remove, reverse=True):
            if len(mutated) > 3:  # keep at least 3 instructions
                if cycle in mutated:
                    del mutated[cycle]

        # Modify some remaining instructions that are not in cycles_to_keep
        # (optional: change their addresses to avoid conflicts)
        all_cycles = set(mutated.keys())
        modifiable = list(all_cycles - cycles_to_keep - {min(all_cycles), max(all_cycles)})
        if modifiable:
            # change address of a few to random
            for _ in range(min(len(modifiable), 2)):
                cycle = random.choice(modifiable)
                old_type, _ = mutated[cycle]
                new_addr = random.randint(min_address, max_address)
                mutated[cycle] = (old_type, new_addr)
                modifiable.remove(cycle)

        # If desired interference is absent, add new instructions using desired addresses
        if desired_types and not cycles_to_keep:
            # Add one instruction for each desired type (if possible)
            for itype in desired_types:
                markers = outcome_info.get(itype, {}).get(core_id, set())
                for marker in markers:
                    if marker[0] == 'addr':
                        addr = marker[1]
                        # Find an available cycle
                        used_cycles = set(mutated.keys())
                        available = list(set(range(0, self.max_cycle + 1)) - used_cycles)
                        if available and len(mutated) < self.max_instructions:
                            new_cycle = random.choice(available)
                            instr_type = random.choice(['read', 'write'])
                            mutated[new_cycle] = (instr_type, addr)
                        break  # add at most one per type

        # Ensure we do not exceed max_instructions
        if self.max_instructions and len(mutated) > self.max_instructions:
            extra = list(set(mutated.keys()) - cycles_to_keep - {min(mutated.keys()), max(mutated.keys())})
            to_del = random.sample(extra, len(mutated) - self.max_instructions)
            for k in to_del:
                del mutated[k]

        return mutated

    def mutate(self, instructions,min_address,max_address, outcome_info=None, goal=None):
        """
        Original mutation method (random) – kept as fallback.
        If outcome_info and goal are provided, use guided mutation.
        """
        if outcome_info is not None and goal is not None:
            # We need core_id, but we don't have it here. We'll handle in __call__.
            return self._guided_mutate(instructions, 0, goal, outcome_info,min_address,max_address)  # default core_id 0

        # Original random mutation logic
        mutated = copy.deepcopy(instructions)
        instruction_types = ['read', 'write']

        def determin_cycles(mutated):
            used_cycles = set(mutated.keys())
            max_used_cycle = max(used_cycles)
            min_used_cycle = min(used_cycles)
            min_used_cycle_set = {min_used_cycle}
            max_used_cycle_set = {max_used_cycle}
            all_cycles = set(range(0, self.max_cycle + 1))
            available_cycles = list(all_cycles - used_cycles)
            return (used_cycles, max_used_cycle, min_used_cycle,
                    min_used_cycle_set, max_used_cycle_set,
                    all_cycles, available_cycles)

        used_cycles, max_used_cycle, min_used_cycle, min_used_cycle_set, max_used_cycle_set, all_cycles, available_cycles = determin_cycles(mutated)

        for _ in range(self.num_mutations):
            if self.max_instructions and len(mutated) > 3:
                mutation_type = random.choice(['delete', 'modify'])
            elif self.max_instructions and len(mutated) == self.max_instructions:
                mutation_type = random.choice(['delete', 'modify'])
            else:
                mutation_type = random.choice(['add'])
            if mutation_type == 'add' and available_cycles:
                new_cycle = random.choice(available_cycles)
                instr_type = random.choice(instruction_types)
                address = random.randint(min_address, max_address)
                mutated[new_cycle] = (instr_type, address)
                available_cycles.remove(new_cycle)
            elif mutation_type == 'delete' and mutated:
                cycle_to_delete = random.choice(list(set(mutated.keys()) - min_used_cycle_set - max_used_cycle_set))
                del mutated[cycle_to_delete]
                available_cycles.append(cycle_to_delete)
            elif mutation_type == 'modify' and mutated:
                cycle_to_modify = random.choice(list(set(mutated.keys()) - min_used_cycle_set - max_used_cycle_set))
                old_type, old_address = mutated[cycle_to_modify]
                modify_choice = random.choice(['type', 'address', 'both', 'cycle'])
                if modify_choice == 'type':
                    new_type = 'write' if old_type == 'read' else 'read'
                    mutated[cycle_to_modify] = (new_type, old_address)
                elif modify_choice == 'address':
                    new_address = random.randint(min_address, max_address)
                    mutated[cycle_to_modify] = (old_type, new_address)
                elif modify_choice == 'both':
                    new_type = 'write' if old_type == 'read' else 'read'
                    new_address = random.randint(min_address, max_address)
                    mutated[cycle_to_modify] = (new_type, new_address)
                elif modify_choice == 'cycle':
                    new_cycle = random.choice(available_cycles)
                    mutated[new_cycle] = (old_type, old_address)
                    used_cycles, max_used_cycle, min_used_cycle, min_used_cycle_set, max_used_cycle_set, all_cycles, available_cycles = determin_cycles(mutated)

        if self.max_instructions and len(mutated) > self.max_instructions:
            to_del = random.sample(list(mutated.keys()), len(mutated) - self.max_instructions)
            for k in to_del:
                del mutated[k]
        return mutated

    def __call__(self, program: dict, goal: dict, outcome: dict = None):
        """
        Mutate both cores of the program.
        If `outcome` and `goal` are provided, use guided mutation.
        """
        # Parse outcome for guidance
        outcome_info = None
        if outcome is not None:
            outcome_info = self._parse_outcome(outcome)

        # Mutate each core separately
        new_core0 = self.mutate(program['core0'], self.min_address_core_0,self.max_address_core_0,outcome_info, goal)
        new_core1 = self.mutate(program['core1'], self.min_address_core_1,self.max_address_core_1,outcome_info, goal)

        return {'core0': new_core0, 'core1': new_core1}
