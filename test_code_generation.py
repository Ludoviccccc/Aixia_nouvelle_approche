from exploration.codegeneration import Address_Management 
from exploration.env.func import Experiment
import random
import numpy as np
from exploration.history import History
from exploration.imgep.OptimizationPolicy import OptimizationPolicykNN

def print_dict(dict_):
    for key in dict_:
        print(key,dict_[key])

def distance_between_outcome(outcome1,outcome2):
    print('distance function')
    tab = (outcome1 != outcome2)*1.0
    print(tab)
    out = np.sum(tab.values)
    return out

cut_program = lambda program,len_: {key:program[key] for j,key in enumerate(program) if j<min(len_,len(program))}



num_addr = 40
num_banks = 4
min_address = 0
max_address = 19
num_instructions = 5
k = 3
policy = OptimizationPolicykNN(k=k,min_address=min_address,max_address = max_address)
addr_management = Address_Management(max_instructions=10,
                                    min_address=min_address,
                                    max_address=max_address,
                                    num_banks=num_banks,
                                    num_addr=num_addr,
                                    num_instructions=num_instructions)

#
#dt_tab = []
#for j in range(2):
#    experiment = Experiment(num_banks=num_banks,num_addr=num_addr)
#    bank,row = random.choice(addr_management.address2loc.available_rows)
#    program, adjoint_program = addr_management.generate_instruction_sequence(bank,row)
#    print_dict(adjoint_program)
#    experiment.load_instr(core0_inst=program,core1_inst=[])
#    output = experiment.simulate(400)
#    dt = output['ddr_simpl_vec_core0']
#    dt_tab.append(dt)
#    print(dt)
#
#print(distance_between_outcome(dt_tab[-1],dt_tab[-2]))



bank,row = random.choice(addr_management.address2loc.available_rows)
print(f'(bank,row) = ({bank},{row}')

history = History(length_ = num_instructions)

for _ in range(5):

    experiment = Experiment(num_banks=num_banks,num_addr=num_addr)
    program, adjoint_program = addr_management.generate_instruction_sequence(bank,row)
    print(adjoint_program)
    #print_dict(adjoint_program)
    experiment.load_instr(core0_inst=program,core1_inst=[])
    output = experiment.simulate(400)
    dt = output['ddr_simpl_vec_core0']
    
    history.store({'program':{'core0':program},
                    'adjoint':{'core0':adjoint_program},
                'event':dt,
                },(bank,row))


#experiment = Experiment(num_banks=num_banks,num_addr=num_addr)
#shorter_program = {key:program[key] for j,key in enumerate(program) if j<len(program)-1}
#shorter_program = cut_program(program,len(program)-1) 
#print_dict(shorter_program)
#experiment.load_instr(core0_inst=shorter_program,core1_inst=[])
#output = experiment.simulate(400)
#dt = output['ddr_simpl_vec_core0']
#print(dt)
#
goal = np.random.randint(1,3,(5,3))
output = policy.select_closest_codes(history,goal,(bank,row))
#policy.
#print(output)
