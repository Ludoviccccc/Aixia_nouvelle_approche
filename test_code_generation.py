from exploration.codegeneration import Address_Management 
from exploration.env.func import Experiment
import random
import numpy as np

def print_dict(dict_):
    for key in dict_:
        print(key,dict_[key])

def distance_between_outcome(outcome1,outcome2):
    print('distance function')
    tab = (outcome1 != outcome2)*1.0
    print(tab)
    out = np.sum(tab.values)
    return out
num_addr = 40
num_banks = 4
min_address = 0
max_address = 19
num_instructions = 5
addr_management = Address_Management(max_instructions=10,
                                    min_address=min_address,
                                    max_address=max_address,
                                    num_banks=num_banks,
                                    num_addr=num_addr,
                                    num_instructions=num_instructions)


dt_tab = []
for j in range(4):
    experiment = Experiment(num_banks=num_banks,num_addr=num_addr)
    bank,row = random.choice(addr_management.address2loc.available_rows)
    program, ajoint_program = addr_management.generate_instruction_sequence(bank,row)
    print_dict(ajoint_program)
    experiment.load_instr(core0_inst=program,core1_inst=[])
    output = experiment.simulate(400)
    dt = output['ddr_simpl_vec_core0']
    dt_tab.append(dt)
    print(dt)

print(distance_between_outcome(dt_tab[-1],dt_tab[-2]))
