from os import altsep
#===============================================================================
# This model represents a memory hierarchy with
# - 2 levels of cache (L1 local, L2 shared)
# - no cache sharing policy (local caches may become inconsistent with respect 
#   to main memory)
# - a DDR memory implementing some simple optimization features (see the DDR class)
# - an interconnect
# The number of cores, levels of cache, characteristics of the cache (number of ways,...)
# are parameters and can be modified.
#===============================================================================

import random
import heapq
from enum import Enum, auto
import numpy as np

# ==========================================================
# Global clock
# ==========================================================
# -----------------------------------------------------
# Add to the Var class initialization (add these new tracking structures):

class Var:
    def __init__(self,
            step:int=10,
            max_instructions:int=100,
                      ):
        self.global_cycle = 0
        # New: Track shared resource contention
        self.shared_resource_events = []
        self.max_instructions = max_instructions
        self.access_ddr = {
            'cycle': [],
            'core_id': [],
            'addr': [],
            'operation': [],
            'bank': [],
            'row': [],
            'status': [],
            'id':[],
        }
        make_empty_dict =  lambda: {window:0 for window in range(1+max_instructions//step)}
        self.hits = {"type":"hit","L1":make_empty_dict(),"L2":make_empty_dict()}
        self.misses = {"type":"miss","L1":make_empty_dict(),"L2":make_empty_dict()}
        self.events = {"L1":{},"L2":{}}
        self.step = step
        self.count = 0
        
        # NEW: Detailed instruction sequence tracking
        self.instruction_sequences = []  # List of instruction execution records
        self.current_instruction_id = None
        
    def start_instruction(self, instr_id, cycle, core_id, operation, addr):
        """Start tracking a new instruction"""
        self.current_instruction_id = instr_id
        self.instruction_sequences.append({
            'instr_id': instr_id,
            'cycle_start': cycle,
            'core_id': core_id,
            'operation': operation,
            'address': addr,
            'steps': [],
            'cycle_end': None,
            'total_cycles': None
        })
    
    def add_instruction_step(self, instr_id, step_type, level, details, cycle):
        """Add a step to the current instruction's sequence"""
        # Find the instruction record
        for record in self.instruction_sequences:
            if record['instr_id'] == instr_id:
                record['steps'].append({
                    'cycle': cycle,
                    'step_type': step_type,
                    'level': level,
                    'details': details
                })
                break
    
    def complete_instruction(self, instr_id, cycle):
        """Mark instruction as complete"""
        for record in self.instruction_sequences:
            if record['instr_id'] == instr_id:
                record['cycle_end'] = cycle
                record['total_cycles'] = cycle - record['cycle_start']
                break
        self.current_instruction_id = None
    
    def log_memory_access_sequence(self, instr_id, core_id, addr, operation, 
                                   level, access_type, eviction_info=None, 
                                   lower_access=None):
        """
        Log the complete memory access sequence for an instruction
        
        access_type: 'hit' or 'miss'
        eviction_info: {'dirty': bool, 'evicted_addr': int, 'needs_writeback': bool}
        lower_access: {'level': str, 'operation': str, 'addr': int}
        """
        sequence = {
            'instr_id': instr_id,
            'core_id': core_id,
            'address': addr,
            'operation': operation,  # 'read' or 'write'
            'cache_level': level,    # 'L1' or 'L2'
            'access_type': access_type,  # 'hit' or 'miss'
            'eviction': eviction_info,
            'lower_memory_access': lower_access,
            'cycle': self.global_cycle
        }
        
        if not hasattr(self, 'memory_access_sequences'):
            self.memory_access_sequences = []
        self.memory_access_sequences.append(sequence)

    def log_event(self,
            type_:str,
            cycle:int,
            level:str,
            core_id:int,
            addr:int,
            way:int,
            operation:str,
            id_:int,
            ):
        access = {
                "cycle":cycle,
                "type":type_,
                "operation":operation,
                "instr_id":id_,
                "addr": addr,
                "core_id": core_id,
                "way": way
                }
        if id_>=self.max_instructions:
            raise TypeError(f'id_ {id_} is too big')
        #add to self.events dictionary
        if addr not in self.events[level]:
            self.events[level][addr] = [access]
        else:
            self.events[level][addr].append(access)
        if type_=="miss":
            self.misses[level][id_//self.step] += 1
        if type_=="hit":
            self.hits[level][id_//self.step] += 1
        if level=='L1':
            self.count +=1
        
        # NEW: Log detailed sequence based on operation type and hit/miss
        self.log_memory_access_sequence(
            instr_id=id_,
            core_id=core_id,
            addr=addr,
            operation=operation,
            level=level,
            access_type=type_
        )
        
        # Add step to instruction sequence
        self.add_instruction_step(
            instr_id=id_,
            step_type=f"{level}_{type_.upper()}",
            level=level,
            details={'operation': operation, 'way': way},
            cycle=cycle
        )
    
    def log_eviction(self,
                    cycle,
                    level,
                    core_id,
                    evicted_addr,
                    way,
                    dirty,
                    operation,
                    reason="miss_replacement",
                    id_=0,
                    ):
        access = {
                    "type":"eviction",
                    "code_id":core_id,
                    "way":way,
                    "operation":operation,
                    "cycle":cycle,
                    "dirty":dirty,
                    "instr_id":id_,
                    "evicted_addr": evicted_addr,
                    "reason": reason
                }
        if evicted_addr not in self.events[level]:
            self.events[level][evicted_addr] = [access]
        else:
            self.events[level][evicted_addr].append(access)
        
        # NEW: Log eviction details for the instruction sequence
        if hasattr(self, 'memory_access_sequences') and self.memory_access_sequences:
            # Find the most recent access for this instruction and add eviction info
            for seq in reversed(self.memory_access_sequences):
                if seq['instr_id'] == id_ and seq['eviction'] is None:
                    seq['eviction'] = {
                        'dirty': dirty,
                        'evicted_addr': evicted_addr,
                        'way': way,
                        'reason': reason,
                        'needs_writeback': dirty
                    }
                    break
        
        # Add step to instruction sequence
        self.add_instruction_step(
            instr_id=id_,
            step_type=f"{level}_EVICTION",
            level=level,
            details={'evicted_addr': evicted_addr, 'dirty': dirty, 'reason': reason, 'way': way},
            cycle=cycle
        )
    
    def log_lower_level_access(self, instr_id, level_from, level_to, operation, addr, is_writeback=False):
        """Log when a lower level memory access occurs (L2 access or DDR access)"""
        if not hasattr(self, 'lower_level_accesses'):
            self.lower_level_accesses = []
        
        access_record = {
            'instr_id': instr_id,
            'from_level': level_from,
            'to_level': level_to,
            'operation': operation,
            'address': addr,
            'is_writeback': is_writeback,
            'cycle': self.global_cycle
        }
        self.lower_level_accesses.append(access_record)
        
        # Add step to instruction sequence
        step_type = "WRITEBACK" if is_writeback else f"{level_from}_TO_{level_to}"
        self.add_instruction_step(
            instr_id=instr_id,
            step_type=step_type,
            level=level_from,
            details={'operation': operation, 'addr': addr, 'target': level_to},
            cycle=self.global_cycle
        )
    
    def log_shared_resource_event(self, event_type, resource_type, initiators, details,cycle):
        """Log when multiple initiators access shared resources simultaneously"""
        event = {
            'cycle': cycle,
            'type': event_type,
            'resource': resource_type,
            'initiators': initiators.copy(),  # Core IDs involved
            'details': details.copy()
        }
        self.shared_resource_events.append(event)
    
    def log_ddr_access(self, core_id, addr, operation, bank, row, status, id_):
        """Log DDR memory access for contention analysis"""
        cycle = self.global_cycle
        access = {
            'cycle': cycle,
            'core_id': core_id,
            'addr': addr,
            'operation': operation,
            'bank': bank,
            'row': row,
            'status': status,
            'id': id_,
        }
        self.access_ddr['cycle'].append(cycle)
        self.access_ddr['core_id'].append(core_id)
        self.access_ddr['addr'].append(addr)
        self.access_ddr['operation'].append(operation)
        self.access_ddr['bank'].append(bank)
        self.access_ddr['row'].append(row)
        self.access_ddr['status'].append(status)
        self.access_ddr['id'].append(id_)
        
        # Log as lower level access
        self.log_lower_level_access(
            instr_id=id_,
            level_from="L2",
            level_to="DDR",
            operation=operation,
            addr=addr,
            is_writeback=(operation == 'write')
        )
    
    def get_instruction_sequences_formatted(self):
        """Return formatted instruction sequences as described in prompt2.txt"""
        formatted_output = []
        
        for seq in self.instruction_sequences:
            output_lines = []
            output_lines.append(f"\n--- Instruction {seq['instr_id']} (Cycle {seq['cycle_start']}-{seq['cycle_end']}) ---")
            output_lines.append(f"Core {seq['core_id']}: {seq['operation'].upper()} @ {hex(seq['address'])}")
            output_lines.append("")
            
            step_count = 1
            for step in seq['steps']:
                if "HIT" in step['step_type']:
                    if "WRITE" in str(step['details'].get('operation', '')):
                        output_lines.append(f"{step_count}. CPU => Cache {step['level']} (write hit) => update cache line => mark dirty")
                        output_lines.append(f"   (No lower-level memory access)")
                    else:
                        output_lines.append(f"{step_count}. CPU => Cache {step['level']} (read hit) => return data")
                        output_lines.append(f"   (No lower-level memory access)")
                
                elif "MISS" in step['step_type']:
                    if "WRITE" in str(step['details'].get('operation', '')):
                        output_lines.append(f"{step_count}. CPU => Cache {step['level']} (write miss)")
                    else:
                        output_lines.append(f"{step_count}. CPU => Cache {step['level']} (read miss)")
                
                elif "EVICTION" in step['step_type']:
                    if step['details'].get('dirty', False):
                        output_lines.append(f"{step_count}.   Evict dirty line at {hex(step['details']['evicted_addr'])} => needs write-back")
                    else:
                        output_lines.append(f"{step_count}.   Evict clean line at {hex(step['details']['evicted_addr'])}")
                
                elif "WRITEBACK" in step['step_type']:
                    output_lines.append(f"{step_count}.   Write-back to lower-level memory ({step['details']['operation']} @ {hex(step['details']['addr'])})")
                
                elif "TO_" in step['step_type']:
                    if step['details']['operation'] == 'read':
                        output_lines.append(f"{step_count}.   Fetch line from {step['details']['target']} ({step['details']['operation']} @ {hex(step['details']['addr'])})")
                    else:
                        output_lines.append(f"{step_count}.   Write line to {step['details']['target']} ({step['details']['operation']} @ {hex(step['details']['addr'])})")
                
                step_count += 1
            
            # Add final return step
            if seq['operation'] == 'read':
                output_lines.append(f"{step_count}. Return data to CPU")
            else:
                if seq['steps'] and any("HIT" in s['step_type'] for s in seq['steps']):
                    output_lines.append(f"{step_count}. (Write complete)")
                else:
                    output_lines.append(f"{step_count}. Write complete, line marked dirty")
            
            output_lines.append(f"\nTotal cycles: {seq['total_cycles']}")
            formatted_output.append("\n".join(output_lines))
        
        return "\n".join(formatted_output)
    
    def print_instruction_sequences(self):
        """Print all instruction sequences"""
        print(self.get_instruction_sequences_formatted())
    
    def clear_history(self):
        self.global_cycle = 0
        self.shared_resource_events = []
        self.instruction_sequences = []
        if hasattr(self, 'memory_access_sequences'):
            self.memory_access_sequences = []
        if hasattr(self, 'lower_level_accesses'):
            self.lower_level_accesses = []
    def export_sequences_to_file(self, filename="instruction_sequences.txt"):
        """Export instruction sequences to a text file"""
        with open(filename, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("MEMORY ACCESS SEQUENCES\n")
            f.write("=" * 80 + "\n")
            f.write(self.get_instruction_sequences_formatted())
            f.write("\n" + "=" * 80 + "\n")
            f.write("\nSUMMARY BY ACCESS TYPE\n")
            f.write("=" * 80 + "\n")

            # Count different types of accesses
            read_hits = 0
            read_misses = 0
            write_hits = 0
            write_misses = 0
            dirty_evictions = 0
            clean_evictions = 0

            for seq in self.instruction_sequences:
                if seq['operation'] == 'read':
                    has_hit = any("HIT" in s['step_type'] for s in seq['steps'])
                    if has_hit:
                        read_hits += 1
                    else:
                        read_misses += 1
                else:  # write
                    has_hit = any("HIT" in s['step_type'] for s in seq['steps'])
                    if has_hit:
                        write_hits += 1
                    else:
                        write_misses += 1

                # Count evictions
                for step in seq['steps']:
                    if "EVICTION" in step['step_type'] and step['details'].get('dirty', False):
                        dirty_evictions += 1
                    elif "EVICTION" in step['step_type']:
                        clean_evictions += 1

            f.write(f"\nRead Hits: {read_hits}")
            f.write(f"\nRead Misses: {read_misses}")
            f.write(f"\nWrite Hits: {write_hits}")
            f.write(f"\nWrite Misses: {write_misses}")
            f.write(f"\nDirty Evictions: {dirty_evictions}")
            f.write(f"\nClean Evictions: {clean_evictions}")
            f.write(f"\nTotal Instructions: {len(self.instruction_sequences)}")


# CacheLine: Represents a single cache line in the cache hierarchy
# -----------------------------------------------------
# We are using n-way associative cache:
# - Each set contains n cache lines with a tag entry.
# - Each line contains m bytes.
#
# A memory Address is structured as follows:
# +----------------+-----------+-----------+
# |     Tag        |   Index   |  Offset   |
# +----------------+-----------+-----------+
# where
#
# (Used to find blk) (Set selection) (Byte in block)
# "Block" and "line" are used interchangeably.
# Cache Structure:
# Set 0: [Block 0] [Block 1] [Block 2] [Block 3]  ← 4-way associativity (n=4)
# Set 1: [Block 0] [Block 1] [Block 2] [Block 3]
# ...
# Set N: [Block 0] [Block 1] [Block 2] [Block 3]

class CacheLine:
    def __init__(self):
        self.valid = False       # Indicates if this line holds valid data
        self.tag = None          # Tag of the data block
        self.dirty = False       # Indicates if the line has been written to (for write-back)

# Implements Pseudo-LRU (PLRU) replacement policy for N-way set associative caches
# The pseudoi-LRU is used to determine the bock to replace in case of cache miss.
# A binary tree is used to implement the PLRU algorithm. There is one tree per set.
# For a 4-way cache, 3 bits are used to determine the block to select.
#
#      Bit 0 (Root)
#     /           \
#   Bit 1         Bit 2
#   /   \         /   \
# Block0 Block1 Block2 Block3
#
# Each node of the tree contains a direction (left=0, right=1) that indicates
# the path to follow to find the next pLRU entry.
class PLRU:
    def __init__(self, ways):
        self.bits = [0] * (ways - 1)  # Tree structure to track usage
        self.ways = ways

    # Update the binary tree in case of a hit
    # The bits in the tree are modified to point "away" from this entry
    # (which is the MRU)
    def update_on_access(self, way):
        idx = 0
        num_levels = self.ways.bit_length() - 1
        for level in range(num_levels):
            # Select direction according to the way
             # (e.g., way=3=0b101 in a 4-way cache => direction = 1 (right subtree), 0 (left subtree)
            direction = (way >> (num_levels - 1 - level)) & 1
            self.bits[idx] = 1-direction # Point to the opposite direction
            idx = (idx << 1)+ 1 + direction

    # Compute the next victim (the pLRU)
    # The block is selected by traversing the tree according
    # to the directions given by each bit.
    def get_victim(self):
        idx = 0
        way = 0
        for level in range(self.ways.bit_length() - 1):
            direction = self.bits[idx]
            way = (way << 1) | direction
            idx = ( idx << 1) + 1 + direction
        return way

# ---------------------------------------------------------
# Represents a memory access request (either read or write)
# ---------------------------------------------------------
class MemoryRequest:
    def __init__(self, core_id, time, req_type, addr, callback=None,id_=None):
        self.core_id = core_id
        self.time = time              # Time of request
        self.req_type = req_type      # Type of request 'read' or 'write'
        self.addr = addr
        self.callback = callback      # Callback function to signal read completion
        self.completion_time = -1     # When the request is expected to complete

        self.id_ = id_ #identifyer for the instruction

    def __lt__(self, other):
        # Prioritize based on completion time for scheduling
        return self.time < other.time

    def __str__(self):
        return f"<req: {self.req_type.upper()}@{self.addr} from core {self.core_id} >"

# ---------------------------------------------------------
# Interconnect model between CPU cores and DDR, with bandwidth and latency
# ---------------------------------------------------------
# Behaviour :
# - Each request takes at least some base delay to be served.
# - A request may be delayed if the interconnect bandwidth has been "used"
# The interconnect cannot serve more than "bandwidth" requests in one cycle.
# Note
# - Using a heapqueue ensures that all items are and remain sorted
#   according to their ready_time (and req)
class Interconnect:
    def __init__(self, memory_controller, delay=5, bandwidth=4,vars_=None):
        self.vars = vars_
        self.memory_controller = memory_controller
        self.queue = []               # Queue of pending memory requests (ready_time, request)
        self.delay = delay            # Base delay before forwarding to DDR controller
        self.bandwidth = bandwidth    # Max number of requests per cycle

    # Push a request into the interconnect queue.
    # We push the tuple (ready_time, request) where ready_time is the earliest
    # time at which the request may be served by the interconnect.
    def request(self, req):
        

        # Add a random component to the delay for more realistic simulation
        ready_time = self.vars.cycle + self.delay + random.randint(0, 2)
        heapq.heappush(self.queue, (ready_time, req))

        #print(f"{self.vars.global_cycle}: [Interconnect] Request {req.req_type.upper()}@{req.addr} from core {req.core_id} queued, to be released at {ready_time}")

    # Process the interconnect's current cycle
    def tick(self):
        
        processed = 0
        requests_to_forward = []

        # Identify requests ready to be forwarded to the memory controller, respecting bandwidth
        while self.queue and self.queue[0][0] <= self.vars.cycle and processed < self.bandwidth:
            ready_time, req = heapq.heappop(self.queue)
            requests_to_forward.append(req)
            processed += 1

        # Forward the selected requests to the memory controller
        for req in requests_to_forward:
            #print(f"{self.vars.global_cycle}: [Interconnect] Request {req} sent to memory controller")
            self.memory_controller.request(req)



# ---------------------------------------------------------
# DDR Memory Controller Model
# Arbitrates and schedules requests for the DDR memory
# ---------------------------------------------------------
class DDRMemoryController:
    def __init__(self, ddr_model, tRCD=15, tRP=15, tCAS=15, tRC=30, tWR=15, tRTP=8, tCCD=4,vars_=None):

        self.vars = vars_
        self.ddr = ddr_model
        self.queue = []  # Requests waiting to be scheduled by the controller
        self.scheduled_ddr_requests = [] # Requests passed to DDR, waiting for completion

        # DDR timing parameters (example values)
        self.tRCD = tRCD    # Row to Column Delay
        self.tRP = tRP      # Row Precharge
        self.tCAS = tCAS    # Column Access Strobe latency
        self.tRC = tRC      # Row Cycle time
        self.tWR = tWR      # Write Recovery Time
        self.tRTP = tRTP    # Read to Precharge Time
        self.tCCD = tCCD    # Column to Column Delay

        # State to track for arbitration (from the paper's strategy)
        self.last_command_time = {} # Tracks when a bank was last commanded
        self.bank_open_row = [None] * self.ddr.num_banks
        self.bank_precharge_complete_time = [0] * self.ddr.num_banks
        self.last_access_command = {} # To track RD/WR transition penalties
        self.last_access_addr = {} # To track the last accessed address for a core

        self.sequence_ddr = []

    # Enqueue a request
    def request(self, req):
        
        #print(f"{self.vars.global_cycle}: [DDR controller] request queued: {req.req_type.upper()}@{req.addr}")
        heapq.heappush(self.queue, (req.time, req)) # Store with original arrival time for fairness
        self.sequence_ddr.append({'stage':'queued','cycle':self.vars.global_cycle,'type':req.req_type.upper(),'core':req.core_id,'addr':req.addr})

    def tick(self):
        
        # First, complete any requests that DDR has finished processing
        self._complete_ddr_requests()

        # Then, schedule a new request if possible
        output = self._schedule_next_request()


        return output


    def _complete_ddr_requests(self):
        
        # Requests are completed as soon as DDR signals they are done.
        completed = []
        for req_info in self.scheduled_ddr_requests:
            req = req_info['request']
            if req.completion_time <= self.vars.cycle:
                if req.req_type == 'read':
                    _ = self.ddr.memory.get(req.addr, 0) # Read value from DDR model
                    #print(f"{self.vars.global_cycle}: [DDR controller] READ@{req.addr} complete")
                    self.sequence_ddr.append({'stage':'complete','cycle':self.vars.global_cycle,'type':req.req_type.upper(),'core':req.core_id,'addr':req.addr})
                    if req.callback:
                        req.callback()
                elif req.req_type == 'write':
                    #print(f"{self.vars.global_cycle}: [DDR controller] WRITE@{req.addr} complete")
                    self.sequence_ddr.append({'stage':'complete','cycle':self.vars.global_cycle,'type':req.req_type.upper(),'core':req.core_id,'addr':req.addr})
                    pass

                completed.append(req_info)

        for req_info in completed:
            self.scheduled_ddr_requests.remove(req_info)


    def _schedule_next_request(self):
        
        if not self.queue:  # No request, return
            return

        # Apply arbitration strategy:
        # 1. Read prioritization
        # 2. Opened row prioritization
        # 3. RD/WR batching (simplified by favoring row hits and avoiding bank conflicts)
        # 4. Older commands (handled by initial sorting in `self.queue` which is a min-heap based on arrival time)

        # Candidates for scheduling
        candidates = []
        for _, req in self.queue:
            bank = self.ddr._get_bank(req.addr)
            row = self.ddr._get_row(req.addr)

            # Check if bank is available (not in precharge)
            if self.bank_precharge_complete_time[bank] > self.vars.cycle:
                continue

            # Check for intra-bank constraints (e.g., tRC for ACT commands, tCCD for consecutive RD/WR to same bank)
            # This is a simplified check for illustration
            last_cmd_time = self.last_command_time.get(bank, -self.tRC) # Default if no previous command
            if self.vars.cycle < last_cmd_time + self.tCCD: # Basic command-to-command delay
                 continue

            self.sequence_ddr.append({'stage':'ready','cycle':self.vars.global_cycle,'type':req.req_type.upper(),'core':req.core_id,'addr':req.addr})
            candidates.append(req)

        if not candidates:
            #print(f"{self.vars.global_cycle}: [DDR controller] No suitable candidates for scheduling this cycle.")
            return

        # Sort candidates based on priority rules (simplified scoring for demonstration)
        # We want to prioritize:
        # 1. Row hits
        # 2. Reads over Writes
        # 3. Older requests (handled by min-heap property of self.queue)
        candidates.sort(key=lambda req: (
            0 if self.bank_open_row[self.ddr._get_bank(req.addr)] == self.ddr._get_row(req.addr) else 1, # Row hit first
            0 if req.req_type == 'read' else 1, # Reads before writes
            req.time # Oldest request if other criteria are equal
        ))

        best_req = candidates[0]
        bank = self.ddr._get_bank(best_req.addr)
        row = self.ddr._get_row(best_req.addr)

        # Calculate actual delay for the request
        delay = self.ddr.base_latency
        #row_status = "ROW HIT"
        row_status = 1
        if self.bank_open_row[bank] == row:
            #print(f"{self.vars.global_cycle}: [DDR] ROW HIT@{best_req.addr} for bank {bank} ")
            delay = self.ddr.row_hit_latency
        else:
            #print(f"{self.vars.global_cycle}: [DDR] ROW MISS@{best_req.addr} for bank {bank} ")
            delay = self.tRP + self.tRCD + self.tCAS # ACT (tRCD) + PRE (tRP) + CAS
            #row_status = "ROW MISS"
            row_status = -1
            self.bank_precharge_complete_time[bank] = self.vars.cycle + self.tRP # Bank busy during precharge
            self.bank_open_row[bank] = row # Update opened row for the bank

        # Add transition penalties (WR->RD or RD->WR)
        # From Figure 3.10 and 3.11: WR->RD adds twTR, RD->WR adds WL (Write Latency) + 2 cycles
        # Assuming WR is tCAS + tWR and RD is tCAS
        if bank in self.last_access_command:
            last_cmd_type = self.last_access_command[bank]
            if last_cmd_type == 'write' and best_req.req_type == 'read':
                # Simplified: add twR as turnaround penalty for WR->RD
                delay += self.tWR # tWTR for actual paper value
                #print(f"{self.vars.global_cycle}: [DDR] Applying WR->RD transition penalty for Bank {bank}")
            elif last_cmd_type == 'read' and best_req.req_type == 'write':
                # Simplified: add tWR (Write Latency) + 2 cycles for RD->WR
                delay += self.tWR + 2
                #print(f"{self.vars.global_cycle}: [DDR] Applying RD->WR transition penalty for Bank {bank}")

        completion_time = self.vars.cycle + delay




        # Update controller's state after scheduling
        self.last_command_time[bank] = self.vars.cycle
        self.last_access_command[bank] = best_req.req_type
        self.last_access_addr[bank] = best_req.addr

        # Remove the request from the controller's queue
        for i, (time, req) in enumerate(self.queue):
            if req == best_req:
                self.queue.pop(i)
                break
        heapq.heapify(self.queue) # Re-heapify after pop

        #print(f"{self.vars.global_cycle}: [DDR controller] Scheduling {best_req.req_type.upper()}@{best_req.addr} via Controller")
        #print(f"{self.vars.global_cycle}: [DDR controller] Bank {bank}, Row {row} | {row_status} | Calculated Delay: {delay} | Completion at Cycle {completion_time}")

        self.sequence_ddr.append({'stage':'scheduling','cycle':self.vars.global_cycle,'type':req.req_type.upper(),'core':req.core_id,'addr':req.addr})

        # Pass the request to the DDR
        best_req.time = self.vars.cycle # Update request time to when it's issued to DDR
        best_req.completion_time = completion_time
        self.ddr.request(best_req) # DDR will now track its internal completion
        self.scheduled_ddr_requests.append({'request': best_req, 'bank': bank, 'row': row, 'status': row_status})


        self.vars.log_ddr_access(best_req.core_id, best_req.addr, best_req.req_type,
                               self.ddr._get_bank(best_req.addr), self.ddr._get_row(best_req.addr), row_status,best_req.id_)
        #for cmd in candidates[1:]:
        #    self.vars.log_ddr_access(cmd.core_id, cmd.addr, cmd.req_type,
        #                       self.ddr._get_bank(cmd.addr), self.ddr._get_row(cmd.addr), 'waiting',best_req.id_)

        return {'completion_time': completion_time,
                'row': row,
                'bank': bank,
                'status': row_status,
                'core':best_req.core_id,
                'delay': delay,
                'candidates':candidates,
                'current_type':best_req.req_type,
                }

class DDRState(Enum):
    IDLE = auto()
    ACTIVATE_BANK_ROW = auto()
    WRITING = auto()
    READING = auto()
    PRECHARGING = auto()

#---------------------------------------------------------
# DDR Memory Model
#---------------------------------------------------------
class DDRMemory:
    def __init__(self, num_banks=8,vars_=None):
        self.vars = vars_
        self.num_banks = num_banks
        self.memory = {} # Actual data storage (addr -> value)
        self.vars.cycle = 0
        # [TODO] Provide real latency values
        self.base_latency = 0
        self.row_hit_latency = 0

        # State machine for each bank
        self.bank_states = [DDRState.IDLE] * num_banks
        self.bank_timers = [0] * num_banks # Time until next state transition
        self.bank_open_row = [None] * num_banks # Currently open row in each bank
        self.bank_active_requests = [None] * num_banks # Request currently being serviced by a bank

        self.scheduled_completions = [] # Requests whose data is ready to be returned

    def _get_bank(self, addr):
        return addr % self.num_banks

    def _get_row(self, addr):
        return addr // 8 # Example: each row covers 8 addresses (line_size is 4, so 4 cache lines per row for a 4-line_size cache)

    # Request from controller to DDR (e.g., ACT, RD, WR, PRE)
    def request(self, req):
        

        bank = self._get_bank(req.addr)
        row = self._get_row(req.addr)

        # Simplified state transitions (see Figure 3.9 in Mascarenas-Gonzalez thesis)
        current_state = self.bank_states[bank]
        #print(f"{self.vars.global_cycle}: [DDR] Bank {bank} receives {req.req_type.upper()} for Row {row}. Current state: {current_state.name}")

        if req.req_type == 'read':
            if current_state == DDRState.IDLE or self.bank_open_row[bank] != row:
                # Need to ACTIVATE first (handled by controller for actual delay)
                # For this simplified FSM, we assume controller has done the ACT/PRE
                self.bank_states[bank] = DDRState.READING
                self.bank_timers[bank] = req.completion_time
                self.bank_open_row[bank] = row
                #print(f"{self.vars.global_cycle}: [DDR] Bank {bank} transition: IDLE or row change -> READING scheduled at {req.completion_time}")

            elif current_state == DDRState.ACTIVATE_BANK_ROW or current_state == DDRState.READING:
                self.bank_states[bank] = DDRState.READING
                self.bank_timers[bank] = req.completion_time
                #print(f"{self.vars.global_cycle}: [DDR] Bank {bank} transition: ACTIVATE_BANK_ROW/READING -> READING scheduled at {req.completion_time}")
                
            else:
                #print(f"{self.vars.global_cycle}: [DDR] ERROR: Cannot READ from Bank {bank} in state {current_state.name}")
                pass

        elif req.req_type == 'write':
            if current_state == DDRState.IDLE or self.bank_open_row[bank] != row:
                self.bank_states[bank] = DDRState.WRITING
                self.bank_timers[bank] = req.completion_time
                self.bank_open_row[bank] = row
                #print(f"{self.vars.global_cycle}: [DDR] Bank {bank} transition: IDLE -> WRITING  scheduled at {req.completion_time}")

            elif current_state == DDRState.ACTIVATE_BANK_ROW or current_state == DDRState.WRITING:
                self.bank_states[bank] = DDRState.WRITING
                self.bank_timers[bank] = req.completion_time
                #print(f"{self.vars.global_cycle}: [DDR] Bank {bank} transition: ACTIVATE_BANK_ROW/WRITING -> WRITING  scheduled at {req.completion_time}")
            else:
                #print(f"{self.vars.global_cycle}: [DDR] ERROR: Cannot WRITE to Bank {bank} in state {current_state.name}")
                pass

        # Store the request with its completion time for processing
        heapq.heappush(self.scheduled_completions, (req.completion_time, req))


    # DDR's internal tick, handling state transitions and data completion
    def tick(self):
        
        # Process scheduled completions
        while self.scheduled_completions and self.scheduled_completions[0][0] <= self.vars.cycle:
            completion_time, req = heapq.heappop(self.scheduled_completions)
            bank = self._get_bank(req.addr)

            if req.req_type == 'read':
                pass # Operation is done by controller   
            elif req.req_type == 'write':
                pass #  Operation is done by controller 

            # Update bank state after completion
            if self.bank_states[bank] == DDRState.READING or self.bank_states[bank] == DDRState.WRITING:
                # After a read/write, it implicitly goes to ACTIVATE_BANK_ROW, ready for more column access or PRE
                self.bank_states[bank] = DDRState.ACTIVATE_BANK_ROW
                self.bank_timers[bank] = 0 # Ready for next command
                #print(f"{self.vars.global_cycle}: [DDR] Bank {bank} access completion, transition: READING/WRITING -> ACTIVATE_BANK_ROW")

        # Update FSM timers for each bank
        for i in range(self.num_banks):
            if self.bank_timers[i] > self.vars.cycle:
                # Timer still running, nothing to do for this cycle
                pass
            elif self.bank_states[i] == DDRState.ACTIVATE_BANK_ROW:
                # If a bank is active and its previous command timer expired, it's ready for another
                # READ/WRITE or can be PRECHARGED by the controller.
                pass # Stays in ACTIVATE_BANK_ROW until controller issues next command
            elif self.bank_states[i] == DDRState.PRECHARGING and self.bank_timers[i] <= self.vars.cycle:
                self.bank_states[i] = DDRState.IDLE
                self.bank_open_row[i] = None
                #print(f"{self.vars.global_cycle}: [DDR] Bank {i} transition: PRECHARGING -> IDLE")


#---------------------------------------
# Models one level in the cache hierarchy
#----------------------------------------
class CacheLevel:
    def __init__(self, level_name, core_id, size, line_size, assoc, memory=None, write_back=True, write_allocate=True,vars_=None):
        self.vars = vars_
        self.level = level_name
        self.core_id = core_id
        self.line_size = line_size
        self.assoc = assoc
        self.num_sets = (size // line_size) // assoc
        self.sets = [[CacheLine() for _ in range(assoc)] for _ in range(self.num_sets)]
        self.plru_trees = [PLRU(assoc) for _ in range(self.num_sets)]
        self.memory = memory        # Could be DDR or next cache level (now it's interconnect)
        self.lower = None           # Lower level cache
        self.write_back = write_back
        self.write_allocate = write_allocate
        self.hits = 0
        self.hits_read = 0
        self.hits_write = 0
        self.misses = 0
        self.misses_write = 0
        self.misses_read = 0
        
        self.miss_tab = np.zeros((self.num_sets,assoc))
        self.hit_tab = np.zeros((self.num_sets,assoc))

    # Extract the set index from the address
    #  addr = [ tag ][ idx ][ offset ]
    def _index(self, addr):
        return (addr // self.line_size) % self.num_sets

    # Extract the tag from the address
    #  addr = [ tag ][ idx ][ offset ]
    def _tag(self, addr):
        return addr // (self.line_size * self.num_sets)

    # Handles cache read request
    # Update the CacheLevel.read() method to log lower level accesses:

    def read(self, addr, callback, origine=None, id_=None):
        index = self._index(addr)
        tag = self._tag(addr)
        cache_set = self.sets[index]
        plru = self.plru_trees[index]
    
        # Start tracking this instruction if not already started
        if id_ is not None and self.vars.current_instruction_id != id_:
            self.vars.start_instruction(id_, self.vars.global_cycle, self.core_id, 'read', addr)
    
        # Search the tag in the cache set
        for i, line in enumerate(cache_set):
            if line.valid and line.tag == tag:
                # Cache hit
                self.hits += 1
                self.hits_read += 1
                self.hit_tab[index, i] += 1
    
                plru.update_on_access(i)
    
                self.vars.log_event(
                    type_="hit",
                    cycle=self.vars.global_cycle,
                    level=self.level,
                    core_id=self.core_id,
                    addr=addr,
                    way=i,
                    operation="read",
                    id_=id_,
                )
    
                callback()
                self.vars.complete_instruction(id_, self.vars.global_cycle)
                return
    
        # Cache miss
        self.vars.log_event(
            type_="miss",
            cycle=self.vars.global_cycle,
            level=self.level,
            core_id=self.core_id,
            addr=addr,
            way=i,
            operation='read',
            id_=id_
        )
    
        self.misses += 1
        self.misses_read += 1
        self.miss_tab[index, i] += 1
    
        victim_idx = plru.get_victim()
        victim_line = cache_set[victim_idx]
    
        # Log if this is a clean or dirty eviction
        if victim_line.valid and self.write_back and victim_line.dirty:
            victim_addr = ((victim_line.tag * self.num_sets) + index) * self.line_size
            self.vars.log_lower_level_access(
                instr_id=id_,
                level_from=self.level,
                level_to="lower",
                operation="write",
                addr=victim_addr,
                is_writeback=True
            )
    
        def lower_cb():
            if victim_line.valid and victim_line.dirty and self.write_back:
                victim_addr = ((victim_line.tag * self.num_sets) + index) * self.line_size
                if self.lower:
                    self.lower.write(victim_addr, origine=self.core_id, id_=id_)
                elif self.memory:
                    self.memory.request(MemoryRequest(origine, self.memory.vars.global_cycle, 'write', victim_addr, callback=None, id_=id_))
    
            victim_line.valid = True
            victim_line.tag = tag
            victim_line.dirty = False
            plru.update_on_access(victim_idx)
            callback()
            self.vars.complete_instruction(id_, self.vars.global_cycle)
    
        # Log lower level read access
        self.vars.log_lower_level_access(
            instr_id=id_,
            level_from=self.level,
            level_to="lower",
            operation="read",
            addr=addr,
            is_writeback=False
        )
    
        if self.lower:
            self.lower.read(addr, lower_cb, origine=self.core_id, id_=id_)
        elif self.memory:
            self.memory.request(MemoryRequest(origine, self.memory.vars.global_cycle, 'read', addr, lower_cb, id_=id_))
    # Handles cache write request
    def write(self, addr, origine=None, id_=None):
        index = self._index(addr)
        tag = self._tag(addr)
        cache_set = self.sets[index]
        plru = self.plru_trees[index]

        # Start tracking this instruction if not already started
        if id_ is not None and self.vars.current_instruction_id != id_:
            self.vars.start_instruction(id_, self.vars.global_cycle, self.core_id, 'write', addr)

        for i, line in enumerate(cache_set):
            if line.valid and line.tag == tag:
                # Cache hit in write-back mode
                self.hits += 1
                self.hits_write += 1

                line.dirty = True if self.write_back else False
                plru.update_on_access(i)

                if not self.write_back:
                    if self.lower:
                        self.lower.write(addr, origine=self.core_id, id_=id_)
                    elif self.memory:
                        self.memory.request(MemoryRequest(origine, self.memory.vars.global_cycle, 'write', addr, id_=id_))

                self.vars.log_event(
                    type_="hit",
                    cycle=self.vars.global_cycle,
                    level=self.level,
                    core_id=self.core_id,
                    addr=addr,
                    way=i,
                    operation="write",
                    id_=id_,
                )

                self.vars.complete_instruction(id_, self.vars.global_cycle)
                return

        # Cache miss
        self.vars.log_event(
            type_="miss",
            cycle=self.vars.global_cycle,
            level=self.level,
            core_id=self.core_id,
            addr=addr,
            way=i,
            operation="write",
            id_=id_,
        )

        self.misses += 1
        self.misses_write += 1

        if self.write_allocate:
            victim_idx = plru.get_victim()
            victim_line = cache_set[victim_idx]

            if victim_line.valid and self.write_back and victim_line.dirty:
                victim_addr = ((victim_line.tag * self.num_sets) + index) * self.line_size
                self.vars.log_lower_level_access(
                    instr_id=id_,
                    level_from=self.level,
                    level_to="lower",
                    operation="write",
                    addr=victim_addr,
                    is_writeback=True
                )

                if self.lower:
                    self.lower.write(victim_addr, origine=self.core_id, id_=id_)
                elif self.memory:
                    self.memory.request(MemoryRequest(origine, self.memory.vars.global_cycle, 'write', victim_addr, id_=id_))

            self.vars.log_lower_level_access(
                instr_id=id_,
                level_from=self.level,
                level_to="lower",
                operation="read",
                addr=addr,
                is_writeback=False
            )

            victim_line.valid = True
            victim_line.tag = tag
            victim_line.dirty = self.write_back
            plru.update_on_access(victim_idx)
        else:
            if self.lower:
                self.lower.write(addr, origine=self.core_id, id_=id_)
            elif self.memory:
                self.memory.request(MemoryRequest(origine, self.memory.vars.global_cycle, 'write', addr, id_=id_))

        self.vars.complete_instruction(id_, self.vars.global_cycle)
    def stats(self):
        total = self.hits + self.misses
        denominator = self.miss_tab + self.hit_tab
        denominator[denominator==0] = -1
        self.cache_miss_tab = self.miss_tab/(denominator)
        self.cache_miss_tab[self.cache_miss_tab<=0] = 0
        return {
            'level': self.level,
            'hits': self.hits,
            'hits_read': self.hits_read,
            'hits_write': self.hits_write,
            'misses_read': self.misses_read,
            'misses_write': self.misses_write,
            'misses': self.misses,
            'miss_rate': self.misses / total if total else 0,
            'cache_miss_detailled':self.miss_tab,#number of miss at every locaation
        }

# ---------------------------------------------------------
# Multi-level cache hierarchy for a core
# Currently supports 2 levels (L1 + shared L2)
# ---------------------------------------------------------
class MultiLevelCache:
    def __init__(self, core_id, l1_conf, shared_cache):
        self.core_id = core_id
        # Create the memory hierarchy
        self.l1 = CacheLevel("L1", core_id, **l1_conf)
        self.l1.lower = shared_cache  # L1 connects to the shared L2 cache
        #add up cache for lower cache
        self.l1.lower.upper = self.l1

    # Read operation (starts at L1 level)
    def read(self, addr, callback,id_):
        self.l1.read(addr, callback,id_=id_)

    # Write operation (starts at L1 level)
    def write(self, addr,id_):
        self.l1.write(addr,id_=id_)

    def stats(self):
        return {
            "core": self.core_id,
            "L1": self.l1.stats(),
            "L2": self.l1.lower.stats() if self.l1.lower else {} # Shared L2 stats
        }

# ---------------------------------------------------------
# Simple CPU core model that generates memory accesses
# ---------------------------------------------------------
class Core:
    def __init__(self, core_id, cache,vars_):
        self.vars = vars_
        self.core_id = core_id
        self.cache = cache
        self.cache.core_id = core_id
        self.pending_accesses = []  # List of (op, addr) tuples for pending accesses
        self.stall_op = None        # (op, addr) of the stalled operation, if any
        self.inst = {}            # Instructions scheduled by cycle {cycle: (op, addr)}
        self.inst_queue = []      # Sorted list of (cycle, op, addr, id_) for sequential execution
        self.inst_ptr = 0         # Index of next instruction to execute

    # Load a sequence of instructions
    # Instructions are a dict {cycle: (op, addr)}
    def load_instr(self, inst):
        self.inst = inst
        if isinstance(inst, dict):
            self.inst_queue = sorted(
                [(cycle, op, addr,id_) for id_,(cycle, (op, addr)) in enumerate(inst.items())]
            )
            if len(self.inst_queue)>self.vars.max_instructions:
                raise TypeError(f'{self.inst_queue} is larger than {self.var.max_instructions}')
        else:
            self.inst_queue = []
        self.inst_ptr = 0

    def read(self, addr, callback,id_):
        self.cache.read(addr, callback,id_=id_)

    def write(self, addr,id_):
        self.cache.write(addr,id_=id_)   


    def enqueue_access(self, op, addr,id_):
        # Enqueue a memory access operation (read or write) in FIFO order 
        # This is used to track pending accesses for dependency checking.
        #print(f"{self.vars.global_cycle}: [Core {self.core_id}] enqueueing access {op.upper()}@{addr} :", end=" ")  
        self.pending_accesses.append((op, addr,id_))
        if len(self.pending_accesses) > 10:
            #print(f"{self.vars.global_cycle}: [Core {self.core_id}] :more than 10 pending accesses!")   
            pass
        #print(f"{self.pending_accesses}")

    def dequeue_access(self, op, addr):
        # Remove the oldest entry in the queue matching the operation and address
        #print(f"{self.vars.global_cycle}: [Core {self.core_id}] dequeueing access {op.upper()}@{addr} :", end=" ")
        for i, (o, a,id_) in enumerate(self.pending_accesses):
            if o == op and a == addr:
                self.pending_accesses.pop(i)
                #print(f"{self.pending_accesses}")                
                return  

    def dependency(self, op, addr):
        # Check if there is a RaW, WaR or WaW dependency on the given address
        # Currenty, we consider all pending accesses in the queue.
        # In this model, we stall as soon as the same address identical, except in RaR
        for (o, a,id_) in self.pending_accesses:
            if (op != o) and (a == addr):
                return True 
        return False

    def tick(self):
        

        # If the core is waiting for a previous access to complete, it cannot issue a new request
        # We consider all dependencies between instruction in RAW, WAR and WAW on addresses.
        if self.stall_op:
            op, addr,id_ = self.stall_op
            if not self.dependency(op, addr):
                #print(f"{self.vars.global_cycle}: [Core {self.core_id}] Resuming stalled {op.upper()}@{addr}")
                if op == 'write':
                    self.write(addr,id_=id_)
                    self.stall_op = None
                elif op == 'read':
                    self.enqueue_access('read', addr,id_=id_)
                    self.read(addr, lambda addr=addr: self.dequeue_access('read', addr),id_=id_)
                    self.stall_op = None
            else:
                #print(f"{self.vars.global_cycle}: [Core {self.core_id}] Still stalled on {op.upper()}@{addr} due to dependency")
                return

        # Check if there is an instruction to execute (next in queue that is due)
        if self.inst_ptr < len(self.inst_queue):
            cycle, op, addr,id_ = self.inst_queue[self.inst_ptr]
            if self.vars.global_cycle >= cycle:
                self.inst_ptr += 1
                if op=='write':
                    if self.dependency('write', addr):
                        # There is a pending access with dependency, we stall
                        #print(f"{self.vars.global_cycle}: [Core {self.core_id}] WRITE@{addr} stalled due to dependency")
                        self.stall_op = ('write', addr,id_)
                        return
                    else:
                        #print(f"{self.vars.global_cycle}: [Core {self.core_id}] WRITE op at @{addr}")
                        self.write(addr,id_=id_)
                        return self.vars.global_cycle
                else:
                    if self.dependency('read', addr):
                        # There is a pending access with dependency, we stall
                        #print(f"{self.vars.global_cycle}: [Core {self.core_id}] READ@{addr} stalled due to dependency")
                        self.stall_op = ('read', addr,id_)
                        return
                    else:
                        #print(f"{self.vars.global_cycle}: [Core {self.core_id}] READ op at @{addr}")
                        self.enqueue_access('read', addr,id_)
                        self.read(addr, lambda addr=addr: self.dequeue_access('read', addr),id_=id_)
                        return self.vars.global_cycle

# Example usage after simulation:
def print_contention_analysis():
    """Print detailed analysis of shared resource contention"""
    analysis = analyze_shared_resource_contention()

    print("\n=== SHARED RESOURCE CONTENTION ANALYSIS ===")
    print(f"Total contention events: {analysis['total_contention_events']}")
    print(f"DDR memory contention cycles: {len(analysis['ddr_contention_cycles'])}")

    print("\n=== DETAILED CONTENTION EVENTS ===")
    for event in GlobalVar.shared_resource_events:
        print(f"Cycle {event['cycle']}: {event['type']}")
        print(f"  Cores involved: {event['initiators']}")
        print(f"  Details: {event['details']}")
